#!/usr/bin/env python3
"""Build MCP pin-list jobs for the review sheet's critical designators."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "harness"))
from easyeda_source_format import parse_records_any_format

src = json.loads(Path(sys.argv[1]).read_text())["source"]
out = Path(sys.argv[2])
rows = parse_records_any_format(src, tool="build_pin_jobs")
id_of = {}
for row in rows:
    if row[0] == "ATTR" and len(row) >= 5 and row[3] == "Designator" and row[4]:
        id_of[str(row[4])] = str(row[2])

wanted = [
    "U1-PWR1", "R67-PWR1", "U17-PWR2", "C11-PWR2", "U16-VAL", "U3-PWR2",
    "U2-PWR1", "U12-NFC", "U13-MOT", "C10-PWR2", "R31-AUD", "R32-AUD", "R33-AUD",
    "R8-PWR2", "U4-PWR2", "C68-PWR2", "RILIM-LED", "F1-PWR1",
]
jobs = [{"tool": "get_current_context", "tag": "ctx", "args": {}}]
missing = []
for ref in wanted:
    cid = id_of.get(ref)
    if not cid:
        missing.append(ref)
        continue
    jobs.append({
        "tool": "list_schematic_component_pins",
        "tag": ref,
        "args": {"componentPrimitiveId": cid},
    })
out.write_text(json.dumps(jobs, indent=2) + "\n")
print(json.dumps({"jobs": len(jobs), "missing": missing, "resolved": {r: id_of.get(r) for r in wanted}}, indent=2))
