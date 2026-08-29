#!/usr/bin/env python3
"""Fail-closed presentation checker for the one-sheet contract.

A page of pin-plus-short-stub-plus-label fragments is not a schematic.
Inspects a real source. Zero records, zero wires, or zero components FAIL.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
from easyeda_source_format import (
    V3_TYPED_RECORD,
    assemble_v3_wire_segments,
    detect_format,
    parse_v3_records,
)
from extract_electrical_graph import _load_source
from schematic_domains import classify_net, domain_for_designator

STUB_MAX = 40.0
NEAR_COMPONENT = 80.0


def _seg_len(seg) -> float:
    x1, y1, x2, y2 = seg[:4]
    return math.hypot(x2 - x1, y2 - y1)


def analyse(source: str) -> dict:
    if detect_format(source) != V3_TYPED_RECORD:
        raise SystemExit("check_schematic_presentation: only V3 sources are accepted")
    records = parse_v3_records(source)
    if not records:
        raise SystemExit("check_schematic_presentation: parsed 0 records; failing closed")

    components = [r for r in records if r.type == "COMPONENT"]
    wires = [r for r in records if r.type == "WIRE"]
    rects = [r for r in records if r.type == "RECT"]
    texts = [r for r in records if r.type == "TEXT"]
    if not components:
        raise SystemExit("check_schematic_presentation: 0 COMPONENT records; failing closed")
    if not wires:
        raise SystemExit("check_schematic_presentation: 0 WIRE records; failing closed")

    attrs = defaultdict(dict)
    for rec in records:
        if rec.type == "ATTR" and rec.get("key"):
            attrs[rec.get("parentId")][rec.get("key")] = rec.get("value")

    designators = {
        rec.id: attrs.get(rec.id, {}).get("Designator")
        for rec in components
        if attrs.get(rec.id, {}).get("Designator")
    }
    segments = assemble_v3_wire_segments(records)
    wire_nets = {}
    for rec in records:
        if rec.type != "ATTR" or rec.get("key") != "NET":
            continue
        parent = rec.get("parentId")
        if parent in segments:
            wire_nets[parent] = str(rec.get("value") or "")

    stub_wires = 0
    routed_wires = 0
    stub_by_net = Counter()
    routed_by_net = Counter()
    for wid, segs in segments.items():
        length = sum(_seg_len(s) for s in segs)
        net = wire_nets.get(wid, "")
        if length <= STUB_MAX:
            stub_wires += 1
            if net:
                stub_by_net[net] += 1
        else:
            routed_wires += 1
            if net:
                routed_by_net[net] += 1

    power_nets = sorted({n for n in wire_nets.values() if classify_net(n) == "power"})
    power_without_spine = [
        n for n in power_nets if routed_by_net[n] == 0 and stub_by_net[n] >= 2
    ]

    equal_boxes = 0
    if len(rects) >= 8:
        sizes = []
        for rec in rects:
            w = rec.get("width") or rec.get("w")
            h = rec.get("height") or rec.get("h")
            if w is None and rec.get("dotX1") is not None:
                w = abs(float(rec.get("dotX2") or 0) - float(rec.get("dotX1") or 0))
                h = abs(float(rec.get("dotY2") or 0) - float(rec.get("dotY1") or 0))
            if w and h:
                sizes.append((round(float(w) / 50) * 50, round(float(h) / 50) * 50))
        counted = Counter(sizes)
        equal_boxes = max(counted.values()) if counted else 0

    state_notes = 0
    for rec in texts:
        value = str(rec.get("value") or "")
        if any(token in value for token in ("FIT", "DNP", "XOR", "TUNE_TBD", "VALIDATION_ONLY", "OPTION")):
            state_notes += 1

    stub_ratio = stub_wires / max(1, stub_wires + routed_wires)
    failures = []
    if stub_ratio >= 0.55:
        failures.append(
            f"stub_label_substitution: {stub_wires} stubs vs {routed_wires} routed "
            f"({stub_ratio:.0%} stubs)"
        )
    if power_without_spine:
        failures.append(
            f"power_tree_is_labels_only: {power_without_spine[:8]}"
        )
    if equal_boxes >= 8:
        failures.append(
            f"equal_cell_prison_boxes: {equal_boxes} similar RECTs (of {len(rects)})"
        )
    if state_notes < 3 and len(designators) >= 20:
        failures.append(f"option_states_not_drawn: only {state_notes} FIT/DNP/XOR/TUNE notes")

    return {
        "records": len(records),
        "components": len(components),
        "designators": len(designators),
        "wires": len(wires),
        "rects": len(rects),
        "stub_wires": stub_wires,
        "routed_wires": routed_wires,
        "stub_ratio": round(stub_ratio, 3),
        "power_without_spine": power_without_spine,
        "equal_similar_rects": equal_boxes,
        "state_notes": state_notes,
        "failures": failures,
        "inspected": True,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args(argv)
    source, _ = _load_source(args.source)
    report = analyse(source)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"PRESENTATION_INSPECTED records={report['records']} "
        f"designators={report['designators']} wires={report['wires']} "
        f"stubs={report['stub_wires']} routed={report['routed_wires']}"
    )
    if report["failures"]:
        print("SCHEMATIC_PRESENTATION=FAIL")
        for item in report["failures"]:
            print(f"  {item}")
        return 2
    print("SCHEMATIC_PRESENTATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
