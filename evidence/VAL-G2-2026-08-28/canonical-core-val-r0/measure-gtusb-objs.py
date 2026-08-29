#!/usr/bin/env python3
"""Measure GT-USB-7005A OBJ envelopes and tab/SMT clusters. Millimetres."""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OBJS = {
    "captain_original": ROOT
    / "evidence/VAL-G2-2026-08-28/dec-usb-hub/3d/J1_GT-USB-7005A.obj",
    "easyeda_zup": ROOT
    / "evidence/VAL-G2-2026-08-28/canonical-core-val-r0/J1_GT-USB-7005A.easyeda-zup.obj",
    "easyeda_zup_yflip": ROOT
    / "evidence/VAL-G2-2026-08-28/canonical-core-val-r0/J1_GT-USB-7005A.easyeda-zup-yflip.obj",
}


def load_verts(path: Path) -> list[tuple[float, float, float]]:
    verts: list[tuple[float, float, float]] = []
    with path.open() as handle:
        for line in handle:
            if not line.startswith("v "):
                continue
            parts = line.split()
            verts.append((float(parts[1]), float(parts[2]), float(parts[3])))
    return verts


def bbox(verts: list[tuple[float, float, float]]) -> dict:
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    zs = [v[2] for v in verts]
    return {
        "n": len(verts),
        "xmin": min(xs),
        "xmax": max(xs),
        "ymin": min(ys),
        "ymax": max(ys),
        "zmin": min(zs),
        "zmax": max(zs),
        "cx": (min(xs) + max(xs)) / 2,
        "cy": (min(ys) + max(ys)) / 2,
        "cz": (min(zs) + max(zs)) / 2,
        "wx": max(xs) - min(xs),
        "wy": max(ys) - min(ys),
        "wz": max(zs) - min(zs),
        "bz": min(zs),
    }


def cluster_xy(points: list[tuple[float, float, float]], pitch: float = 0.35) -> list[dict]:
    buckets: dict[tuple[int, int], list[tuple[float, float, float]]] = defaultdict(list)
    for x, y, z in points:
        buckets[(round(x / pitch), round(y / pitch))].append((x, y, z))
    clusters = []
    for pts in buckets.values():
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        zs = [p[2] for p in pts]
        clusters.append(
            {
                "n": len(pts),
                "x": sum(xs) / len(xs),
                "y": sum(ys) / len(ys),
                "z": sum(zs) / len(zs),
                "zmin": min(zs),
                "zmax": max(zs),
            }
        )
    clusters.sort(key=lambda c: (round(c["y"], 2), c["x"]))
    return clusters


def analyse(verts: list[tuple[float, float, float]]) -> dict:
    box = bbox(verts)
    # SMT tails: near Z=0 solder plane, |X|<3.2, rearward of mouth.
    smt = [
        v
        for v in verts
        if abs(v[2]) < 0.12 and abs(v[0]) < 3.2 and v[1] > box["cy"]
    ]
    # Through-board tab metal: outboard |X|>5, below PCB top.
    tabs = [v for v in verts if abs(v[0]) > 5.2 and v[2] < -0.15]
    # Mouth face: most-negative Y shell vertices.
    mouth_cut = box["ymin"] + 0.35
    mouth = [v for v in verts if v[1] <= mouth_cut]
    return {
        "bbox": box,
        "easyeda_origin": {"cx": box["cx"], "cy": box["cy"], "bz": box["bz"]},
        "smt_z0_clusters": cluster_xy(smt, 0.25)[:16],
        "tab_below_pcb_clusters": cluster_xy(tabs, 0.6),
        "mouth_ymin": box["ymin"],
        "mouth_sample_n": len(mouth),
        "smt_sample_n": len(smt),
        "tab_sample_n": len(tabs),
    }


def after_origin(point: tuple[float, float, float], origin: dict) -> tuple[float, float, float]:
    return (
        point[0] - origin["cx"],
        point[1] - origin["cy"],
        point[2] - origin["bz"],
    )


def main() -> None:
    report: dict = {}
    for name, path in OBJS.items():
        verts = load_verts(path)
        info = analyse(verts)
        origin = info["easyeda_origin"]
        info["smt_after_origin"] = [
            {
                **c,
                "x_o": c["x"] - origin["cx"],
                "y_o": c["y"] - origin["cy"],
                "z_o": c["z"] - origin["bz"],
            }
            for c in info["smt_z0_clusters"]
        ]
        info["tabs_after_origin"] = [
            {
                **c,
                "x_o": c["x"] - origin["cx"],
                "y_o": c["y"] - origin["cy"],
                "z_o": c["z"] - origin["bz"],
            }
            for c in info["tab_below_pcb_clusters"]
        ]
        report[name] = info
        report[name]["path"] = str(path)
        report[name]["exists"] = path.is_file()

    # Compare vertex-wise if counts match.
    orig = load_verts(OBJS["captain_original"])
    for name in ("easyeda_zup", "easyeda_zup_yflip"):
        other = load_verts(OBJS[name])
        if len(orig) != len(other):
            report[name]["vs_original"] = {"n_orig": len(orig), "n_other": len(other)}
            continue
        dx = [other[i][0] - orig[i][0] for i in range(0, len(orig), max(1, len(orig) // 200))]
        dy = [other[i][1] - orig[i][1] for i in range(0, len(orig), max(1, len(orig) // 200))]
        dz = [other[i][2] - orig[i][2] for i in range(0, len(orig), max(1, len(orig) // 200))]
        # Axis remap guess from first 20 verts
        samples = []
        for i in range(0, min(len(orig), 40)):
            samples.append({"o": orig[i], "n": other[i]})
        report[name]["vs_original"] = {
            "same_count": True,
            "mean_d": [sum(dx) / len(dx), sum(dy) / len(dy), sum(dz) / len(dz)],
            "max_abs_d": [
                max(abs(v) for v in dx),
                max(abs(v) for v in dy),
                max(abs(v) for v in dz),
            ],
            "samples": samples[:8],
        }

    out = Path(__file__).with_name("u1-mesh-measure-2026-08-30.json")
    out.write_text(json.dumps(report, indent=2))
    print(json.dumps({k: {
        "bbox": v["bbox"],
        "origin": v["easyeda_origin"],
        "smt_n": v["smt_sample_n"],
        "tab_n": v["tab_sample_n"],
        "tabs_after_origin": v["tabs_after_origin"],
        "smt_after_origin": v["smt_after_origin"][:4],
        "vs_original": v.get("vs_original"),
    } for k, v in report.items()}, indent=2))
    print("wrote", out)


if __name__ == "__main__":
    main()
