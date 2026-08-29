#!/usr/bin/env python3
"""Independent H0 measurement: STEP + recommended-layout pixels.

Does not copy EasyEDA cache. Does not infer PCB thickness from Sinker 1.9 / CH 0.4.
"""
from __future__ import annotations

import json
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
DS = HERE / "datasheets"
OUT = HERE / "_h0_measure"
OUT.mkdir(exist_ok=True)

STP = DS / "_extract" / "GT-USB-7005A.stp"
LAYOUT = DS / "_extract" / "measured" / "crop_pcb_layout.png"
FULL = DS / "_extract" / "hires" / "gswitch-150-1.png"
LAYOUT_A = DS / "_extract" / "hires" / "layout_a.png"
LAYOUT_NOTES = DS / "_extract" / "gswitch-7005a-notes_left.png"


def parse_step_points(path: Path) -> list[tuple[float, float, float]]:
    text = path.read_text(errors="replace")
    pts = []
    for m in re.finditer(
        r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*([eE0-9.+-]+)\s*,\s*([eE0-9.+-]+)\s*,\s*([eE0-9.+-]+)\s*\)",
        text,
    ):
        pts.append((float(m.group(1)), float(m.group(2)), float(m.group(3))))
    return pts


def cluster_1d(values: list[float], tol: float) -> list[tuple[float, int]]:
    if not values:
        return []
    s = sorted(values)
    groups: list[list[float]] = [[s[0]]]
    for v in s[1:]:
        if abs(v - groups[-1][-1]) <= tol:
            groups[-1].append(v)
        else:
            groups.append([v])
    return [(statistics.mean(g), len(g)) for g in groups]


def step_analysis(pts: list[tuple[float, float, float]]) -> dict:
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    zs = [p[2] for p in pts]
    bbox = {
        "x": [min(xs), max(xs)],
        "y": [min(ys), max(ys)],
        "z": [min(zs), max(zs)],
        "n": len(pts),
    }
    # Rear SMT tails: Z deeply negative (into board from mouth), |X|<=3.2, thin Y cluster
    smt = [p for p in pts if p[2] <= -3.80 and abs(p[0]) <= 3.20]
    smt_y = cluster_1d([p[1] for p in smt], 0.02)
    smt_y.sort(key=lambda t: -t[1])
    smt_y0 = smt_y[0][0] if smt_y else None
    smt_x = cluster_1d([p[0] for p in smt if smt_y0 is not None and abs(p[1] - smt_y0) < 0.03], 0.04)
    smt_x_centres = [c for c, n in smt_x if n >= 4]
    smt_z = [p[2] for p in smt if smt_y0 is not None and abs(p[1] - smt_y0) < 0.03]

    y_min = min(ys)
    sink = (smt_y0 - y_min) if smt_y0 is not None else None

    # TH-like pins: |X| in 0.2..3.2, Y between -0.8 and +1.4, Z mid-body
    th_cand = [
        p
        for p in pts
        if 0.25 <= abs(p[0]) <= 3.10 and -0.90 <= p[1] <= 1.40 and -3.80 <= p[2] <= -1.80
    ]
    th_x = cluster_1d([p[0] for p in th_cand], 0.06)
    th_y = cluster_1d([p[1] for p in th_cand], 0.06)
    th_z = cluster_1d([p[2] for p in th_cand], 0.08)

    # Legs / tabs: |X| > 4.8
    legs = [p for p in pts if abs(p[0]) >= 4.80]
    leg_x = cluster_1d([p[0] for p in legs], 0.08)
    leg_y = cluster_1d([p[1] for p in legs], 0.08)
    leg_z = cluster_1d([p[2] for p in legs], 0.10)
    # lowest Y of whole solid vs SMT plane
    # pin tips below SMT plane
    below_smt = [p for p in pts if smt_y0 is not None and p[1] < smt_y0 - 0.05]
    pin_min_y = min(p[1] for p in below_smt) if below_smt else None
    pin_reach = (smt_y0 - pin_min_y) if (smt_y0 is not None and pin_min_y is not None) else None

    # isolate likely TH pin lowest Y (not shell): |X|<3.2
    th_below = [p for p in below_smt if abs(p[0]) <= 3.20]
    th_min_y = min(p[1] for p in th_below) if th_below else None
    th_reach = (smt_y0 - th_min_y) if (smt_y0 is not None and th_min_y is not None) else None

    # shell lowest is global ymin if |X|<4.6
    shell_low = [p for p in pts if abs(p[0]) <= 4.60]
    shell_ymin = min(p[1] for p in shell_low) if shell_low else None
    shell_ymax = max(p[1] for p in shell_low) if shell_low else None

    return {
        "bbox": bbox,
        "smt_point_count": len(smt),
        "smt_y_clusters": smt_y[:8],
        "smt_solder_y": smt_y0,
        "smt_x_centres": smt_x_centres,
        "smt_z_span": [min(smt_z), max(smt_z)] if smt_z else None,
        "shell_ymin": shell_ymin,
        "shell_ymax": shell_ymax,
        "sink_below_smt_mm": sink,
        "th_candidate_count": len(th_cand),
        "th_x_clusters": th_x,
        "th_y_clusters": th_y[:12],
        "th_z_clusters": th_z[:12],
        "leg_x_clusters": [(c, n) for c, n in leg_x if n >= 20],
        "leg_y_clusters": [(c, n) for c, n in leg_y if n >= 20][:16],
        "leg_z_clusters": [(c, n) for c, n in leg_z if n >= 20][:16],
        "global_ymin": min(ys),
        "global_ymax": max(ys),
        "pin_min_y": pin_min_y,
        "pin_reach_below_smt_mm": pin_reach,
        "th_min_y": th_min_y,
        "th_reach_below_smt_mm": th_reach,
        "on_160_bottom_protrusion_mm": (sink - 1.60) if sink is not None else None,
        "th_emergence_on_160_mm": (th_reach - 1.60) if th_reach is not None else None,
    }


