#!/usr/bin/env python3
"""Fail-closed tests for the G2.2 PWR1 ILM semantic gate."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from check_g22_pwr1_ilm import main as cli_main
from g22_pwr1_ilm import analyse, fixture_v3, parse_ohms, resolve_r1

ROOT = Path(__file__).resolve().parent.parent
REAL_BAD = ROOT / "evidence/VAL-G2-2026-08-28/dec-usb-hub/g22/G2.2-HOLD-REOPEN.source.txt"
POST_HOLD = ROOT / "evidence/VAL-G2-2026-08-28/g22-hold-lane/anchors/post-ilm-saved-source.json"
CANONICAL = ROOT / "evidence/VAL-G2-2026-08-28/canonical-core-val-r0/live-source-2026-08-28-2232.json"


class IlmSemanticTests(unittest.TestCase):
    def test_bad_ilm_on_usb_dp_fails(self):
        report = analyse(fixture_v3(ilm_on_dp=True))
        self.assertFalse(report.ok)
        self.assertFalse(report.unresolved)
        joined = " ".join(report.errors)
        self.assertIn("USB_DP_UP", joined)
        self.assertGreater(report.counts["easyeda_records_parsed"], 0)
        self.assertEqual(report.counts["symbol_pins_resolved"], 10)
        self.assertGreater(report.counts["assertions_executed"], 0)
        self.assertEqual(report.u1_pins["9"].nets, ["USB_DP_UP"])
        self.assertEqual(report.r1["electrical_ohms"], 1240)
        self.assertTrue(report.r1["metadata_mismatch"])
        self.assertNotEqual(report.r1["electrical_ohms"], 10000)

    def test_repaired_ilm_passes(self):
        report = analyse(fixture_v3(ilm_on_dp=False))
        self.assertTrue(report.ok, report.errors)
        self.assertEqual(report.u1_pins["9"].nets, ["USB_EFUSE_ILIM"])
        self.assertIn("U1-PWR1.9", report.ilim_members)
        self.assertTrue(any(m.startswith("R1-PWR1.") for m in report.ilim_members))
        self.assertTrue(report.dp_continuity["rusb_dp_on_usb_dp_up"])
        self.assertTrue(report.dp_continuity["hub_island_usb_dp_up"])
        self.assertFalse(report.dp_continuity["u1_pin9_on_usb_dp_up"])
        self.assertEqual(report.r1["electrical_ohms"], 1240)
        self.assertTrue(report.r1["metadata_mismatch"])

    def test_partid_cannot_report_10k(self):
        report = analyse(fixture_v3(ilm_on_dp=False, r1_partid_10k=True))
        self.assertEqual(report.r1["electrical_ohms"], 1240)
        self.assertEqual(report.r1["partid_implied_ohms"], 10000)
        self.assertTrue(report.r1["metadata_mismatch"])
        self.assertNotEqual(report.r1["electrical_ohms"], report.r1["partid_implied_ohms"])

    def test_zero_records_fails_closed(self):
        report = analyse("")
        self.assertFalse(report.ok)
        self.assertTrue(report.unresolved)
        self.assertEqual(report.counts["easyeda_records_parsed"], 0)

    def test_missing_u1_unresolved(self):
        from g22_pwr1_ilm import fixture_v3 as fx
        text = fx(ilm_on_dp=False).replace("U1-PWR1", "U99-NOPE")
        report = analyse(text)
        self.assertTrue(report.unresolved)
        self.assertFalse(report.ok)

    def test_broken_dplus_fails(self):
        report = analyse(fixture_v3(ilm_on_dp=False, include_dplus=False))
        self.assertFalse(report.ok)
        self.assertTrue(any("U20-USB" in e or "D+" in e or "USB_DP_UP" in e for e in report.errors))

    def test_cli_bad_fixture_exit_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.txt"
            path.write_text(fixture_v3(ilm_on_dp=True), encoding="utf-8")
            self.assertEqual(cli_main([str(path)]), 2)

    def test_cli_good_fixture_exit_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "good.txt"
            path.write_text(fixture_v3(ilm_on_dp=False), encoding="utf-8")
            self.assertEqual(cli_main([str(path)]), 0)

    def test_pin9_defect_fixed_not_same(self):
        from g22_pwr1_ilm import classify_pin, ILIM_NET, DP_NET
        self.assertEqual(
            classify_pin("9", ILIM_NET, DP_NET, ILIM_NET),
            "DEFECT_FIXED",
        )
        self.assertEqual(parse_ohms("1.24k"), 1240)
        self.assertEqual(parse_ohms("1.24 kΩ"), 1240)

    def test_resolve_r1_ignores_partid(self):
        info = resolve_r1(
            {
                "id": "eR1",
                "partId": "RC0402FR-0710KL.1",
                "rotation": 0,
                "x": 0,
                "y": 0,
                "attrs": {
                    "Manufacturer Part": "RNCF0402BTC1K24",
                    "Name": "1.24k",
                    "Value": "",
                    "Device": "263cdab6e3341f4ea8fd57ccc688e923",
                    "Supplier Part": "C2491273",
                },
            }
        )
        self.assertEqual(info["electrical_ohms"], 1240)
        self.assertTrue(info["metadata_mismatch"])

    @unittest.skipUnless(REAL_BAD.is_file(), "G2.2 HOLD-REOPEN dump absent")
    def test_epro_real_g22_pre_fix_refuses_promotion(self):
        from epro_electrical_oracle import main as oracle_main

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "graph.json"
            rc = oracle_main(
                [str(REAL_BAD), "-o", str(out), "--role", "G2.2_READABLE"]
            )
            self.assertEqual(rc, 2)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(payload["ilm_semantics"]["u1_pins"]["9"]["nets"], ["USB_DP_UP"])

    @unittest.skipUnless(REAL_BAD.is_file(), "G2.2 HOLD-REOPEN dump absent")
    def test_real_g22_pre_fix_fails(self):
        report = analyse(REAL_BAD.read_text(encoding="utf-8"), source_path=str(REAL_BAD))
        self.assertFalse(report.ok)
        self.assertFalse(report.unresolved)
        self.assertEqual(report.u1_pins["9"].nets, ["USB_DP_UP"])
        self.assertEqual(report.r1["electrical_ohms"], 1240)
        self.assertNotEqual(report.r1["electrical_ohms"], 10000)

    @unittest.skipUnless(CANONICAL.is_file(), "canonical snapshot absent")
    def test_canonical_ilm_is_correct_value_not_gated(self):
        payload = json.loads(CANONICAL.read_text(encoding="utf-8"))
        source = payload["source"] if isinstance(payload, dict) else payload
        report = analyse(source, source_path=str(CANONICAL), expect_r1_ohms=None)
        self.assertFalse(report.unresolved, report.errors)
        self.assertEqual(report.u1_pins["9"].nets, ["USB_EFUSE_ILIM"])
        self.assertNotIn("USB_DP_UP", report.u1_pins["9"].nets)
        # Canonical Aug-28 snapshot still carries 1.33 kΩ; that is not this defect.
        self.assertNotEqual(report.r1["electrical_ohms"], 10000)

    def test_epro_promotion_refuses_bad_ilm(self):
        from epro_electrical_oracle import main as oracle_main

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "bad.txt"
            out = Path(tmp) / "graph.json"
            src.write_text(fixture_v3(ilm_on_dp=True), encoding="utf-8")
            rc = oracle_main(
                [str(src), "-o", str(out), "--role", "G2.2_READABLE", "--ilm-semantics"]
            )
            self.assertEqual(rc, 2)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertFalse(payload["ilm_semantics"]["ok"])
            self.assertEqual(payload["ilm_semantics"]["u1_pins"]["9"]["nets"], ["USB_DP_UP"])

    def test_epro_promotion_passes_repaired_ilm(self):
        from epro_electrical_oracle import main as oracle_main

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "good.txt"
            out = Path(tmp) / "graph.json"
            src.write_text(fixture_v3(ilm_on_dp=False), encoding="utf-8")
            rc = oracle_main(
                [str(src), "-o", str(out), "--role", "G2.2_READABLE", "--ilm-semantics"]
            )
            self.assertEqual(rc, 0, "repaired fixture must clear the G2.2 promotion ILM gate")
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertTrue(payload["ilm_semantics"]["ok"])
            self.assertEqual(payload["ilm_semantics"]["u1_pins"]["9"]["nets"], ["USB_EFUSE_ILIM"])
            self.assertEqual(payload["ilm_semantics"]["r1"]["electrical_ohms"], 1240)
            self.assertTrue(payload["ilm_semantics"]["r1"]["metadata_mismatch"])

    @unittest.skipUnless(POST_HOLD.is_file(), "G2.2 HOLD post-ILM dump absent")
    def test_live_hold_post_ilm_passes(self):
        from extract_electrical_graph import _load_source

        source, _ = _load_source(POST_HOLD)
        report = analyse(source, source_path=str(POST_HOLD))
        self.assertTrue(report.ok, report.errors)
        self.assertEqual(report.u1_pins["9"].nets, ["USB_EFUSE_ILIM"])
        self.assertNotIn("USB_DP_UP", report.u1_pins["9"].nets)
        self.assertIn("U1-PWR1.9", report.ilim_members)
        self.assertTrue(any(m.startswith("R1-PWR1.") for m in report.ilim_members))
        self.assertFalse(report.dp_continuity["u1_pin9_on_usb_dp_up"])
        self.assertEqual(report.r1["electrical_ohms"], 1240)
        self.assertNotEqual(report.r1["electrical_ohms"], 10000)
        # D-052: this dump is ILM knowledge, not a G2.2 promotion stamp.
        # Oracle G2.2_READABLE still refuses stacked Type-C / picture frames.


if __name__ == "__main__":
    unittest.main()
