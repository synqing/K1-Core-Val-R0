#!/usr/bin/env python3
"""Presentation checker must FAIL the stub-label pattern and PASS a routed spine."""
from __future__ import annotations

import unittest

from check_schematic_presentation import analyse

STUBBY = """\
{"type":"COMPONENT","ticket":1,"id":"e1"}||{"partId":"p","x":0,"y":0,"rotation":0}|
{"type":"ATTR","ticket":2,"id":"a1"}||{"parentId":"e1","key":"Designator","value":"R1-PWR1"}|
{"type":"COMPONENT","ticket":3,"id":"e2"}||{"partId":"p","x":4000,"y":0,"rotation":0}|
{"type":"ATTR","ticket":4,"id":"a2"}||{"parentId":"e2","key":"Designator","value":"R2-PWR1"}|
{"type":"WIRE","ticket":5,"id":"w1"}||{"zIndex":1,"locked":false}|
{"type":"LINE","ticket":6,"id":"l1"}||{"startX":0,"startY":0,"endX":20,"endY":0,"lineGroup":"w1"}|
{"type":"ATTR","ticket":7,"id":"n1"}||{"parentId":"w1","key":"NET","value":"5V_SYS"}|
{"type":"WIRE","ticket":8,"id":"w2"}||{"zIndex":1,"locked":false}|
{"type":"LINE","ticket":9,"id":"l2"}||{"startX":4000,"startY":0,"endX":4020,"endY":0,"lineGroup":"w2"}|
{"type":"ATTR","ticket":10,"id":"n2"}||{"parentId":"w2","key":"NET","value":"5V_SYS"}|
{"type":"RECT","ticket":11,"id":"r1"}||{"dotX1":0,"dotY1":0,"dotX2":1000,"dotY2":800,"radiusX":0,"radiusY":0}|
{"type":"RECT","ticket":12,"id":"r2"}||{"dotX1":1000,"dotY1":0,"dotX2":2000,"dotY2":800,"radiusX":0,"radiusY":0}|
{"type":"RECT","ticket":13,"id":"r3"}||{"dotX1":2000,"dotY1":0,"dotX2":3000,"dotY2":800,"radiusX":0,"radiusY":0}|
{"type":"RECT","ticket":14,"id":"r4"}||{"dotX1":3000,"dotY1":0,"dotX2":4000,"dotY2":800,"radiusX":0,"radiusY":0}|
{"type":"RECT","ticket":15,"id":"r5"}||{"dotX1":0,"dotY1":800,"dotX2":1000,"dotY2":1600,"radiusX":0,"radiusY":0}|
{"type":"RECT","ticket":16,"id":"r6"}||{"dotX1":1000,"dotY1":800,"dotX2":2000,"dotY2":1600,"radiusX":0,"radiusY":0}|
{"type":"RECT","ticket":17,"id":"r7"}||{"dotX1":2000,"dotY1":800,"dotX2":3000,"dotY2":1600,"radiusX":0,"radiusY":0}|
{"type":"RECT","ticket":18,"id":"r8"}||{"dotX1":3000,"dotY1":800,"dotX2":4000,"dotY2":1600,"radiusX":0,"radiusY":0}|
{"type":"TEXT","ticket":19,"id":"t1"}||{"x":0,"y":0,"value":"box"}|
"""

ROUTED = """\
{"type":"COMPONENT","ticket":1,"id":"e1"}||{"partId":"p","x":0,"y":0,"rotation":0}|
{"type":"ATTR","ticket":2,"id":"a1"}||{"parentId":"e1","key":"Designator","value":"R1-PWR1"}|
{"type":"COMPONENT","ticket":3,"id":"e2"}||{"partId":"p","x":400,"y":0,"rotation":0}|
{"type":"ATTR","ticket":4,"id":"a2"}||{"parentId":"e2","key":"Designator","value":"R2-PWR1"}|
{"type":"WIRE","ticket":5,"id":"w1"}||{"zIndex":1,"locked":false}|
{"type":"LINE","ticket":6,"id":"l1"}||{"startX":0,"startY":0,"endX":400,"endY":0,"lineGroup":"w1"}|
{"type":"ATTR","ticket":7,"id":"n1"}||{"parentId":"w1","key":"NET","value":"5V_SYS"}|
{"type":"TEXT","ticket":8,"id":"t1"}||{"x":10,"y":-20,"value":"R_A XOR R_B FIT DNP TUNE_TBD"}|
{"type":"TEXT","ticket":9,"id":"t2"}||{"x":10,"y":-40,"value":"OPTION VALIDATION_ONLY"}|
{"type":"TEXT","ticket":10,"id":"t3"}||{"x":10,"y":-60,"value":"FIT path"}|
"""


class PresentationTests(unittest.TestCase):
    def test_stub_sheet_fails(self):
        report = analyse(STUBBY)
        self.assertTrue(report["failures"])
        self.assertTrue(any("stub_label" in f or "power_tree" in f or "prison" in f for f in report["failures"]))

    def test_routed_spine_can_pass(self):
        report = analyse(ROUTED)
        self.assertFalse(report["failures"], report["failures"])


if __name__ == "__main__":
    unittest.main()
