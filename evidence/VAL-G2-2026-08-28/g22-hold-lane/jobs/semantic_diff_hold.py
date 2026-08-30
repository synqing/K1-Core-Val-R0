#!/usr/bin/env python3
"""Structural semantic diff of two HOLD dumps. Forbidden deltas fail closed."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "harness"))
from extract_electrical_graph import _load_source  # noqa: E402
from easyeda_source_format import parse_v3_records  # noqa: E402
from g22_pwr1_ilm import _attrs_by_owner, _components  # noqa: E402


def skip_dochead(source: str) -> str:
    lines = source.splitlines(keepends=True)
    if lines and '"DOCHEAD"' in lines[0]:
        return "".join(lines[1:])
    return source


def fnv1a(text: str) -> str:
    h = 2166136261
    for ch in text:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return f"{len(text)}:{h:08x}"


def net_vertices(recs):
    verts = defaultdict(list)
    for rec in recs:
        if rec.type != "WIRE":
            continue
        net = rec.get("net") or rec.raw.get("NET") if hasattr(rec, "raw") else None
        attrs = {}
        # WIRE net lives on ATTR or on the record
    return verts


def wire_signature(recs, attrs):
    wires = []
    for rec in recs:
        if rec.type != "WIRE":
            continue
        net = attrs.get(rec.id, {}).get("NET") or rec.get("net")
        pts = rec.get("points") or rec.get("line") or rec.get("pointsStr")
        x = rec.get("x")
        y = rec.get("y")
        # V3 wire geometry fields
        line = rec.get("line") if rec.get("line") is not None else rec.fields[4:] if hasattr(rec, "fields") else None
        wires.append((rec.id, net, rec.get("x"), rec.get("y"), tuple(rec.fields[2:8]) if hasattr(rec, "fields") else None))
    return wires


def component_rows(comps):
    rows = {}
    for name, c in comps.items():
        rows[name] = {
            "id": c.get("id"),
            "x": c.get("x"),
            "y": c.get("y"),
            "rotation": c.get("rotation"),
            "isMirror": c.get("isMirror"),
            "partId": c.get("partId"),
            "device": (c.get("attrs") or {}).get("Device"),
            "value": (c.get("attrs") or {}).get("Name") or (c.get("attrs") or {}).get("Value"),
            "mpn": (c.get("attrs") or {}).get("Manufacturer Part"),
        }
    return rows


def named_nets(recs, attrs):
    nets = set()
    for rec in recs:
        if rec.type != "WIRE":
            continue
        net = attrs.get(rec.id, {}).get("NET")
        if net:
            nets.add(net)
    return nets


def nc_state(recs):
    ncs = set()
    for rec in recs:
        if rec.type == "ATTR" and rec.get("key") in {"noConnected", "No Connected"}:
            if str(rec.get("value")).lower() in {"true", "yes", "1"}:
                ncs.add(rec.get("parentId"))
    return ncs


def dnp_state(comps):
    rows = {}
    for name, c in comps.items():
        attrs = c.get("attrs") or {}
        rows[name] = {
            "bom": attrs.get("Add into BOM"),
            "pcb": attrs.get("Convert to PCB"),
        }
    return rows


def main() -> int:
    trusted_p = Path(sys.argv[1])
    live_p = Path(sys.argv[2])
    trusted, tmeta = _load_source(trusted_p)
    live, lmeta = _load_source(live_p)
    t_recs = parse_v3_records(trusted)
    l_recs = parse_v3_records(live)
    t_attrs = _attrs_by_owner(t_recs)
    l_attrs = _attrs_by_owner(l_recs)
    t_comps = _components(t_recs, t_attrs)
    l_comps = _components(l_recs, l_attrs)
    t_rows = component_rows(t_comps)
    l_rows = component_rows(l_comps)
    lost = sorted(set(t_rows) - set(l_rows))
    added = sorted(set(l_rows) - set(t_rows))
    moved = []
    identity = []
    for name in sorted(set(t_rows) & set(l_rows)):
        a, b = t_rows[name], l_rows[name]
        if (a["x"], a["y"], a["rotation"], a["isMirror"]) != (b["x"], b["y"], b["rotation"], b["isMirror"]):
            moved.append({"ref": name, "trusted": a, "live": b})
        if (a["id"], a["partId"], a["device"], a["mpn"]) != (b["id"], b["partId"], b["device"], b["mpn"]):
            identity.append({"ref": name, "trusted": a, "live": b})
    t_nets = named_nets(t_recs, t_attrs)
    l_nets = named_nets(l_recs, l_attrs)
    t_dnp = dnp_state(t_comps)
    l_dnp = dnp_state(l_comps)
    dnp_delta = []
    for name in sorted(set(t_dnp) & set(l_dnp)):
        if t_dnp[name] != l_dnp[name]:
            dnp_delta.append({"ref": name, "trusted": t_dnp[name], "live": l_dnp[name]})
    t_wire_ids = {r.id for r in t_recs if r.type == "WIRE"}
    l_wire_ids = {r.id for r in l_recs if r.type == "WIRE"}
    type_counts = {
        "trusted": {k: sum(1 for r in t_recs if r.type == k) for k in ("COMPONENT", "WIRE", "TEXT", "RECT", "LINE")},
        "live": {k: sum(1 for r in l_recs if r.type == k) for k in ("COMPONENT", "WIRE", "TEXT", "RECT", "LINE")},
    }
    forbidden = []
    if lost:
        forbidden.append(f"designator_loss {lost}")
    if added:
        forbidden.append(f"designator_add {added}")
    if moved:
        forbidden.append(f"component_movement {len(moved)}")
    if identity:
        forbidden.append(f"device_identity {len(identity)}")
    if t_nets - l_nets:
        forbidden.append(f"net_loss {sorted(t_nets - l_nets)[:20]}")
    if l_nets - t_nets:
        forbidden.append(f"net_add {sorted(l_nets - t_nets)[:20]}")
    if t_wire_ids != l_wire_ids:
        forbidden.append(
            f"wire_id_delta lost={len(t_wire_ids-l_wire_ids)} added={len(l_wire_ids-t_wire_ids)}"
        )
    if dnp_delta:
        forbidden.append(f"dnp_fit {dnp_delta[:8]}")
    report = {
        "trusted_hash": fnv1a(trusted),
        "live_hash": fnv1a(live),
        "trusted_normalized": hashlib.sha256(skip_dochead(trusted).encode()).hexdigest(),
        "live_normalized": hashlib.sha256(skip_dochead(live).encode()).hexdigest(),
        "normalized_equal": skip_dochead(trusted) == skip_dochead(live),
        "designated_trusted": len(t_comps),
        "designated_live": len(l_comps),
        "type_counts": type_counts,
        "lost": lost,
        "added": added,
        "moved_count": len(moved),
        "moved_head": moved[:8],
        "identity_count": len(identity),
        "identity_head": identity[:8],
        "nets_lost": sorted(t_nets - l_nets)[:30],
        "nets_added": sorted(l_nets - t_nets)[:30],
        "wire_ids_lost": len(t_wire_ids - l_wire_ids),
        "wire_ids_added": len(l_wire_ids - t_wire_ids),
        "dnp_delta_head": dnp_delta[:8],
        "forbidden": forbidden,
        "ok": not forbidden,
    }
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("semantic-diff.json")
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in (
        "trusted_hash", "live_hash", "normalized_equal", "designated_trusted",
        "designated_live", "moved_count", "identity_count", "wire_ids_lost",
        "wire_ids_added", "ok", "forbidden", "nets_lost", "nets_added", "type_counts",
    )}, indent=2))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