def detect_layout_features(img_path: Path, tag: str) -> dict:
    im = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
    if im is None:
        raise SystemExit(f"cannot read {img_path}")
    h, w = im.shape
    # invert: ink dark
    _, bw = cv2.threshold(im, 200, 255, cv2.THRESH_BINARY_INV)
    # circles
    blur = cv2.GaussianBlur(im, (5, 5), 0)
    circles = cv2.HoughCircles(
        blur,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=8,
        param1=80,
        param2=18,
        minRadius=3,
        maxRadius=28,
    )
    circ = []
    if circles is not None:
        for x, y, r in circles[0]:
            circ.append({"x": float(x), "y": float(y), "r": float(r)})
    circ.sort(key=lambda c: (round(c["y"] / 4), c["x"]))

    # rectangular SMT-like blobs: tall-ish thin
    contours, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = []
    for cnt in contours:
        x, y, rw, rh = cv2.boundingRect(cnt)
        area = cv2.contourArea(cnt)
        if area < 20 or area > 8000:
            continue
        aspect = rh / max(rw, 1)
        if 1.4 <= aspect <= 6.0 and 4 <= rw <= 40 and 10 <= rh <= 90:
            rects.append(
                {
                    "x": x + rw / 2,
                    "y": y + rh / 2,
                    "w": rw,
                    "h": rh,
                    "area": float(area),
                }
            )
    rects.sort(key=lambda r: r["x"])

    vis = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
    for c in circ:
        cv2.circle(vis, (int(c["x"]), int(c["y"])), int(c["r"]), (0, 180, 0), 1)
        cv2.circle(vis, (int(c["x"]), int(c["y"])), 1, (0, 0, 255), 2)
    for r in rects:
        cv2.rectangle(
            vis,
            (int(r["x"] - r["w"] / 2), int(r["y"] - r["h"] / 2)),
            (int(r["x"] + r["w"] / 2), int(r["y"] + r["h"] / 2)),
            (255, 0, 0),
            1,
        )
    cv2.imwrite(str(OUT / f"{tag}_detect.png"), vis)

    return {
        "path": str(img_path),
        "wh": [w, h],
        "n_circles": len(circ),
        "circles": circ,
        "n_rects": len(rects),
        "rects": rects,
    }


