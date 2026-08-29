#!/usr/bin/env python3
"""Isolate the Hirose CX70M solid bbox and assembly transform."""
from __future__ import annotations

import re
from pathlib import Path

SRC = Path("/Users/spectrasynq/Downloads/User Library-USB_C_Hirose_CX_4800304000_v3.STEP")
text = SRC.read_text(errors="ignore")

# entity map: #id -> (type, body)
ent = {}
for m in re.finditer(r"#(\d+)\s*=\s*([A-Z0-9_]+)\s*\((.*?)\);", text, re.S):
    ent[int(m.group(1))] = (m.group(2), m.group(3))

print("entities", len(ent))
for i, (typ, body) in ent.items():
    if typ in {
        "ITEM_DEFINED_TRANSFORMATION",
        "ADVANCED_BREP_SHAPE_REPRESENTATION",
        "SHAPE_REPRESENTATION",
        "NEXT_ASSEMBLY_USAGE_OCCURRENCE",
        "REPRESENTATION_RELATIONSHIP",
        "REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION",
        "CONTEXT_DEPENDENT_SHAPE_REPRESENTATION",
    } or typ.endswith("REPRESENTATION_RELATIONSHIP"):
        print(f"#{i} {typ} {body[:240].replace(chr(10),' ')}")

# resolve cartesian
pt = {}
for i, (typ, body) in ent.items():
    if typ != "CARTESIAN_POINT":
        continue
    nums = re.findall(r"([-+0-9.Ee]+)", body)
    # first token may be from NONE; take last 3
    if len(nums) >= 3:
        x, y, z = map(float, nums[-3:])
        pt[i] = (x, y, z)

def refs(body: str) -> list[int]:
    return [int(x) for x in re.findall(r"#(\d+)", body)]

# find BREP representation and walk to points
brep_ids = [i for i, (t, _) in ent.items() if t == "ADVANCED_BREP_SHAPE_REPRESENTATION"]
print("brep_ids", brep_ids)

visited = set()
want_pts = set()

def walk(i: int, depth=0):
    if i in visited or i not in ent or depth > 40:
        return
    visited.add(i)
    typ, body = ent[i]
    if typ == "CARTESIAN_POINT":
        want_pts.add(i)
        return
    for r in refs(body):
        walk(r, depth + 1)

for bid in brep_ids:
    walk(bid)

print("brep walk entities", len(visited), "points", len(want_pts))
if want_pts:
    xs, ys, zs = zip(*(pt[i] for i in want_pts if i in pt))
    print("BREP xmin", min(xs), "xmax", max(xs), "dx", max(xs) - min(xs))
    print("BREP ymin", min(ys), "ymax", max(ys), "dy", max(ys) - min(ys))
    print("BREP zmin", min(zs), "zmax", max(zs), "dz", max(zs) - min(zs))
    print("BREP center", (min(xs)+max(xs))/2, (min(ys)+max(ys))/2, (min(zs)+max(zs))/2)

# ITEM_DEFINED_TRANSFORMATION: typically (name, desc, axis1, axis2)
for i, (typ, body) in ent.items():
    if typ != "ITEM_DEFINED_TRANSFORMATION":
        continue
    print("XFORM", i, body)
    for r in refs(body):
        if r in ent:
            print("  ref", r, ent[r][0], ent[r][1][:160].replace("\n", " "))
            if ent[r][0] == "AXIS2_PLACEMENT_3D":
                for rr in refs(ent[r][1]):
                    if rr in pt:
                        print("    pt", rr, pt[rr])
                    elif rr in ent:
                        print("    ", rr, ent[rr][0], ent[rr][1][:120].replace("\n", " "))
