#!/usr/bin/env python3
"""Extract the G2.2 electrical identity graph from a V3 schematic source.

This is the invariant G2.2 is forbidden to change: designators, Device UUIDs,
symbol / footprint / MPN / supplier identity, BOM and PCB-conversion state,
named nets, NC intent, and any known pin → net membership.

Geometry (X/Y, rotation, wire segments, labels, rectangles) is ignored.

A host document source has no PIN primitives. NC parents look like
``<componentId>-<pinId>`` and are resolved to a designator plus that pin id.
Full pin-number membership is optional and comes from a live pin-binding dump.
Until an official dcd7 export is frozen, coverage of pin numbers is PARTIAL.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
from easyeda_source_format import parse_v3_records

SCHEMA = "k1.electrical-graph.v1"

def _yes_no(value):
    if value is None or value == "":
        return None
    text = str(value).strip().lower()
    if text in {"yes", "true", "1"}:
        return "yes"
    if text in {"no", "false", "0"}:
        return "no"
    return str(value)


def _load_source(path: Path) -> tuple[str, dict]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        payload = json.loads(raw)
        if isinstance(payload, dict) and "source" in payload:
            return payload["source"], payload
        raise SystemExit(f"{path}: JSON has no 'source' field")
    return raw, {}


def _attrs_by_owner(records):
    attrs = defaultdict(dict)
    for rec in records:
        if rec.type != "ATTR":
            continue
        key = rec.get("key")
        if not key:
            continue
        attrs[rec.get("parentId")][key] = rec.get("value")
    return attrs


def _resolve_component(pin_parent: str, component_ids: list[str]):
    if pin_parent in component_ids:
        return pin_parent
    for cid in component_ids:
        if pin_parent.startswith(cid + "-") or pin_parent.startswith(cid + "_"):
            return cid
    return None


def _pin_bindings(path: Path | None) -> dict:
    if path is None:
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for designator, pins in (payload.get("bindings") or {}).items():
        for pin in pins:
            number = str(pin.get("pin") or "")
            if not number:
                continue
            key = f"{designator}.{number}"
            nets = pin.get("nets") or []
            net = pin.get("net")
            if net is None and len(nets) == 1:
                net = nets[0]
            out[key] = {
                "designator": designator,
                "pin": number,
                "name": pin.get("name"),
                "net": net,
                "nets": sorted({n for n in nets if n}),
                "nc": bool(pin.get("nc")),
            }
    return out


def extract_electrical_graph(
    source: str,
    *,
    source_path: str | None = None,
    pin_bindings: dict | None = None,
    role: str = "UNDECLARED",
    official_freeze: bool = False,
) -> dict:
    records = parse_v3_records(source)
    if not records:
        raise SystemExit("extract_electrical_graph: parsed 0 records; failing closed")

    attrs = _attrs_by_owner(records)
    components = [r for r in records if r.type == "COMPONENT"]
    if not components:
        raise SystemExit("extract_electrical_graph: parsed 0 COMPONENT records; failing closed")

    component_ids = [r.id for r in components]
    component_ids_longest = sorted(component_ids, key=len, reverse=True)

    identity = {}
    non_electrical = {}
    for rec in components:
        owner = attrs.get(rec.id, {})
        designator = owner.get("Designator")
        unit = {
            "id": rec.id,
            "part_id": rec.get("partId"),
            "device": owner.get("Device"),
            "unique_id": owner.get("Unique ID"),
            "symbol": owner.get("Symbol"),
            "footprint": owner.get("Supplier Footprint") or owner.get("Footprint"),
            "mpn": owner.get("Manufacturer Part"),
            "supplier_part": owner.get("Supplier Part"),
            "supplier": owner.get("supplier"),
            "supplier_id": owner.get("supplierId"),
            "lcsc_part_name": owner.get("LCSC Part Name"),
            "value": owner.get("Value"),
            "bom": _yes_no(owner.get("Add into BOM")),
            "pcb": _yes_no(owner.get("Convert to PCB")),
        }
        if not designator:
            non_electrical[rec.id] = unit
            continue
        slot = identity.setdefault(
            designator,
            {
                "designator": designator,
                "units": [],
                "part_ids": [],
                "devices": [],
                "unique_ids": [],
                "symbols": [],
                "footprints": [],
                "mpns": [],
                "supplier_parts": [],
                "suppliers": [],
                "supplier_ids": [],
                "bom": [],
                "pcb": [],
            },
        )
        slot["units"].append(unit)
        for field, key in (
            ("part_ids", "part_id"),
            ("devices", "device"),
            ("unique_ids", "unique_id"),
            ("symbols", "symbol"),
            ("footprints", "footprint"),
            ("mpns", "mpn"),
            ("supplier_parts", "supplier_part"),
            ("suppliers", "supplier"),
            ("supplier_ids", "supplier_id"),
            ("bom", "bom"),
            ("pcb", "pcb"),
        ):
            value = unit[key]
            if value not in slot[field]:
                slot[field].append(value)

    if not identity:
        raise SystemExit("extract_electrical_graph: 0 designators; failing closed")

    nets = sorted(
        {
            str(owner["NET"])
            for owner in attrs.values()
            if owner.get("NET")
        }
    )
    if not nets:
        raise SystemExit("extract_electrical_graph: 0 named nets; failing closed")

    nc = []
    for rec in records:
        if rec.type != "ATTR" or rec.get("key") != "NO_CONNECT":
            continue
        if _yes_no(rec.get("value")) != "yes":
            continue
        parent = rec.get("parentId") or ""
        cid = _resolve_component(parent, component_ids_longest)
        designator = attrs.get(cid, {}).get("Designator") if cid else None
        if not designator:
            raise SystemExit(
                f"extract_electrical_graph: NO_CONNECT {rec.id} parent {parent!r} "
                "did not resolve to a designator"
            )
        nc.append({"designator": designator, "pin_id": parent, "attr_id": rec.id})
    nc.sort(key=lambda row: (row["designator"], row["pin_id"]))

    bindings = pin_bindings or {}
    coverage = "PARTIAL_LIVE_BINDINGS" if bindings else "IDENTITY_AND_NC_ONLY"

    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    return {
        "schema": SCHEMA,
        "role": role,
        "official_freeze": official_freeze,
        "source": {
            "path": source_path,
            "sha256": digest,
            "record_count": len(records),
            "component_count": len(components),
            "designator_count": len(identity),
            "named_net_count": len(nets),
            "nc_count": len(nc),
            "bound_pin_count": len(bindings),
        },
        "identity": identity,
        "non_electrical": non_electrical,
        "nets": nets,
        "nc": nc,
        "pin_membership": {
            "coverage": coverage,
            "pins": bindings,
        },
        "counts": {
            "records": len(records),
            "components": len(components),
            "designators": len(identity),
            "non_electrical": len(non_electrical),
            "named_nets": len(nets),
            "nc": len(nc),
            "bound_pins": len(bindings),
        },
    }


def canonical_identity(graph: dict) -> dict:
    """Stable comparable projection: drop unit coordinates and raw id lists order."""
    out = {}
    for designator, row in graph["identity"].items():
        out[designator] = {
            "devices": sorted(x for x in row["devices"] if x),
            "unique_ids": sorted(x for x in row["unique_ids"] if x),
            "symbols": sorted(x for x in row["symbols"] if x),
            "footprints": sorted(x for x in row["footprints"] if x),
            "mpns": sorted(x for x in row["mpns"] if x),
            "supplier_parts": sorted(x for x in row["supplier_parts"] if x),
            "suppliers": sorted(x for x in row["suppliers"] if x),
            "supplier_ids": sorted(x for x in row["supplier_ids"] if x),
            "bom": sorted(x for x in row["bom"] if x is not None),
            "pcb": sorted(x for x in row["pcb"] if x is not None),
            "unit_count": len(row["units"]),
        }
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="V3 source dump JSON or raw .txt")
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--pin-bindings", type=Path)
    parser.add_argument("--role", default="UNDECLARED")
    parser.add_argument("--official-freeze", action="store_true")
    args = parser.parse_args(argv)

    source, _meta = _load_source(args.source)
    graph = extract_electrical_graph(
        source,
        source_path=str(args.source),
        pin_bindings=_pin_bindings(args.pin_bindings),
        role=args.role,
        official_freeze=args.official_freeze,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "ELECTRICAL_GRAPH=OK "
        f"designators={graph['counts']['designators']} "
        f"nets={graph['counts']['named_nets']} "
        f"nc={graph['counts']['nc']} "
        f"bound_pins={graph['counts']['bound_pins']} "
        f"role={graph['role']} "
        f"official_freeze={graph['official_freeze']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