def scale_from_a_row(rects: list[dict], expected_span_mm: float = 5.50) -> dict | None:
    if len(rects) < 8:
        return None
    # take the most populated Y band
    ys = [r["y"] for r in rects]
    bands = cluster_1d(ys, 6.0)
    bands.sort(key=lambda t: -t[1])
    y0 = bands[0][0]
    row = [r for r in rects if abs(r["y"] - y0) < 8]
    row.sort(key=lambda r: r["x"])
    if len(row) < 8:
        return None
    span_px = row[-1]["x"] - row[0]["x"]
    px_per_mm = span_px / expected_span_mm
    xs = [r["x"] for r in row]
    pitches = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
    return {
        "n": len(row),
        "y_px": y0,
        "span_px": span_px,
        "px_per_mm": px_per_mm,
        "centres_px": xs,
        "mean_pitch_px": statistics.mean(pitches) if pitches else None,
        "mean_w_px": statistics.mean(r["w"] for r in row),
        "mean_h_px": statistics.mean(r["h"] for r in row),
        "origin_x_px": statistics.mean(xs),  # should be connector CL if 12 pads
    }


def classify_circles(circ: list[dict], origin_x: float, origin_y_a: float, ppm: float) -> dict:
    feats = []
    for c in circ:
        x_mm = (c["x"] - origin_x) / ppm
        y_mm = (origin_y_a - c["y"]) / ppm  # +Y into board if A-row is higher on image? layout is usually A-row toward board interior = up or down
        # In typical recommended-layout drawings, mating edge is at bottom, A-row above B-row.
        # crop_pcb_layout: need to inspect. We'll store both.
        d_mm = 2 * c["r"] / ppm
        feats.append({"x_mm": x_mm, "y_mm_from_a": (c["y"] - origin_y_a) / ppm, "d_mm": d_mm, **c})
    return {"features": feats}


def main() -> None:
    print("=== STEP ===")
    pts = parse_step_points(STP)
    print("cartesian", len(pts))
    sa = step_analysis(pts)
    print(json.dumps({k: sa[k] for k in sa if "cluster" not in k}, indent=2))
    print("smt_x_centres", sa["smt_x_centres"])
    print("th_x", sa["th_x_clusters"])
    print("th_y", sa["th_y_clusters"][:10])
    print("leg_x", sa["leg_x_clusters"])

    print("=== LAYOUT PIXEL DETECT ===")
    reports = {}
    for tag, path in (
        ("crop_pcb", LAYOUT),
        ("layout_a", LAYOUT_A),
        ("notes_left", LAYOUT_NOTES),
    ):
        if not path.exists():
            continue
        det = detect_layout_features(path, tag)
        scale = scale_from_a_row(det["rects"])
        print(tag, "circles", det["n_circles"], "rects", det["n_rects"], "scale", scale)
        reports[tag] = {"detect_summary": {k: det[k] for k in ("path", "wh", "n_circles", "n_rects")}, "scale": scale}
        if scale:
            cls = classify_circles(det["circles"], scale["origin_x_px"], scale["y_px"], scale["px_per_mm"])
            # group circles by Y
            yb = cluster_1d([f["y_mm_from_a"] for f in cls["features"]], 0.12)
            print("  circle Y bands mm from A-row:", yb)
            for f in sorted(cls["features"], key=lambda z: (round(z["y_mm_from_a"], 2), z["x_mm"])):
                if abs(f["x_mm"]) < 8:
                    print(
                        f"    circ x={f['x_mm']:+6.3f} y_fromA={f['y_mm_from_a']:+6.3f} d={f['d_mm']:.3f}"
                    )
            reports[tag]["circles_mm"] = cls["features"]
            reports[tag]["circle_y_bands"] = yb
            reports[tag]["pad_w_mm"] = scale["mean_w_px"] / scale["px_per_mm"]
            reports[tag]["pad_h_mm"] = scale["mean_h_px"] / scale["px_per_mm"]

    out = {"step": sa, "layout": reports}
    (OUT / "MEASURE.json").write_text(json.dumps(out, indent=2, default=float))
    print("wrote", OUT / "MEASURE.json")


if __name__ == "__main__":
    main()
