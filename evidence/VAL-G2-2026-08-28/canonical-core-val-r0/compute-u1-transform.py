#!/usr/bin/env python3
"""Compute U1 3D transform from live pads + Captain original OBJ."""

from __future__ import annotations

import json
from pathlib import Path

MM = 39.37007874015748
CX, CY = 3317.7691, 3459.8224

pads = {
    "A12": (3209.5041, 3357.0624),
    "A1": (3426.0341, 3357.0624),
    "rear_L": (3078.5941, 3430.2924),  # 29
    "rear_R": (3556.9441, 3430.2924),  # 26
    "front_L": (3078.5941, 3581.8724),  # 28
    "front_R": (3556.9441, 3581.8724),  # 27
}


def local_mm(x: float, y: float) -> tuple[float, float]:
    # instance angle 180: local = origin - board
    return ((CX - x) / MM, (CY - y) / MM)


locals_mm = {k: local_mm(*xy) for k, xy in pads.items()}
smt_y = local_mm(3317.7691, 3357.0624)[1]
rear_y = (locals_mm["rear_L"][1] + locals_mm["rear_R"][1]) / 2
front_y = (locals_mm["front_L"][1] + locals_mm["front_R"][1]) / 2
edge_y = (CY - 3661.1083) / MM

# Captain original OBJ is Blender Y-up: (x, z_pcb, -y_mouth)
# EasyEDA ORIGIN: cx=0, cy=-0.06, bz=-5.3
# rotX=+90: (x, y, z) -> (x, -z, y)
cx_m, cy_m, bz_m = 0.0, -0.06, -5.3


def orig_from_readme(x: float, y_mouth: float, z_pcb: float) -> tuple[float, float, float]:
    return (x, z_pcb, -y_mouth)


def after_origin(p: tuple[float, float, float]) -> tuple[float, float, float]:
    return (p[0] - cx_m, p[1] - cy_m, p[2] - bz_m)


def rotx90(p: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = p
    return (x, -z, y)


smt_readme = (0.0, 4.46, 0.0)
smt_after = rotx90(after_origin(orig_from_readme(*smt_readme)))
off_y = smt_y - smt_after[1]
off_z = 0.0 - smt_after[2]

rear_readme = (6.075, 2.65, -0.87)
front_readme = (6.075, -1.20, -0.87)
mouth_readme = (0.0, -5.0, 0.0)

def apply(p_readme):
    x, y, z = rotx90(after_origin(orig_from_readme(*p_readme)))
    return (x, y + off_y, z + off_z)

report = {
    "u1_origin_mil": [CX, CY],
    "u1_angle": 180,
    "live_local_mm": {k: [round(v[0], 4), round(v[1], 4)] for k, v in locals_mm.items()},
    "live_smt_y_mm": round(smt_y, 4),
    "live_rear_tab_y_mm": round(rear_y, 4),
    "live_front_tab_y_mm": round(front_y, 4),
    "live_board_edge_y_mm": round(edge_y, 4),
    "mesh": "evidence/VAL-G2-2026-08-28/dec-usb-hub/3d/J1_GT-USB-7005A.obj",
    "mesh_note": "Captain original is Blender Y-up export. rotX=+90 restores README Z-up, mouth -Y.",
    "original_uuid": "7e3f17b4e5b64384aaa03075cd65e3e3",
    "smt_after_rotx90_mm": [round(v, 4) for v in smt_after],
    "off_y_mm": round(off_y, 4),
    "off_z_mm": round(off_z, 4),
    "off_y_mil": round(off_y * MM, 3),
    "off_z_mil": round(off_z * MM, 3),
    "predicted_smt_mm": [round(v, 4) for v in apply(smt_readme)],
    "predicted_rear_mm": [round(v, 4) for v in apply(rear_readme)],
    "predicted_front_mm": [round(v, 4) for v in apply(front_readme)],
    "predicted_mouth_mm": [round(v, 4) for v in apply(mouth_readme)],
    "resid_rear_y_mm": round(apply(rear_readme)[1] - rear_y, 4),
    "resid_front_y_mm": round(apply(front_readme)[1] - front_y, 4),
    "transform": f"0, 0, 0, 0, 90, 0, 0, {off_y * MM:.3f}, {off_z * MM:.3f}",
    "yflip_rejected_reason": "yflip mouth is +Y; U1 angle 180 maps +Y inland. Identity yflip sits inland of the cut-out.",
}

out = Path(__file__).with_name("u1-measured-transform-2026-08-30.json")
out.write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
