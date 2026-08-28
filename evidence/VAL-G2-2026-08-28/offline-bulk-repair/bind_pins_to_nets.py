#!/usr/bin/env python3
"""Bind live pin coordinates to named wire stubs from review source."""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "harness"))
from easyeda_source_format import parse_records_any_format

SRC = Path(sys.argv[1])
PINS = Path(sys.argv[2])
OUT = Path(sys.argv[3])
TOL = 8

source = json.loads(SRC.read_text())["source"]
rows = parse_records_any_format(source, tool="bind_pins_to_nets")
wire_segs = {}
wire_net = {}
for row in rows:
    if row[0] == "WIRE" and len(row) > 2 and isinstance(row[2], list):
        wire_segs[row[1]] = row[2]
    elif row[0] == "ATTR" and len(row) >= 5 and row[3] == "NET" and row[4]:
        wire_net[row[2]] = str(row[4])

ends = []
for wid, segs in wire_segs.items():
    net = wire_net.get(wid)
    if not net:
        continue
    for seg in segs:
        if len(seg) >= 4:
            ends.append((int(seg[0]), int(seg[1]), net, wid))
            ends.append((int(seg[2]), int(seg[3]), net, wid))

pin_rows = json.loads(PINS.read_text())
bindings = {}
for rec in pin_rows:
    tag = rec.get("tag")
    if tag == "ctx" or not rec.get("ok"):
        continue
    res = rec.get("result")
    if isinstance(res, str):
        res = json.loads(res)
    for pin in res.get("pins") or []:
        x, y = int(pin["x"]), int(pin["y"])
        hits = []
        for ex, ey, net, wid in ends:
            if abs(ex - x) <= TOL and abs(ey - y) <= TOL:
                hits.append((net, wid, abs(ex - x) + abs(ey - y)))
        hits.sort(key=lambda h: h[2])
        nets = sorted({h[0] for h in hits})
        bindings.setdefault(tag, []).append({
            "pin": str(pin.get("pinNumber")),
            "name": pin.get("pinName"),
            "nc": pin.get("noConnected"),
            "x": x,
            "y": y,
            "nets": nets,
            "net": nets[0] if len(nets) == 1 else (nets or None),
        })

checks = {}

def net_of(ref, pin):
    for p in bindings.get(ref, []):
        if p["pin"] == str(pin):
            return p.get("net"), p.get("nc"), p.get("nets")
    return None, None, []

u1_pg, _, _ = net_of("U1-PWR1", "3")
r67_a, _, _ = net_of("R67-PWR1", "1")
r67_b, _, _ = net_of("R67-PWR1", "2")
checks["U1.3_and_R67_same_PG"] = {
    "U1.3": u1_pg,
    "R67.1": r67_a,
    "R67.2": r67_b,
    "ok": u1_pg == "PWR_ENTRY_PG_RT_IOMUX_TBD" and "PWR_ENTRY_PG_RT_IOMUX_TBD" in {r67_a, r67_b},
}
c11_1, _, _ = net_of("C11-PWR2", "1")
c11_2, _, _ = net_of("C11-PWR2", "2")
checks["C11_on_5V_SYS"] = {"1": c11_1, "2": c11_2, "ok": "5V_SYS" in {c11_1, c11_2}}
u16, nc16, _ = net_of("U16-VAL", "5")
checks["U16.5_SENSE_3V3"] = {"net": u16, "nc": nc16, "ok": u16 == "3V3" and nc16 is False}
u3, nc3, _ = net_of("U3-PWR2", "5")
checks["U3.5_PG_BUCK_PG"] = {"net": u3, "nc": nc3, "ok": u3 == "BUCK_PG" and nc3 is False}
u2a0, nc_a0, _ = net_of("U2-PWR1", "2")  # A0 is pin 2
u2a1, nc_a1, _ = net_of("U2-PWR1", "1")  # A1 is pin 1
checks["U2_A0_A1_strapped"] = {"A0": u2a0, "A1": u2a1, "nc": (nc_a0, nc_a1), "ok": nc_a0 is False and nc_a1 is False and {u2a0, u2a1} <= {"GND", "0", "AGND"}}
c10_1, nc_c101, _ = net_of("C10-PWR2", "1")
c10_2, nc_c102, _ = net_of("C10-PWR2", "2")
checks["C10_soft_start"] = {"1": c10_1, "2": c10_2, "nc": (nc_c101, nc_c102), "ok": nc_c101 is False and nc_c102 is False and None not in {c10_1, c10_2}}
u12_15, nc15, _ = net_of("U12-NFC", "15")
u12_20, nc20, _ = net_of("U12-NFC", "20")
u12_23, nc23, _ = net_of("U12-NFC", "23")
checks["U12_DEC04"] = {"RFO2": (u12_15, nc15), "I2C_EN": (u12_20, nc20), "RFI2": (u12_23, nc23),
                      "ok": nc15 is True and nc23 is True and nc20 is False}
rilim1, _, _ = net_of("RILIM-LED", "1")
rilim2, _, _ = net_of("RILIM-LED", "2")
checks["RILIM"] = {"1": rilim1, "2": rilim2}

OUT.write_text(json.dumps({"tolerance": TOL, "checks": checks, "bindings": bindings}, indent=2) + "\n")
print(json.dumps({"wrote": str(OUT), "checks": {k: v.get("ok", v) for k, v in checks.items()}}, indent=2))
