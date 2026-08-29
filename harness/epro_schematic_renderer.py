#!/usr/bin/env python3
"""Rebuild schematic presentation from a frozen electrical graph.

Preserves the source serialization generation. Changes only component pose,
wire/junction geometry, labels, notes and domain graphics. Refuses to write a
promotion candidate unless an official freeze digest is supplied.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
from check_electrical_equivalence import compare_graphs
from easyeda_source_format import (
    V3_TYPED_RECORD,
    V3_Y_SIGN,
    assemble_v3_wire_segments,
    detect_format,
    parse_v3_records,
)
from extract_electrical_graph import extract_electrical_graph, _load_source, _pin_bindings
from schematic_domains import classify_net, domain_for_designator
from schematic_floorplan import build_floorplan

NEAR = 90.0


def emit_v3(type_: str, ticket, id_, payload: dict) -> str:
    header = {"type": type_, "ticket": ticket, "id": id_}
    return (
        json.dumps(header, separators=(",", ":"))
        + "||"
        + json.dumps(payload, separators=(",", ":"))
        + "|"
    )


def _component_xy(rec) -> tuple[float, float]:
    return float(rec.get("x")), V3_Y_SIGN * float(rec.get("y"))


def _nearest(px, py, placed_old: dict, limit=NEAR):
    best = None
    best_d = limit
    for cid, (x, y, des) in placed_old.items():
        d = abs(px - x) + abs(py - y)
        if d < best_d:
            best_d = d
            best = (cid, des)
    return best


def members_from_graph(graph: dict) -> dict[str, set[str]]:
    members: dict[str, set[str]] = defaultdict(set)
    pins = (graph.get("pin_membership") or {}).get("pins") or {}
    for row in pins.values():
        if row.get("nc"):
            continue
        des = row.get("designator")
        nets = set(row.get("nets") or [])
        if row.get("net"):
            nets.add(row["net"])
        for net in nets:
            if des and net:
                members[str(net)].add(des)
    return members


def net_members(records, segments, attrs, graph: dict | None = None) -> dict[str, set[str]]:
    members = members_from_graph(graph or {})
    old_xy = {}
    for rec in records:
        if rec.type != "COMPONENT":
            continue
        des = attrs.get(rec.id, {}).get("Designator")
        if not des:
            continue
        old_xy[rec.id] = (*_component_xy(rec), des)
    for rec in records:
        if rec.type != "ATTR" or rec.get("key") != "NET":
            continue
        net = rec.get("value")
        parent = rec.get("parentId")
        if not net or parent not in segments:
            continue
        for x1, y1, x2, y2 in segments[parent]:
            for pt in ((x1, y1), (x2, y2)):
                hit = _nearest(pt[0], pt[1], old_xy)
                if hit:
                    members[str(net)].add(hit[1])
    return dict(members)


def _next_id(counter: list, prefix: str) -> str:
    counter[0] += 1
    return f"{prefix}{counter[0]:06d}"


def _ortho(x1, y1, x2, y2):
    if abs(x1 - x2) < 8:
        return [(x1, y1, x2, y2)]
    if abs(y1 - y2) < 8:
        return [(x1, y1, x2, y2)]
    mid_x = x1
    return [(x1, y1, mid_x, y2), (mid_x, y2, x2, y2)]


def _xy(value) -> int:
    return int(round(float(value)))


def render(source: str, floorplan: dict, *, generation: str, graph: dict | None = None) -> str:
    if generation != V3_TYPED_RECORD:
        raise SystemExit(f"renderer preserves oracle generation; got {generation}")
    records = parse_v3_records(source)
    attrs = defaultdict(dict)
    for rec in records:
        if rec.type == "ATTR" and rec.get("key"):
            attrs[rec.get("parentId")][rec.get("key")] = rec.get("value")
    segments = assemble_v3_wire_segments(records)
    members = net_members(records, segments, attrs, graph)
    placements = floorplan["placements"]
    regions = floorplan["regions"]

    dropped_parents = {rec.id for rec in records if rec.type in {"WIRE", "LINE", "RECT"}}
    keep = []
    max_ticket = 0
    for rec in records:
        max_ticket = max(max_ticket, int(rec.ticket or 0))
        if rec.type in {"WIRE", "LINE", "RECT"}:
            continue
        if rec.type == "ATTR" and rec.get("parentId") in dropped_parents:
            continue
        if rec.type == "TEXT":
            value = str(rec.get("value") or "")
            if value[:2].isdigit() and ". " in value[:6]:
                continue
        keep.append(rec)

    new_lines = []
    for rec in keep:
        if rec.type == "COMPONENT":
            des = attrs.get(rec.id, {}).get("Designator")
            payload = dict(rec.payload)
            if des and des in placements:
                pose = placements[des]
                payload["x"] = pose["x"]
                payload["y"] = V3_Y_SIGN * pose["y"]
                payload["rotation"] = pose.get("rotation", payload.get("rotation", 0))
            new_lines.append(emit_v3(rec.type, rec.ticket, rec.id, payload))
        else:
            new_lines.append(emit_v3(rec.type, rec.ticket, rec.id, dict(rec.payload)))

    counter = [max_ticket]
    # Soft-region graphics
    for name, box in regions.items():
        rid = _next_id(counter, "e2g2r")
        new_lines.append(
            emit_v3(
                "RECT",
                counter[0],
                rid,
                {
                    "dotX1": _xy(box["x"]),
                    "dotY1": V3_Y_SIGN * _xy(box["y"]),
                    "dotX2": _xy(box["x"] + box["w"]),
                    "dotY2": V3_Y_SIGN * _xy(box["y"] + box["h"]),
                    "radiusX": 0,
                    "radiusY": 0,
                    "strokeColor": "#888888",
                    "strokeStyle": 1,
                    "fillColor": "none",
                    "strokeWidth": 1,
                    "fillStyle": 0,
                    "rotation": 0,
                },
            )
        )
        tid = _next_id(counter, "e2g2t")
        new_lines.append(
            emit_v3(
                "TEXT",
                counter[0],
                tid,
                {
                    "x": _xy(box["x"] + 40),
                    "y": V3_Y_SIGN * _xy(box["y"] + 60),
                    "value": name.replace("_", " ").upper(),
                    "rotation": 0,
                },
            )
        )

    # Visible wiring: signal/SI/ownership get orthogonal trunks; power gets a spine
    # per net inside its dominant domain; GND stays labelled stubs.
    for net, designators in sorted(members.items()):
        points = []
        for des in sorted(designators):
            pose = placements.get(des)
            if pose:
                points.append((pose["x"] + 40, pose["y"] + 20, des))
        if len(points) < 2:
            continue
        kind = classify_net(net)
        if kind == "gnd":
            continue
        if kind == "power":
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            trunk_y = sorted(ys)[len(ys) // 2]
            segs = [(min(xs), trunk_y, max(xs), trunk_y)]
            for x, y, _des in points:
                if abs(y - trunk_y) > 4:
                    segs.append((x, y, x, trunk_y))
        else:
            segs = []
            for i in range(len(points) - 1):
                x1, y1, _ = points[i]
                x2, y2, _ = points[i + 1]
                segs.extend(_ortho(x1, y1, x2, y2))
        wid = _next_id(counter, "e2g2w")
        new_lines.append(emit_v3("WIRE", counter[0], wid, {"zIndex": 1, "locked": False}))
        new_lines.append(
            emit_v3("ATTR", counter[0], _next_id(counter, "e2g2a"), {"parentId": wid, "key": "NET", "value": net})
        )
        for x1, y1, x2, y2 in segs:
            lid = _next_id(counter, "e2g2l")
            new_lines.append(
                emit_v3(
                    "LINE",
                    counter[0],
                    lid,
                    {
                        "startX": _xy(x1),
                        "startY": V3_Y_SIGN * _xy(y1),
                        "endX": _xy(x2),
                        "endY": V3_Y_SIGN * _xy(y2),
                        "lineGroup": wid,
                    },
                )
            )

    option_notes = {
        "power_entry": "USB-C inlet → CC / VBUS / ESD · FIT / DNP / TUNE_TBD",
        "usb_hub": "USB2422 US / DN1 RT / DN2 S3 · F6-B / KILL-B",
        "power_reg": "5V_SYS spine → branches · OPTION / TUNE_TBD",
        "audio": "ADC / TDM / PDM XOR options · FIT / DNP / TUNE_TBD",
        "rt1062": "RT1062 ownership · IOMUX_TBD holds stay named",
        "led": "RT → level shift → connector · TUNE_TBD series",
        "debug": "S3 → RT reset / boot / UART / recovery",
        "s3": "K1BR / service USB / radio · VALIDATION_ONLY",
        "nfc": "host → ST25R3916B → matching TUNE_TBD → antenna",
        "motion": "host/ownership beside motion · INT2 NC",
        "validation": "VALIDATION_ONLY instrumentation · DNP allowed",
    }
    for name, box in regions.items():
        tid = _next_id(counter, "e2g2t")
        new_lines.append(
            emit_v3(
                "TEXT",
                counter[0],
                tid,
                {
                    "x": _xy(box["x"] + 40),
                    "y": V3_Y_SIGN * _xy(box["y"] + 140),
                    "value": option_notes.get(name, "OPTION"),
                    "rotation": 0,
                },
            )
        )

    # Preserve every named net even if membership was empty (identity invariant).
    # Use a routed-length labelled spine, not a 3 mm stub.
    existing_nets = {
        rec.get("value")
        for rec in records
        if rec.type == "ATTR" and rec.get("key") == "NET" and rec.get("value")
    }
    written = {
        json.loads(line.split("||", 1)[1].rstrip("|")).get("value")
        for line in new_lines
        if '"NET"' in line
    }
    leftover_y = 80
    for net in sorted(existing_nets - written):
        wid = _next_id(counter, "e2g2w")
        new_lines.append(emit_v3("WIRE", counter[0], wid, {"zIndex": 1, "locked": False}))
        new_lines.append(
            emit_v3("ATTR", counter[0], _next_id(counter, "e2g2a"), {"parentId": wid, "key": "NET", "value": net})
        )
        new_lines.append(
            emit_v3(
                "LINE",
                counter[0],
                _next_id(counter, "e2g2l"),
                {
                    "startX": 40,
                    "startY": V3_Y_SIGN * leftover_y,
                    "endX": 280,
                    "endY": V3_Y_SIGN * leftover_y,
                    "lineGroup": wid,
                },
            )
        )
        leftover_y += 20
    return "\n".join(new_lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--floorplan", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--pin-bindings", type=Path)
    parser.add_argument("--allow-unfrozen", action="store_true")
    args = parser.parse_args(argv)

    source, _meta = _load_source(args.source)
    generation = detect_format(source)
    graph = json.loads(args.graph.read_text(encoding="utf-8"))
    if graph.get("official_freeze") is not True and not args.allow_unfrozen:
        print("RENDER=REFUSED official electrical freeze required (or pass --allow-unfrozen for a fixture)")
        return 2
    if args.floorplan:
        floorplan = json.loads(args.floorplan.read_text(encoding="utf-8"))
    else:
        floorplan = build_floorplan(graph)
    rewritten = render(source, floorplan, generation=generation, graph=graph)
    after = extract_electrical_graph(
        rewritten,
        source_path=str(args.output),
        pin_bindings=_pin_bindings(args.pin_bindings),
        role="G2.2_CANDIDATE",
        official_freeze=False,
    )
    errors = compare_graphs(graph, after)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rewritten, encoding="utf-8")
    after_path = args.output.with_suffix(".graph.json")
    after_path.write_text(json.dumps(after, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if errors:
        print("RENDER=FAIL electrical identity changed")
        for item in errors[:30]:
            print(f"  {item}")
        return 2
    print(
        "RENDER=OK "
        f"generation={generation} "
        f"designators={after['counts']['designators']} "
        f"nets={after['counts']['named_nets']} "
        f"official_freeze={graph.get('official_freeze')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
