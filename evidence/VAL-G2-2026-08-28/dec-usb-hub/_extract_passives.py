#!/usr/bin/env python3
import json
import sys
from collections import defaultdict

snap = json.loads(open(sys.argv[1], encoding="utf-8").read())
src = snap["source"]
records = []
for line in src.splitlines():
    if "||" not in line:
        continue
    head, payload = line.split("||", 1)
    try:
        kind = json.loads(head)
        body = json.loads(payload)
    except json.JSONDecodeError:
        continue
    records.append((kind.get("type"), kind.get("id"), body))

attrs_by_parent = defaultdict(list)
for typ, _id, body in records:
    if typ == "ATTR":
        attrs_by_parent[body.get("parentId")].append(body)

components = []
for typ, cid, body in records:
    if typ != "COMPONENT":
        continue
    attrs = {a.get("key"): a.get("value") for a in attrs_by_parent.get(cid, [])}
    components.append({
        "id": cid,
        "x": body.get("x"),
        "y": body.get("y"),
        "designator": attrs.get("Designator"),
        "name": attrs.get("Name") or body.get("name"),
        "value": attrs.get("Value") or attrs.get("Resistance") or attrs.get("Capacitance"),
        "device": attrs.get("Device"),
        "supplier": attrs.get("Supplier Part") or attrs.get("LCSC Part") or attrs.get("SupplierId"),
        "footprint": attrs.get("Footprint"),
        "lib": body.get("libraryUuid") or attrs.get("Library Uuid"),
        "partId": body.get("partId"),
    })

print("components", len(components))
wanted_des = ("R", "C", "Y")
by_val = {}
for c in components:
    des = c["designator"] or ""
    if not des[:1] in wanted_des:
        continue
    key = (des[:1], c.get("value"), c.get("supplier"), c.get("device"), c.get("footprint"))
    by_val.setdefault(key, c)

for key, c in sorted(by_val.items(), key=lambda kv: (kv[0][0], str(kv[0][1]))):
    print(f"{c['designator']:16} val={c.get('value')} lcsc={c.get('supplier')} device={c.get('device')} fp={c.get('footprint')} partId={c.get('partId')}")
