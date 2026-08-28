#!/usr/bin/env python3
"""Extract a frozen, read-only denominator from an on-disk EasyEDA source snapshot.

Purpose: one shared, faithful extraction so parallel read-only auditors never each
re-parse the raw source (seven divergent parsers is seven chances to be wrong in
seven different ways), and never touch the live EasyEDA session.

This tool EXTRACTS. It does not judge. It builds no verdict and prints no PASS.
Connectivity proof, BOM adjudication and pin disposition belong to their own
checkers, which must each be able to go RED on a fault battery.

Fails closed: zero parsed records is never a success (canon K1E-055).
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sys
from collections import Counter, defaultdict

SCHEMA_VERSION = 1


def load_records(snapshot: pathlib.Path) -> tuple[dict, list]:
    payload = json.loads(snapshot.read_text())
    for key in ("source", "source_hash", "project_uuid", "document_uuid"):
        if key not in payload:
            raise SystemExit(f"snapshot missing required key {key!r}: {snapshot}")
    records = []
    for line in payload["source"].split("\n"):
        line = line.strip()
        if not line.startswith("["):
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if not records:
        raise SystemExit(f"parsed zero records from {snapshot} — refusing to emit a denominator")
    return payload, records


def build(payload: dict, records: list) -> dict:
    components: dict[str, dict] = {}
    wires: dict[str, dict] = {}
    for rec in records:
        kind = rec[0]
        if kind == "COMPONENT":
            components[rec[1]] = {
                "primitive_id": rec[1],
                "x": rec[3],
                "y": rec[4],
                "rotation": rec[5],
                "attrs": {},
            }
        elif kind == "WIRE":
            wires[rec[1]] = {"primitive_id": rec[1], "segments": rec[2], "attrs": {}}

    no_connect: list[str] = []
    orphan_attrs = 0
    for rec in records:
        if rec[0] != "ATTR":
            continue
        _, _attr_id, parent, key, value = rec[0], rec[1], rec[2], rec[3], rec[4]
        if parent in components:
            components[parent]["attrs"][key] = value
        elif parent in wires:
            wires[parent]["attrs"][key] = value
        else:
            orphan_attrs += 1
            if key == "NO_CONNECT":
                no_connect.append(parent)

    by_designator: dict[str, dict] = {}
    undesignated: list[str] = []
    for comp in components.values():
        ref = comp["attrs"].get("Designator")
        if not ref:
            undesignated.append(comp["primitive_id"])
            continue
        by_designator.setdefault(ref, []).append(comp)
    duplicates = {ref: len(v) for ref, v in by_designator.items() if len(v) > 1}

    net_wires: dict[str, list[str]] = defaultdict(list)
    unnamed_wires: list[str] = []
    for wire in wires.values():
        net = wire["attrs"].get("NET")
        if net:
            net_wires[net].append(wire["primitive_id"])
        else:
            unnamed_wires.append(wire["primitive_id"])

    # Endpoint occupancy per net: how many distinct wire endpoints carry the name.
    # This is geometry, reported raw. It is NOT a connectivity verdict.
    net_endpoints: dict[str, list[list[int]]] = {}
    for net, ids in net_wires.items():
        pts = []
        for wid in ids:
            for seg in wires[wid]["segments"]:
                pts.append([seg[0], seg[1]])
                pts.append([seg[2], seg[3]])
        net_endpoints[net] = pts

    attr_key_census = Counter()
    for comp in components.values():
        for key in comp["attrs"]:
            attr_key_census[key] += 1

    return {
        "schema_version": SCHEMA_VERSION,
        "source_hash": payload["source_hash"],
        "project_uuid": payload["project_uuid"],
        "document_uuid": payload["document_uuid"],
        "counts": {
            "records": len(records),
            "components": len(components),
            "designators": len(by_designator),
            "undesignated_components": len(undesignated),
            "duplicate_designators": duplicates,
            "wires": len(wires),
            "named_nets": len(net_wires),
            "unnamed_wires": len(unnamed_wires),
            "no_connect_marks": len(no_connect),
            "orphan_attrs": orphan_attrs,
        },
        "attr_key_census": dict(attr_key_census.most_common()),
        "components": {
            ref: {
                "primitive_id": c[0]["primitive_id"],
                "x": c[0]["x"],
                "y": c[0]["y"],
                "rotation": c[0]["rotation"],
                **c[0]["attrs"],
            }
            for ref, c in sorted(by_designator.items())
        },
        "nets": {
            net: {"wire_ids": sorted(ids), "wire_count": len(ids),
                  "endpoint_count": len(net_endpoints[net])}
            for net, ids in sorted(net_wires.items())
        },
        "net_endpoint_geometry": {n: net_endpoints[n] for n in sorted(net_endpoints)},
        "undesignated_component_ids": sorted(undesignated),
        "unnamed_wire_ids": sorted(unnamed_wires),
        "no_connect_parent_ids": sorted(no_connect),
    }


BOM_FIELDS = [
    "Designator", "Name", "Value", "Manufacturer", "Manufacturer Part",
    "supplier", "supplierId", "Supplier Part", "LCSC Part Name",
    "Supplier Footprint", "JLCPCB Part Class", "Device", "Symbol",
    "Description", "Datasheet", "primitive_id",
]


def write_bom_csv(index: dict, out: pathlib.Path) -> int:
    with out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=BOM_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for ref, comp in index["components"].items():
            row = {k: comp.get(k, "") for k in BOM_FIELDS}
            row["Designator"] = ref
            writer.writerow(row)
    return len(index["components"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("snapshot", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args()

    payload, records = load_records(args.snapshot)
    index = build(payload, records)

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "index.json").write_text(json.dumps(index, indent=2, sort_keys=True))
    (args.out / "source.txt").write_text(payload["source"])
    rows = write_bom_csv(index, args.out / "bom_flat.csv")

    c = index["counts"]
    if c["components"] == 0 or c["wires"] == 0 or rows == 0:
        raise SystemExit("EXTRACT=FAIL zero components, wires or BOM rows")

    print(f"EXTRACT=OK source_hash={index['source_hash']}")
    for k, v in c.items():
        print(f"  {k:26} = {v}")
    print(f"  bom_rows                   = {rows}")
    print(f"  out                        = {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
