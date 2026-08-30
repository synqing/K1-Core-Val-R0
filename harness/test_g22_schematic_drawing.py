#!/usr/bin/env python3
"""Fail-closed tests for G2.2 schematic drawing (stacked Type-C / OCS frames)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from check_g22_schematic_drawing import main as cli_main
from g22_schematic_drawing import analyse
from g22_usb_hub import fixture_v3

ROOT = Path(__file__).resolve().parent.parent
POST_HOLD = ROOT / "evidence/VAL-G2-2026-08-28/g22-hold-lane/anchors/post-ilm-saved-source.json"


class SchematicDrawingTests(unittest.TestCase):
    def test_zero_records_fails_closed(self):
        report = analyse("")
        self.assertFalse(report.ok)
        self.assertTrue(report.unresolved)
        self.assertEqual(report.counts["easyeda_records_parsed"], 0)
        self.assertEqual(report.counts["assertions_executed"], 0)

    def test_good_usb_fixture_passes(self):
        report = analyse(fixture_v3())
        self.assertTrue(report.ok, report.errors)
        self.assertEqual(report.counts["type_c_symbols"], 1)
        self.assertEqual(report.stacked_pairs, [])
        self.assertEqual(report.picture_frames, [])
        self.assertGreater(report.counts["easyeda_records_parsed"], 0)
        self.assertGreater(report.counts["line_segments_inspected"], 0)
        self.assertGreater(report.counts["assertions_executed"], 0)

    def test_stacked_type_c_fails(self):
        report = analyse(fixture_v3(retired_j1_xy=(185, -4095)))
        self.assertFalse(report.ok)
        self.assertFalse(report.unresolved)
        self.assertEqual(report.counts["type_c_symbols"], 2)
        self.assertEqual(len(report.stacked_pairs), 1)
        self.assertLess(report.stacked_pairs[0]["distance"], 80)
        joined = " ".join(report.errors)
        self.assertIn("Type-C stack", joined)
        self.assertIn("S-USB-04", joined)

    def test_parked_retired_type_c_passes(self):
        report = analyse(fixture_v3(retired_j1_xy=(2000, -4120)))
        self.assertTrue(report.ok, report.errors)
        self.assertEqual(report.counts["type_c_symbols"], 2)
        self.assertEqual(report.stacked_pairs, [])

    def test_ocs_picture_frame_fails(self):
        report = analyse(fixture_v3(ocs_picture_frame=True))
        self.assertFalse(report.ok)
        self.assertFalse(report.unresolved)
        self.assertGreaterEqual(len(report.picture_frames), 1)
        self.assertGreaterEqual(report.picture_frames[0]["length"], 400)
        joined = " ".join(report.errors)
        self.assertIn("USB_OCS1_N picture-frame", joined)
        self.assertIn("S-USB-14", joined)

    def test_cli_stacked_exit_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stacked.txt"
            path.write_text(fixture_v3(retired_j1_xy=(185, -4095)), encoding="utf-8")
            self.assertEqual(cli_main([str(path)]), 2)

    def test_cli_good_fixture_exit_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "good.txt"
            path.write_text(fixture_v3(), encoding="utf-8")
            self.assertEqual(cli_main([str(path)]), 0)

    def test_epro_drawing_refuses_stacked(self):
        from epro_electrical_oracle import main as oracle_main

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "stacked.txt"
            out = Path(tmp) / "graph.json"
            src.write_text(fixture_v3(retired_j1_xy=(185, -4095)), encoding="utf-8")
            rc = oracle_main(
                [
                    str(src),
                    "-o",
                    str(out),
                    "--role",
                    "G2.1_ELECTRICAL_DIGEST",
                    "--schematic-drawing-semantics",
                ]
            )
            self.assertEqual(rc, 2)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertFalse(payload["schematic_drawing"]["ok"])

    def test_hold_post_ilm_stacked_or_framed(self):
        """Historical HOLD dump must not silently pass the drawing gate."""
        if not POST_HOLD.is_file():
            self.skipTest("HOLD post-ILM source missing")
        from extract_electrical_graph import _load_source

        source, _ = _load_source(POST_HOLD)
        report = analyse(source, source_path=str(POST_HOLD))
        self.assertFalse(report.ok)
        self.assertFalse(report.unresolved)
        self.assertGreater(report.counts["easyeda_records_parsed"], 1000)
        self.assertGreater(report.counts["type_c_symbols"], 1)
        self.assertTrue(report.stacked_pairs or report.picture_frames, report.errors)


if __name__ == "__main__":
    unittest.main()
