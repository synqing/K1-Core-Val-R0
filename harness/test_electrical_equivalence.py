#!/usr/bin/env python3
"""Fail-closed tests for the G2.2 electrical-graph invariant."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from check_electrical_equivalence import compare_graphs
from extract_electrical_graph import extract_electrical_graph

SAMPLE = """\
{"type":"COMPONENT","ticket":1,"id":"e1"}||{"partId":"pR","x":10,"y":20,"rotation":0}|
{"type":"ATTR","ticket":2,"id":"a1"}||{"parentId":"e1","key":"Designator","value":"R1"}|
{"type":"ATTR","ticket":3,"id":"a2"}||{"parentId":"e1","key":"Device","value":"dev-r"}|
{"type":"ATTR","ticket":4,"id":"a3"}||{"parentId":"e1","key":"Add into BOM","value":"yes"}|
{"type":"ATTR","ticket":5,"id":"a4"}||{"parentId":"e1","key":"Convert to PCB","value":"yes"}|
{"type":"COMPONENT","ticket":6,"id":"e2"}||{"partId":"pC","x":40,"y":20,"rotation":90}|
{"type":"ATTR","ticket":7,"id":"a5"}||{"parentId":"e2","key":"Designator","value":"C1"}|
{"type":"ATTR","ticket":8,"id":"a6"}||{"parentId":"e2","key":"Device","value":"dev-c"}|
{"type":"WIRE","ticket":9,"id":"w1"}||{"zIndex":1,"locked":false}|
{"type":"ATTR","ticket":10,"id":"a7"}||{"parentId":"w1","key":"NET","value":"VCC"}|
{"type":"ATTR","ticket":11,"id":"a8"}||{"parentId":"e2-pin2","key":"NO_CONNECT","value":"yes"}|
"""


def graph(source=SAMPLE, bindings=None, move=False):
    text = source
    if move:
        text = text.replace('"x":10', '"x":999').replace('"rotation":90', '"rotation":180')
    return extract_electrical_graph(
        text,
        source_path="memory",
        pin_bindings=bindings or {},
        role="TEST",
        official_freeze=False,
    )


class ElectricalGraphTests(unittest.TestCase):
    def test_geometry_change_is_invisible(self):
        errors = compare_graphs(graph(), graph(move=True))
        self.assertEqual(errors, [])

    def test_device_change_fails(self):
        mutated = SAMPLE.replace("dev-r", "dev-OTHER")
        errors = compare_graphs(graph(), graph(mutated))
        self.assertTrue(any("R1.devices" in item for item in errors))

    def test_net_rename_fails(self):
        mutated = SAMPLE.replace("VCC", "VDD")
        errors = compare_graphs(graph(), graph(mutated))
        self.assertTrue(any("named_nets" in item for item in errors))

    def test_nc_loss_fails(self):
        mutated = SAMPLE.replace("e2-pin2", "e2-pin99")
        errors = compare_graphs(graph(), graph(mutated))
        self.assertTrue(any("nc_intent" in item for item in errors))

    def test_pin_net_change_fails(self):
        left = {
            "R1.1": {
                "designator": "R1",
                "pin": "1",
                "net": "VCC",
                "nets": ["VCC"],
                "nc": False,
            }
        }
        right = {
            "R1.1": {
                "designator": "R1",
                "pin": "1",
                "net": "GND",
                "nets": ["GND"],
                "nc": False,
            }
        }
        errors = compare_graphs(graph(bindings=left), graph(bindings=right))
        self.assertTrue(any("R1.1 net" in item for item in errors))

    def test_zero_designators_fails_closed(self):
        empty = '{"type":"WIRE","ticket":1,"id":"w1"}||{"zIndex":1,"locked":false}|\n'
        with self.assertRaises(SystemExit):
            extract_electrical_graph(empty)

    def test_round_trip_file_compare(self):
        from check_electrical_equivalence import main as eq_main
        from extract_electrical_graph import main as ex_main

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            src = tmp / "src.json"
            src.write_text(json.dumps({"source": SAMPLE}), encoding="utf-8")
            a = tmp / "a.json"
            b = tmp / "b.json"
            self.assertEqual(ex_main([str(src), "-o", str(a), "--role", "TEST"]), 0)
            self.assertEqual(ex_main([str(src), "-o", str(b), "--role", "TEST"]), 0)
            self.assertEqual(eq_main([str(a), str(b)]), 0)


if __name__ == "__main__":
    unittest.main()
