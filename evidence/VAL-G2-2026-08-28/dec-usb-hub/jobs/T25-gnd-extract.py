#!/usr/bin/env python3
import json
from pathlib import Path

src = json.loads(Path("evidence/VAL-G2-2026-08-28/dec-usb-hub/anchors/pre-T25.json").read_text())["source"]
recs = []
for chunk in src.split("\n"):
    parts = chunk.split("||")
    if len(parts) < 2:
        continue
    try:
        head = json.loads(parts[0].lstrip("|"))
        body = json.loads(parts[1].rstrip("|"))
        recs.append({**head, **body})
    except Exception:
        continue

gnd_id = "0170749d64f794d2"
lines = [r for r in recs if r.get("lineGroup") == gnd_id or r.get("parentId") == gnd_id]
print("related", len(lines))
print("types", sorted({r.get("type") for r in lines}))
segs = []
for r in lines:
    if r.get("type") == "LINE":
        segs.append([r.get("startX"), r.get("startY"), r.get("endX"), r.get("endY")])
    if r.get("key") == "NET":
        print("NET", r.get("value"), "parent", r.get("parentId"), "x", r.get("x"), "y", r.get("y"))
print("line_segs", len(segs))
# EasyEDA source Y is negated
pos = [[a, -b, c, -d] if a is not None else None for a, b, c, d in segs]
Path("evidence/VAL-G2-2026-08-28/dec-usb-hub/jobs/T25-gnd-segs.json").write_text(
    json.dumps({"id": gnd_id, "count": len(pos), "segs": pos}, indent=2)
)
print("wrote", len(pos), "segs")
