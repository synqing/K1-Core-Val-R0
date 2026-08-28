#!/usr/bin/env python3
"""Tests for the canonical single-sheet read-back checker.

2026-08-28: a staleness gate was added to check_single_schematic.py — the
read-back's sourceHash must match the live mutation gate's current_source_hash,
or the run refuses. That change rippled through this file in two ways, and both
mattered:

  1. `test_current_canonical_readback` asserted the checker PASSES on the
     on-disk read-back. That read-back is two revisions behind the live sheet,
     so the test was asserting green-while-blind. It now asserts the refusal,
     and a separate test covers the content checks with currency satisfied.

  2. Every `run_mutant` test builds a temp read-back and expects CheckError.
     With the gate in front, they all began raising for the WRONG REASON — the
     staleness gate fired before the mutation under test was ever reached, so
     five tests passed while testing nothing. They now supply a matching gate
     state, and assert on the reason, so they exercise what they claim to.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("single_schematic_check", HERE / "check_single_schematic.py")
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)

BASELINE_HASH = "389936:080d43fd"


class SingleSchematicCheckerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline_path = CHECKER.DEFAULT_READBACK
        cls.baseline = json.loads(cls.baseline_path.read_text())

    def _gate_state(self, directory: str, source_hash: str = BASELINE_HASH) -> Path:
        """A gate state that declares `source_hash` current.

        Without this the staleness gate short-circuits every mutant test and they
        pass for the wrong reason.
        """
        path = Path(directory) / "state.json"
        path.write_text(json.dumps({
            "schema_version": 1,
            "state": "READY",
            "project_uuid": "64325d0e55e0435abd018defb0089a9b",
            "document_uuid": "1435cb46f39e48c8a8aadbb84ca81603",
            "current_source_hash": source_hash,
        }))
        return path

    def run_mutant(self, records: list[dict]) -> str:
        """Assert the mutant is rejected, and return WHY — never assume the reason."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutant.json"
            path.write_text(json.dumps(records))
            with self.assertRaises(CHECKER.CheckError) as caught:
                CHECKER.check(path, gate_state=self._gate_state(directory))
            reason = str(caught.exception)
            self.assertNotIn(
                "STALE READ-BACK", reason,
                "the staleness gate fired instead of the mutation under test — "
                "this test would pass for the wrong reason",
            )
            return reason

    # ---- the staleness gate (new) ------------------------------------------

    def test_on_disk_readback_is_refused_against_the_live_gate(self) -> None:
        """The real, current, green-while-blind case: the shipped read-back is stale."""
        with self.assertRaises(CHECKER.CheckError) as caught:
            CHECKER.check(self.baseline_path)
        self.assertIn("STALE READ-BACK", str(caught.exception))

    def test_advanced_gate_hash_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state = self._gate_state(directory, "999999:ffffffff")
            with self.assertRaises(CHECKER.CheckError) as caught:
                CHECKER.check(self.baseline_path, gate_state=state)
            self.assertIn("STALE READ-BACK", str(caught.exception))

    def test_missing_gate_state_is_refused(self) -> None:
        with self.assertRaises(CHECKER.CheckError) as caught:
            CHECKER.check(self.baseline_path, gate_state=Path("/nonexistent/state.json"))
        self.assertIn("cannot prove currency", str(caught.exception))

    # ---- content checks, with currency satisfied ----------------------------

    def test_content_checks_pass_when_readback_is_current(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            summary = CHECKER.check(
                self.baseline_path, BASELINE_HASH, self._gate_state(directory)
            )
        self.assertEqual(summary["unique_designators"], 181)
        self.assertEqual(summary["rectangles"], 10)
        self.assertEqual(summary["currency"]["gate_source_hash"], BASELINE_HASH)

    def test_missing_source_record_fails_closed(self) -> None:
        mutant = [item for item in copy.deepcopy(self.baseline) if item.get("tag") != "source"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutant.json"
            path.write_text(json.dumps(mutant))
            with self.assertRaises(CHECKER.CheckError) as caught:
                CHECKER.check(path, gate_state=self._gate_state(directory))
            # Removing the source record makes currency itself unprovable, which is
            # the correct and stricter rejection.
            self.assertIn("no 'source' record", str(caught.exception))

    def test_second_page_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.baseline)
        objects = next(item for item in mutant if item.get("tag") == "project_objects")["result"]
        page = copy.deepcopy(objects["schematics"][0]["page"][0])
        page["uuid"] = "mutant-second-page"
        objects["schematics"][0]["page"].append(page)
        self.assertIn("exactly one page", self.run_mutant(mutant))

    def test_bad_domain_suffix_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.baseline)
        source = next(item for item in mutant if item.get("tag") == "source")["result"]
        source["source"] = source["source"].replace('"C1-PWR1"', '"C1-BAD"', 1)
        self.assertIn("designator", self.run_mutant(mutant).lower())

    def test_missing_domain_rectangle_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.baseline)
        source = next(item for item in mutant if item.get("tag") == "source")["result"]
        lines = source["source"].splitlines()
        source["source"] = "\n".join(line for line in lines if not line.startswith('["RECT","e62"'))
        self.assertIn("rectangle", self.run_mutant(mutant).lower())

    def test_stale_hash_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(CHECKER.CheckError):
                CHECKER.check(
                    self.baseline_path, "stale:deadbeef", self._gate_state(directory)
                )


if __name__ == "__main__":
    unittest.main()
