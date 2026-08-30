#!/usr/bin/env python3
"""G2.2 schematic *drawing* gate — stacked Type-C and OCS/EN picture-frames.

Electrical USB membership is `g22_usb_hub.py`. This module refuses a sheet that
is electrically plausible while two USB-C symbols occupy the same pin field,
or while overcurrent/enable nets are drawn as 1 000-unit picture frames.

Fail-closed: zero records or zero components cannot print PASS.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot
from typing import Any

from easyeda_source_format import parse_v3_records
from extract_electrical_graph import _load_source
from g22_pwr1_ilm import _attrs_by_owner, _components, _wire_geometry
from g22_usb_hub import FORBIDDEN_TYPE_C, J1_DESIGNATOR, RETIRED_J1

TYPE_C_STACK_MAX = 80.0
PICTURE_FRAME_NETS = frozenset({"USB_OCS1_N", "USB_OCS2_N", "USB_EN1", "USB_EN2"})
PICTURE_FRAME_SEG_MAX = 400.0
TYPE_C_HINTS = ("GT-USB", "USB4105", "USB-7005", "USB_C", "USB-C")


@dataclass
class DrawingReport:
    ok: bool = False
    unresolved: bool = False
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    type_c: list[dict[str, Any]] = field(default_factory=list)
    stacked_pairs: list[dict[str, Any]] = field(default_factory=list)
    picture_frames: list[dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "unresolved": self.unresolved,
            "errors": self.errors,
            "warnings": self.warnings,
            "counts": self.counts,
            "type_c": self.type_c,
            "stacked_pairs": self.stacked_pairs,
            "picture_frames": self.picture_frames,
        }


def is_type_c(designator: str, part_id: str) -> bool:
    d = designator or ""
    p = part_id or ""
    if d in {J1_DESIGNATOR, RETIRED_J1, *FORBIDDEN_TYPE_C}:
        return True
    blob = f"{d} {p}".upper()
    return any(hint in blob for hint in TYPE_C_HINTS)


def analyse(source: str, *, source_path: str | None = None) -> DrawingReport:
    report = DrawingReport()
    errors: list[str] = []
    records = parse_v3_records(source) if source.strip() else []
    report.counts = {
        "files_inspected": 1 if source_path else 0,
        "easyeda_records_parsed": len(records),
        "components_inspected": 0,
        "type_c_symbols": 0,
        "nets_inspected": 0,
        "line_segments_inspected": 0,
        "assertions_executed": 0,
    }
    if not records:
        report.unresolved = True
        errors.append("zero EasyEDA records parsed")
        report.errors = errors
        return report

    attrs = _attrs_by_owner(records)
    components = _components(records, attrs)
    report.counts["components_inspected"] = len(components)
    assertions = 0
    assertions += 1
    if not components:
        report.unresolved = True
        errors.append("zero designated components")
        report.counts["assertions_executed"] = assertions
        report.errors = errors
        return report

    type_c: list[dict[str, Any]] = []
    for designator, comp in components.items():
        if not is_type_c(designator, str(comp.get("partId") or "")):
            continue
        type_c.append(
            {
                "designator": designator,
                "id": comp["id"],
                "partId": comp.get("partId"),
                "x": comp["x"],
                "y": comp["y"],
            }
        )
    report.type_c = type_c
    report.counts["type_c_symbols"] = len(type_c)
    assertions += 1

    stacked: list[dict[str, Any]] = []
    for i, a in enumerate(type_c):
        for b in type_c[i + 1 :]:
            dist = hypot(float(a["x"]) - float(b["x"]), float(a["y"]) - float(b["y"]))
            if dist < TYPE_C_STACK_MAX:
                stacked.append(
                    {
                        "a": a["designator"],
                        "b": b["designator"],
                        "distance": round(dist, 3),
                    }
                )
                errors.append(
                    f"Type-C stack {a['designator']}@{a['id']} and "
                    f"{b['designator']}@{b['id']} origins {dist:.1f} units apart "
                    f"(limit {TYPE_C_STACK_MAX:.0f}) — S-USB-04"
                )
    report.stacked_pairs = stacked
    assertions += 1

    net_of_wire, segs = _wire_geometry(records, attrs)
    named_nets = {n for n in net_of_wire.values() if n}
    report.counts["nets_inspected"] = len(named_nets)
    line_count = sum(len(v) for v in segs.values())
    report.counts["line_segments_inspected"] = line_count
    assertions += 1
    if line_count == 0:
        report.unresolved = True
        errors.append("zero LINE segments parsed")
        report.counts["assertions_executed"] = assertions
        report.errors = errors
        return report

    frames: list[dict[str, Any]] = []
    longest: dict[str, float] = {net: 0.0 for net in PICTURE_FRAME_NETS}
    for wire_id, segments in segs.items():
        net = net_of_wire.get(wire_id)
        if net not in PICTURE_FRAME_NETS:
            continue
        for sx, sy, ex, ey in segments:
            length = hypot(ex - sx, ey - sy)
            if length > longest[net]:
                longest[net] = length
            if length >= PICTURE_FRAME_SEG_MAX:
                frames.append(
                    {
                        "net": net,
                        "wire": wire_id,
                        "length": round(length, 1),
                        "seg": [sx, sy, ex, ey],
                    }
                )
                errors.append(
                    f"{net} picture-frame segment {length:.0f} units "
                    f"(limit {PICTURE_FRAME_SEG_MAX:.0f}) on {wire_id} — S-USB-14"
                )
    report.picture_frames = frames
    report.counts["picture_frame_hits"] = len(frames)
    assertions += 1

    report.counts["assertions_executed"] = assertions
    vacuous = [k for k, v in report.counts.items() if v == 0 and k != "files_inspected"]
    # type_c_symbols == 0 is allowed (not every sheet is USB); picture_frame_hits
    # == 0 is the healthy case. Do not treat those as vacuity.
    vacuous = [
        k
        for k in vacuous
        if k not in {"type_c_symbols", "picture_frame_hits", "files_inspected"}
    ]
    if vacuous:
        report.unresolved = True
        errors.append(f"vacuous counts: {report.counts}")
    report.errors = errors
    report.ok = (not errors) and (not report.unresolved)
    return report


def load_and_analyse(path) -> DrawingReport:
    source, _ = _load_source(path)
    return analyse(source, source_path=str(path))
