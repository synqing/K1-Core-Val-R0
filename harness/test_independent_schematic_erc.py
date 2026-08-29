#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from independent_schematic_erc import (
    HUB_REVIEW_UUID,
    analyse,
    parse_sch_drc_log,
)

SAMPLE = """\
{"type":"COMPONENT","ticket":1,"id":"e1"}||{"partId":"pU","x":10,"y":20,"rotation":0}|
{"type":"ATTR","ticket":2,"id":"a1"}||{"parentId":"e1","key":"Designator","value":"U1-PWR1"}|
{"type":"ATTR","ticket":3,"id":"a2"}||{"parentId":"e1","key":"Device","value":"dev-u1"}|
{"type":"ATTR","ticket":4,"id":"a2n"}||{"parentId":"e1-1","key":"NET","value":"5V_SYS"}|
{"type":"COMPONENT","ticket":5,"id":"e2"}||{"partId":"pU","x":40,"y":20,"rotation":0}|
{"type":"ATTR","ticket":6,"id":"a3"}||{"parentId":"e2","key":"Designator","value":"U17-PWR2"}|
{"type":"ATTR","ticket":7,"id":"a4"}||{"parentId":"e2","key":"Device","value":"dev-u17"}|
"""

LOG = """\
2026-08-29 01:00:00[Info] :  Start Design Rule Checking.
2026-08-29 01:00:00[Warn] :  The wire NFC_VDD_A $1N1 is a single network connected to only one component pin.
2026-08-29 01:00:00[Error] :  Pin U20-USB.3 is floating.
2026-08-29 01:00:00[Info] :  Component $1I72 has empty value of property "Value".
2026-08-29 01:00:00[Info] :  End Design Rule Checking.
"""


def _graph():
    from extract_electrical_graph import extract_electrical_graph

    return extract_electrical_graph(SAMPLE, source_path="memory", role="TEST")


class ErcLogTests(unittest.TestCase):
    def test_parse_skips_start_end(self):
        rows = parse_sch_drc_log(LOG)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[1]["level"], "error")

    def test_oracle_bridge_still_nine_fatals(self):
        report = analyse(SAMPLE, _graph())
        self.assertEqual(report["unclassified_fatals"], 9)
        self.assertEqual(report["gui_panel"], "NOT_CAPTURED_LIVE_WINDOW_IS_CANONICAL")

    def test_gui_log_does_not_inject_bridge(self):
        report = analyse(
            SAMPLE,
            _graph(),
            gui_log=LOG,
            review_project_uuid=HUB_REVIEW_UUID,
        )
        self.assertEqual(report["gui_panel"], "CAPTURED_ITEM_LOG")
        self.assertEqual(report["unclassified_fatals"], 0)
        self.assertEqual(report["real_defects_open"], 1)
        self.assertEqual(report["review_project_uuid"], HUB_REVIEW_UUID)

    def test_overlay_clears_real_defect(self):
        report = analyse(
            SAMPLE,
            _graph(),
            gui_log=LOG,
            overlay=[{"contains": "U20-USB.3 is floating", "class": "named_hold"}],
            review_project_uuid=HUB_REVIEW_UUID,
        )
        self.assertEqual(report["real_defects_open"], 0)
        self.assertEqual(report["unclassified_fatals"], 0)

    def test_cli_gui_log(self):
        from independent_schematic_erc import main

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            src = tmp / "src.json"
            src.write_text(json.dumps({"source": SAMPLE}), encoding="utf-8")
            graph_path = tmp / "g.json"
            graph_path.write_text(json.dumps(_graph()), encoding="utf-8")
            log_path = tmp / "drc.txt"
            log_path.write_text(LOG, encoding="utf-8")
            out = tmp / "erc.json"
            self.assertEqual(
                main(
                    [
                        str(src),
                        "--graph",
                        str(graph_path),
                        "-o",
                        str(out),
                        "--gui-log",
                        str(log_path),
                        "--review-project-uuid",
                        HUB_REVIEW_UUID,
                    ]
                ),
                0,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(payload["gui_panel"], "CAPTURED_ITEM_LOG")


if __name__ == "__main__":
    unittest.main()
