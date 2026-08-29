#!/usr/bin/env python3
"""Summarise live MAIN schematic electrical defects from the 2026-08-30 source dump."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "harness"))
from easyeda_source_format import parse_v3_records

SRC = Path(__file__).with_name("live-source.json")
OUT = Path(__file__).with_name("defect-census.json")


def main() -> None:
    payload = json.loads(SRC.read_text())
    recs = parse_v3_records(payload["source"])
    byid = {r.id: r for r in recs}

    def dump_wire(wid: str) -> dict:
        w = byid.get(wid)
        attrs = []
        for r in recs:
            if r.get("parentId") == wid:
                attrs.append(
                    {
                        "id": r.id,
                        "type": r.type,
                        "key": r.get("key"),
                        "value": r.get("value"),
                        "x": r.get("x"),
                        "y": r.get("y"),
                    }
                )
        return {
            "id": wid,
            "type": None if w is None else w.type,
            "payload": None if w is None else w.payload,
            "attrs": attrs,
        }

    e82471 = dump_wire("e82471")
    led_fault = []
    for r in recs:
        val = str(r.get("value") or "")
        blob = json.dumps(r.payload)
        if "LED_FAULT" in val or "LED_FAULT" in blob:
            led_fault.append(
                {
                    "type": r.type,
                    "id": r.id,
                    "parent": r.get("parentId"),
                    "key": r.get("key"),
                    "value": r.get("value"),
                    "x": r.get("x"),
                    "y": r.get("y"),
                }
            )

    designators = {}
    for r in recs:
        if r.type == "ATTR" and r.get("key") == "Designator" and r.get("value"):
            pid = r.get("parentId")
            c = byid.get(pid)
            designators[str(r.get("value"))] = {
                "id": pid,
                "x": None if c is None else c.get("x"),
                "y": None if c is None else c.get("y"),
                "rotation": None if c is None else c.get("rotation"),
            }

    named = {}
    for needle in (
        "U17-PWR2",
        "U3-PWR2",
        "R75-PWR2",
        "J1-PWR1",
        "D1-PWR1",
        "U6-RTC",
        "J7-ESP",
        "U1-PWR1",
    ):
        named[needle] = designators.get(needle)

    net_labels = defaultdict(list)
    for r in recs:
        if r.type == "ATTR" and r.get("key") == "NET" and r.get("value"):
            net_labels[str(r.get("value"))].append(
                {
                    "id": r.id,
                    "parent": r.get("parentId"),
                    "x": r.get("x"),
                    "y": r.get("y"),
                }
            )

    orphans = {}
    for net in ("5V_LED_COMMON", "LED_EFUSE_DVDT", "LED_EFUSE_ILIM", "BUCK_PG", "LED_FAULT_L_N", "LED_FAULT_R_N"):
        orphans[net] = [dump_wire(x["parent"]) for x in net_labels.get(net, [])]

    # NC flags live as ATTR No-Connect / NC?
    nc_keys = defaultdict(int)
    nc_samples = []
    for r in recs:
        key = r.get("key")
        if key and ("NC" in str(key).upper() or "CONNECT" in str(key).upper() or "NO CONNECT" in str(key).upper()):
            nc_keys[str(key)] += 1
            if len(nc_samples) < 8:
                nc_samples.append({"id": r.id, "key": key, "value": r.get("value"), "parent": r.get("parentId")})

    # empty designators
    empty = []
    for r in recs:
        if r.type == "COMPONENT":
            des = None
            for a in recs:
                if a.get("parentId") == r.id and a.get("key") == "Designator":
                    des = a.get("value")
                    break
            if not des:
                empty.append({"id": r.id, "x": r.get("x"), "y": r.get("y"), "partId": r.get("partId")})

    # wires with negative y (off-sheet)
    neg_y = []
    for r in recs:
        if r.type != "WIRE":
            continue
        pts = r.payload.get("points") or r.payload.get("path") or r.payload.get("lines")
        blob = json.dumps(r.payload)
        if '"y": -' in blob or ",-" in blob:
            # cheap filter then inspect
            ys = []
            if isinstance(pts, list):
                for p in pts:
                    if isinstance(p, dict) and "y" in p:
                        ys.append(p["y"])
                    elif isinstance(p, (list, tuple)) and len(p) >= 2:
                        ys.append(p[1])
            if any((isinstance(y, (int, float)) and y < 0) for y in ys) or "-45" in blob:
                neg_y.append({"id": r.id, "payload": r.payload})

    out = {
        "sourceHash": payload.get("sourceHash"),
        "documentUuid": payload.get("documentUuid"),
        "e82471": e82471,
        "led_fault": led_fault,
        "named_designators": named,
        "orphan_nets": {k: [{"id": w["id"], "payload": w["payload"], "net_attrs": [a for a in w["attrs"] if a["key"] == "NET"]} for w in v] for k, v in orphans.items()},
        "nc_keys": dict(nc_keys),
        "nc_samples": nc_samples,
        "empty_designators": empty,
        "neg_y_wire_count": len(neg_y),
        "neg_y_wires": neg_y[:12],
        "attr_keys_sample": sorted({str(r.get("key")) for r in recs if r.type == "ATTR" and r.get("key")})[:80],
    }
    OUT.write_text(json.dumps(out, indent=2))
    print("wrote", OUT)
    print("sourceHash", payload.get("sourceHash"))
    print("e82471 nets", [a["value"] for a in e82471["attrs"] if a["key"] == "NET"])
    print("LED_FAULT hits", len(led_fault))
    print("U17", named.get("U17-PWR2"))
    print("U3", named.get("U3-PWR2"))
    print("empty_des", empty)
    print("nc_keys", dict(nc_keys))
    print("neg_y", len(neg_y))
    for net in ("BUCK_PG", "LED_FAULT_L_N", "LED_FAULT_R_N", "5V_LED_COMMON"):
        print(net, "wires", len(orphans.get(net) or []))


if __name__ == "__main__":
    main()
