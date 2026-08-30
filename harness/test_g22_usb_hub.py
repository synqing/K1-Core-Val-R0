#!/usr/bin/env python3
"""Fail-closed tests for the G2.2 USB2422 + J1 semantic gate."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from check_g22_usb_hub import main as cli_main
from g22_usb_hub import analyse, fixture_v3

ROOT = Path(__file__).resolve().parent.parent
POST_HOLD = ROOT / "evidence/VAL-G2-2026-08-28/g22-hold-lane/anchors/post-ilm-saved-source.json"


class UsbHubSemanticTests(unittest.TestCase):
    def test_zero_records_fails_closed(self):
        report = analyse("")
        self.assertFalse(report.ok)
        self.assertTrue(report.unresolved)
        self.assertEqual(report.counts["easyeda_records_parsed"], 0)
        self.assertEqual(report.counts["assertions_executed"], 0)

    def test_j1_unwired_fails(self):
        report = analyse(fixture_v3(wire_j1=False))
        self.assertFalse(report.ok)
        self.assertFalse(report.unresolved)
        self.assertGreater(report.counts["easyeda_records_parsed"], 0)
        self.assertEqual(report.counts["connector_pins_resolved"], 28)
        self.assertEqual(report.counts["usb2422_pins_resolved"], 25)
        self.assertGreater(report.counts["assertions_executed"], 0)
        self.assertTrue(any("J1." in e or "GT-USB" in e for e in report.errors))

    def test_r94_same_net_fails(self):
        report = analyse(fixture_v3(r94_same_net=True))
        self.assertFalse(report.ok)
        self.assertTrue(any("R94-USB" in e and "same-net" in e for e in report.errors))

    def test_prtpwr2_gnd_fails(self):
        report = analyse(fixture_v3(prtpwr2_gnd=True))
        self.assertFalse(report.ok)
        self.assertTrue(any("PRTPWR2" in e for e in report.errors))

    def test_dn_shorted_onto_3v3_fails(self):
        report = analyse(fixture_v3(dn_on_3v3=True))
        self.assertFalse(report.ok)
        joined = " ".join(report.errors)
        self.assertIn("shorted onto 3V3", joined)
        self.assertIn("S-USB-06", joined)

    def test_xtalout_on_gnd_fails(self):
        report = analyse(fixture_v3(xtalout_gnd=True))
        self.assertFalse(report.ok)
        joined = " ".join(report.errors)
        self.assertIn("U20.21 XTALOUT on GND", joined)
        self.assertIn("S-USB-08", joined)

    def test_rbias_shares_xtalin_fails(self):
        report = analyse(fixture_v3(rbias_on_xtalin=True))
        self.assertFalse(report.ok)
        joined = " ".join(report.errors)
        self.assertIn("RBIAS shares net", joined)
        self.assertIn("S-USB-07", joined)

    def test_good_fixture_passes(self):
        report = analyse(fixture_v3())
        self.assertTrue(report.ok, report.errors)
        self.assertGreaterEqual(report.paths["j1_functional_wired"], 16)
        self.assertTrue(report.straps["strap_mode"])
        self.assertTrue(report.straps["non_rem_10"])
        self.assertEqual(report.counts["connector_pins_resolved"], 28)
        self.assertEqual(report.counts["usb2422_pins_resolved"], 25)
        self.assertGreater(report.counts["assertions_executed"], 0)
        self.assertNotIn(0, [v for k, v in report.counts.items() if k != "files_inspected"])

    def test_hold_pre_repair_fails_nonvacuous(self):
        if not POST_HOLD.is_file():
            self.skipTest("HOLD post-ILM source missing")
        from extract_electrical_graph import _load_source

        source, _ = _load_source(POST_HOLD)
        report = analyse(source, source_path=str(POST_HOLD))
        self.assertFalse(report.ok)
        self.assertFalse(report.unresolved)
        self.assertGreater(report.counts["easyeda_records_parsed"], 1000)
        self.assertEqual(report.counts["connector_pins_resolved"], 28)
        self.assertEqual(report.counts["usb2422_pins_resolved"], 25)
        self.assertGreater(report.counts["nets_inspected"], 0)
        self.assertGreater(report.counts["assertions_executed"], 0)
        joined = " ".join(report.errors)
        self.assertIn("J1.", joined)
        self.assertIn("R94-USB", joined)

    def test_cli_bad_fixture_exit_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.txt"
            path.write_text(fixture_v3(wire_j1=False), encoding="utf-8")
            self.assertEqual(cli_main([str(path)]), 2)

    def test_cli_good_fixture_exit_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "good.txt"
            path.write_text(fixture_v3(), encoding="utf-8")
            self.assertEqual(cli_main([str(path)]), 0)

    def test_epro_usb_semantics_refuses_hold(self):
        if not POST_HOLD.is_file():
            self.skipTest("HOLD post-ILM source missing")
        from epro_electrical_oracle import main as oracle_main

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "graph.json"
            rc = oracle_main(
                [
                    str(POST_HOLD),
                    "-o",
                    str(out),
                    "--role",
                    "G2.2_READABLE",
                    "--usb-hub-semantics",
                ]
            )
            self.assertEqual(rc, 2)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertFalse(payload["usb_hub_semantics"]["ok"])

    def test_epro_usb_semantics_passes_good_fixture(self):
        from epro_electrical_oracle import main as oracle_main

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "good.txt"
            out = Path(tmp) / "graph.json"
            src.write_text(fixture_v3(), encoding="utf-8")
            rc = oracle_main(
                [
                    str(src),
                    "-o",
                    str(out),
                    "--role",
                    "G2.1_ELECTRICAL_DIGEST",
                    "--usb-hub-semantics",
                ]
            )
            self.assertEqual(rc, 0, "complete USB fixture must clear the hub semantic gate")
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertTrue(payload["usb_hub_semantics"]["ok"])


if __name__ == "__main__":
    unittest.main()
