#!/usr/bin/env python3
"""Parse U1 pads and nearby outline from a PCB snapshot JSON."""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

SNAP = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-yflip-prewrite-snapshot.json"
)
OUT = Path("evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-snapshot-pad-measure.json")

raw = json.loads(SNAP.read_text())
source = raw.get("source") or ""
print("hash", raw.get("source_hash"), "chars", len(source))

# Split EasyEDA V3 records: TYPE||JSON
records = []
for block in source.split("\n"):
    if "||" not in block:
        continue
    head, body = block.split("||", 1)
    try:
        h = json.loads(head)
        b = json.loads(body)
    except json.JSONDecodeError:
        continue
    records.append((h, b))

u1 = None
u1_id = None
for h, b in records:
    if h.get("type") == "COMPONENT" and h.get("id") == "0f194aaf30bc2e32":
        u1 = b
        u1_id = h.get("id")
        break

print("U1", json.dumps({"id": u1_id, **{k: u1.get(k) for k in ("x", "y", "angle", "layerId", "attrs") if u1}}, indent=2)[:800])

cx, cy, ang = u1["x"], u1["y"], u1.get("angle") or 0
rad = math.radians(-ang)
cos, sin = math.cos(rad), math.sin(rad)

pads = []
for h, b in records:
    if h.get("type") != "PAD":
        continue
    x, y = b.get("x"), b.get("y")
    if x is None or y is None:
        continue
    if math.hypot(x - cx, y - cy) > 600:
        continue
    dx, dy = x - cx, y - cy
    pads.append(
        {
            "id": h.get("id"),
            "n": b.get("number") or b.get("padNumber") or b.get("name"),
            "net": b.get("net"),
            "x": x,
            "y": y,
            "localX_mil": dx * cos - dy * sin,
            "localY_mil": dx * sin + dy * cos,
            "hole": b.get("hole"),
            "shape": b.get("shape") or b.get("pad"),
            "layerId": b.get("layerId"),
            "rot": b.get("rotation") or b.get("angle"),
        }
    )

# Also PAD_NET for U1
padnets = []
for h, b in records:
    if h.get("type") == "PAD_NET" and h.get("id") == u1_id:
        padnets.append(b)

# Outline / slot near U1
outlines = []
for h, b in records:
    t = h.get("type")
    if t not in {"LINE", "POLYLINE", "ARC", "REGION", "SLOT", "CUTOUT"}:
        continue
    layer = b.get("layerId")
    # BOARD_OUTLINE = 11
    pts = []
    if "x1" in b:
        pts = [(b.get("x1"), b.get("y1")), (b.get("x2"), b.get("y2"))]
    elif "points" in b:
        pts = b.get("points")
    elif "path" in b:
        pts = b.get("path")
    near = False
    for p in pts or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            if math.hypot(p[0] - cx, p[1] - cy) < 800:
                near = True
        elif isinstance(p, dict) and math.hypot(p.get("x", 0) - cx, p.get("y", 0) - cy) < 800:
            near = True
    if layer == 11 or near:
        outlines.append({"type": t, "id": h.get("id"), "layer": layer, "body_keys": list(b.keys())[:20], "preview": {k: b[k] for k in list(b)[:12]}})

pads.sort(key=lambda p: (round(p["localY_mil"], 1), p["localX_mil"]))
report = {
    "source_hash": raw.get("source_hash"),
    "u1": {"id": u1_id, "x": cx, "y": cy, "angle": ang, "attrs": (u1 or {}).get("attrs")},
    "pad_count": len(pads),
    "pads": pads,
    "padnets": padnets[:40],
    "outline_near": outlines[:30],
    "record_types": {},
}
from collections import Counter
report["record_types"] = dict(Counter(h.get("type") for h, _ in records))
OUT.write_text(json.dumps(report, indent=2))
print("pads", len(pads))
print(json.dumps(pads[:8], indent=2))
print("types", report["record_types"])
print("outlines", len(outlines))
print("wrote", OUT)
