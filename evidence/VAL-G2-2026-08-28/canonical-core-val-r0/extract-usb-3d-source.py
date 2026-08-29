#!/usr/bin/env python3
import json
from pathlib import Path

snap = json.loads(Path("evidence/VAL-G2-2026-08-28/canonical-core-val-r0/usb1-restore-zero-post-snapshot.json").read_text())
src = snap["source"]
print("hash", snap["source_hash"], "len", len(src))
# V3 records are line-oriented type||json
for needle in ["19bbd06e9438ab5d", "001a257400b89df6", "0c8e199e56e60728", "71aa35b92da84360", "0513051d44a0486b", "3D Model"]:
    print("count", needle, src.count(needle))

lines = src.split("\n")
print("lines", len(lines))
keep = []
for i, line in enumerate(lines):
    if any(s in line for s in [
        "19bbd06e9438ab5d", "001a257400b89df6", "0c8e199e56e60728",
        "71aa35b92da84360", "0513051d44a0486b", "USB1", "USB2",
        "3D Model", "FOOTPRINT", "CX70M", "HYCW78",
    ]):
        keep.append((i, line[:500]))
print("matching lines", len(keep))
for i, line in keep[:80]:
    print(f"{i}: {line}")
