#!/usr/bin/env python3
"""Run the three new fault batteries under pytest.

A `--self-test` flag nobody invokes is documentation. These wrappers put the
batteries on the same suite the rest of the harness runs on, and — the part that
matters — each battery is itself asserted to contain cases that go RED. A battery
of all-green expectations cannot detect a harness that is testing nothing
(canon K1E-054).
"""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

CONNECTIVITY = REPO / "harness/check_schematic_connectivity.py"
DRC = REPO / "harness/parse_drc_log.py"
CLOSE_VISUAL = REPO / "schematic/single-sheet-qualification/close_visual_from_census.py"
GATE = REPO / "harness/easyeda_mutation_gate.py"
SINGLE_SCHEMATIC = REPO / "harness/check_single_schematic.py"


def run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(REPO), capture_output=True, text=True, timeout=120,
    )


class SelfTestBatteries(unittest.TestCase):
    def test_connectivity_battery_passes_and_contains_red_cases(self) -> None:
        proc = run(CONNECTIVITY, "--self-test")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("SELF_TEST=OK", proc.stdout)
        self.assertNotIn("red_observed=0", proc.stdout)
        self.assertNotIn("fail_closed_observed=0", proc.stdout)

    def test_drc_battery_passes_and_contains_red_cases(self) -> None:
        proc = run(DRC, "--self-test")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("SELF_TEST=OK", proc.stdout)
        self.assertNotIn("red_observed=0", proc.stdout)
        self.assertNotIn("fail_closed_observed=0", proc.stdout)

    def test_connectivity_battery_keeps_the_fragmentation_control(self) -> None:
        """Fragmentation must stay a statistic. If someone reinstates it as a
        violation, the disjoint-same-name positive control goes red."""
        proc = run(CONNECTIVITY, "--self-test")
        self.assertIn("disjoint-same-name", proc.stdout)
        self.assertIn("expected=GREEN        observed=GREEN", proc.stdout)

    def test_connectivity_battery_has_an_abstention_control(self) -> None:
        proc = run(CONNECTIVITY, "--self-test")
        self.assertIn("unmeasured-part", proc.stdout)
        self.assertIn("ABSTENTION CONTROL", proc.stdout)

    def test_single_schematic_staleness_battery(self) -> None:
        proc = run(SINGLE_SCHEMATIC, "--self-test")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("SELF_TEST=OK", proc.stdout)
        self.assertNotIn("refused_observed=0", proc.stdout)

    def test_single_schematic_refuses_the_stale_on_disk_readback(self) -> None:
        """The live red case: this checker was green while blind before the gate."""
        proc = run(SINGLE_SCHEMATIC)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("STALE READ-BACK", proc.stderr)

    def test_close_visual_refuses_auto_accept(self) -> None:
        proc = run(CLOSE_VISUAL, "--self-test")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("SELF_TEST=OK", proc.stdout)
        self.assertIn("historical auto-accept", proc.stdout)
        self.assertNotIn("refused_observed=0", proc.stdout)


class FailClosedOnNothing(unittest.TestCase):
    """The vacuity guards, exercised directly rather than only via fixtures."""

    def test_connectivity_refuses_without_a_source(self) -> None:
        proc = run(CONNECTIVITY)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("FAIL-CLOSED", proc.stderr)

    def test_connectivity_refuses_a_missing_source(self) -> None:
        proc = run(CONNECTIVITY, "--source", "does/not/exist.txt")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("FAIL-CLOSED", proc.stderr)

    def test_drc_refuses_without_a_log(self) -> None:
        proc = run(DRC)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("FAIL-CLOSED", proc.stderr)

    def test_close_visual_refuses_with_no_arguments(self) -> None:
        proc = run(CLOSE_VISUAL)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("REFUSED", proc.stderr)


class MutationLaneResolution(unittest.TestCase):
    """The gate must name the lane it resolved and never silently pick one."""

    def test_lanes_reports_exactly_one_live_lane(self) -> None:
        proc = run(GATE, "lanes")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("EASYEDA_MUTATION_LIVE_LANES=1", proc.stdout)

    def test_bare_validate_announces_the_lane_it_used(self) -> None:
        proc = run(GATE, "validate")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("EASYEDA_MUTATION_LANE_RESOLVED=", proc.stdout)
        # The canonical lane, not the retired qualification lane.
        self.assertIn("canonical-core-val-r0", proc.stdout)
        self.assertIn("EASYEDA_MUTATION_LANE_PROJECT=64325d0e55e0435abd018defb0089a9b", proc.stdout)

    def test_retired_lane_is_excluded_from_discovery(self) -> None:
        proc = run(GATE, "lanes")
        self.assertIn("[RETIRED] evidence/VAL-G2-2026-08-28", proc.stdout)
        self.assertIn("09e9c541fd3d404082d4b92e55ae5336", proc.stdout)


if __name__ == "__main__":
    unittest.main()
