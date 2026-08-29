#!/usr/bin/env python3
"""Measure Captain GT-USB meshes against live U1 pads. Output one transform."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

MM = 39.37007874015748
CX, CY = 3317.7691, 3459.8224
EDGE_Y = 3661.1083

# Live U1 pads (board mil), from pcb_PrimitivePad.getAll near U1.
PADS = {
    "smt_y": 3357.0624,
    "front_L": (3078.5941, 3581.8724),  # 28
    "front_R": (3556.9441, 3581.8724),  # 27
    "rear_L": (3078.5941, 3430.2924),  # 29
    "rear_R": (3556.9441, 3430.2924),  # 26
}

ROOT = Path(__file__).resolve().parents[3]
YFLIP = ROOT / "evidence/VAL-G2-2026-08-28/canonical-core-val-r0/J1_GT-USB-7005A.easyeda-zup-yflip.obj"
ORIG = ROOT / "evidence/VAL-G2-2026-08-28/dec-usb-hub/3d/J1_GT-USB-7005A.obj"


def load_verts(path: Path) -> list[tuple[float, float, float]]:
    verts = []
    with path.open() as handle:
        for line in handle:
            if line.startswith("v "):
                p = line.split()
                verts.append((float(p[1]), float(p[2]), float(p[3])))
    return verts


def clusters(points: list[tuple[float, float, float]], pitch: float) -> list[dict]:
    buckets: dict[tuple[int, int], list[tuple[float, float, float]]] = defaultdict(list)
    for x, y, z in points:
        buckets[(round(x / pitch), round(y / pitch))].append((x, y, z))
    out = []
    for pts in buckets.values():
        xs, ys, zs = zip(*pts)
        out.append(
            {
                "n": len(pts),
                "x": sum(xs) / len(xs),
                "y": sum(ys) / len(ys),
                "z": sum(zs) / len(zs),
            }
        )
    out.sort(key=lambda c: (c["y"], c["x"]))
    return out


def board_needed_mm() -> dict:
    def to_mm(x: float, y: float) -> tuple[float, float]:
        return ((x - CX) / MM, (y - CY) / MM)

    fl = to_mm(*PADS["front_L"])
    fr = to_mm(*PADS["front_R"])
    rl = to_mm(*PADS["rear_L"])
    rr = to_mm(*PADS["rear_R"])
    return {
        "note": "board millimetres relative to U1 origin; +Y is toward the edge",
        "smt_y": (PADS["smt_y"] - CY) / MM,
        "front_y": (fl[1] + fr[1]) / 2,
        "rear_y": (rl[1] + rr[1]) / 2,
        "tab_x": abs(fl[0]),
        "edge_y": (EDGE_Y - CY) / MM,
        "front_L": fl,
        "front_R": fr,
        "rear_L": rl,
        "rear_R": rr,
    }


def analyse_yflip(verts: list[tuple[float, float, float]]) -> dict:
    # Y-flip remap is already Z-up: X right, +Y mouth, Z height, PCB at Z=0.
    smt = [v for v in verts if abs(v[0]) < 3.2 and v[1] < -3.6 and abs(v[2]) < 0.15]
    tabs = [v for v in verts if abs(v[0]) > 5.6 and v[2] < -0.4]
    mouth = min(v[1] for v in verts), max(v[1] for v in verts)
    return {
        "bbox_y": mouth,
        "smt": clusters(smt, 0.4),
        "tabs": clusters(tabs, 0.8),
        "smt_n": len(smt),
        "tab_n": len(tabs),
    }


def main() -> None:
    need = board_needed_mm()
    yflip = load_verts(YFLIP)
    yinfo = analyse_yflip(yflip)

    smt_y = sum(c["y"] for c in yinfo["smt"]) / len(yinfo["smt"]) if yinfo["smt"] else None
    # Four structural tabs: two Y bands at |x|~6.075
    tab_ys = sorted({round(c["y"], 2) for c in yinfo["tabs"] if abs(abs(c["x"]) - 6.075) < 0.2})
    tab_by_y: dict[float, list[dict]] = defaultdict(list)
    for c in yinfo["tabs"]:
        if abs(abs(c["x"]) - 6.075) < 0.25:
            tab_by_y[round(c["y"], 1)].append(c)

    # Mouth is +Y on this mesh. Front tabs are the more-positive Y pair.
    tab_y_keys = sorted(tab_by_y)
    front_tabs = tab_by_y[tab_y_keys[-1]] if tab_y_keys else []
    rear_tabs = tab_by_y[tab_y_keys[0]] if tab_y_keys else []
    front_y = sum(c["y"] for c in front_tabs) / len(front_tabs) if front_tabs else None
    rear_y = sum(c["y"] for c in rear_tabs) / len(rear_tabs) if rear_tabs else None

    # Hypothesis: EasyEDA 3D uses board axes at the component origin (instance
    # rotation is NOT applied to the mesh). Photo of identity yflip shows mouth
    # toward the edge, which matches mesh +Y == board +Y.
    off_from = {}
    if smt_y is not None:
        off_from["smt"] = need["smt_y"] - smt_y
    if front_y is not None:
        off_from["front"] = need["front_y"] - front_y
    if rear_y is not None:
        off_from["rear"] = need["rear_y"] - rear_y
    offs = [v for v in off_from.values() if v is not None]
    off_y = sum(offs) / len(offs) if offs else 0.0

    transform = f"0, {off_y * MM:.3f}, 0, 0, 0, 0, 0, 0, 0"
    transform_neg = f"0, {-off_y * MM:.3f}, 0, 0, 0, 0, 0, 0, 0"

    report = {
        "u1_origin_mil": [CX, CY],
        "u1_angle": 180,
        "needed_board_mm": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in need.items()},
        "yflip_path": str(YFLIP),
        "yflip_features_mm": {
            "mouth_ymin_ymax": yinfo["bbox_y"],
            "smt_y": None if smt_y is None else round(smt_y, 4),
            "front_tab_y": None if front_y is None else round(front_y, 4),
            "rear_tab_y": None if rear_y is None else round(rear_y, 4),
            "tab_y_keys": tab_y_keys,
            "smt_clusters": yinfo["smt"][:8],
            "tab_clusters": yinfo["tabs"],
        },
        "offset_components_mm": {k: round(v, 4) for k, v in off_from.items()},
        "off_y_mm": round(off_y, 4),
        "off_y_mil": round(off_y * MM, 3),
        "hypothesis": (
            "3D mesh is in board axes at U1 origin. yflip mouth +Y faces the edge. "
            "Identity bind sits ~1.8 mm inland. Positive offY (mil) moves toward the edge."
        ),
        "transform_first": transform,
        "transform_reversed_if_wrong_way": transform_neg,
        "keep_model": "e6946995a72f4deaa7b036359e4ff6e7",
        "do_not_rebind_original": (
            "Captain original is Blender Y-up; identity stands vertical. "
            "yflip is that mesh remapped (x, +z, y). Offset it."
        ),
        "predicted_after_mm": {
            "smt_y": None if smt_y is None else round(smt_y + off_y, 4),
            "front_y": None if front_y is None else round(front_y + off_y, 4),
            "rear_y": None if rear_y is None else round(rear_y + off_y, 4),
            "mouth_max": round(yinfo["bbox_y"][1] + off_y, 4),
            "need_smt": round(need["smt_y"], 4),
            "need_front": round(need["front_y"], 4),
            "need_rear": round(need["rear_y"], 4),
            "need_edge": round(need["edge_y"], 4),
        },
    }
    out = Path(__file__).with_name("u1-seat-offset-2026-08-30.json")
    out.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
