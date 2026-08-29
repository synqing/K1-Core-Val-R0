#!/usr/bin/env python3
"""Precise A-row / B-row / tab measurement from layout_a + STEP pin XY."""
from __future__ import annotations

import json
import re
import statistics
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "_h0_measure"
IMG = HERE / "datasheets/_extract/hires/layout_a.png"
CROP = HERE / "datasheets/_extract/measured/crop_pcb_layout.png"
STP = HERE / "datasheets/_extract/GT-USB-7005A.stp"


def step_pts():
    text = STP.read_text(errors="replace")
    return [
        (float(a), float(b), float(c))
        for a, b, c in re.findall(
            r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*([eE0-9.+-]+)\s*,\s*([eE0-9.+-]+)\s*,\s*([eE0-9.+-]+)\s*\)",
            text,
        )
    ]


def cl1(vals, tol):
    s = sorted(vals)
    g = [[s[0]]]
    for v in s[1:]:
        if abs(v - g[-1][-1]) <= tol:
            g[-1].append(v)
        else:
            g.append([v])
    return [(statistics.mean(x), len(x), min(x), max(x)) for x in g]


def main():
    P = step_pts()
    # SMT solder face: Y==0.400 exactly, Z<=-4.20, |X|<=3.0
    smt = [p for p in P if abs(p[1] - 0.400) < 0.002 and p[2] <= -4.20 and abs(p[0]) <= 3.05]
    print("smt_y400", len(smt), "Z", min(p[2] for p in smt), max(p[2] for p in smt))
    smt_z_solder = min(p[2] for p in smt)  # most into-board
    smt_z_mean = statistics.mean(p[2] for p in smt)
    print("smt_z_solder", smt_z_solder, "mean", smt_z_mean)

    # TH pin solids: two Z bands around -2.3..-3.5, |X| 0.2..3.1
    th = [p for p in P if 0.20 <= abs(p[0]) <= 3.10 and -3.60 <= p[2] <= -2.05]
    print("th", len(th))
    print("th X", [(round(c, 3), n) for c, n, *_ in cl1([p[0] for p in th], 0.04) if n >= 20])
    print("th Z", [(round(c, 3), n) for c, n, *_ in cl1([p[2] for p in th], 0.06) if n >= 15])
    print("th Y", [(round(c, 3), n) for c, n, *_ in cl1([p[1] for p in th], 0.04) if n >= 10])

    # footprint Y: A-row at 0, +Y into board = more negative STEP Z
    # Y_fp = -(Z - smt_z_solder)  would put solder tips at 0; lands extend further into board
    # Better: Y_fp = Z_smt_land_centre - Z
    # land centre from recommended layout is independent; pin XY for B holes:

    # group TH by X magnitude and Z
    for z0, z1, name in ((-2.80, -2.05, "front_mouth"), (-3.60, -2.85, "rear_smt")):
        band = [p for p in th if z0 <= p[2] <= z1]
        xs = [(round(c, 3), n) for c, n, *_ in cl1([p[0] for p in band], 0.05) if n >= 8]
        zs = cl1([p[2] for p in band], 0.04)
        print(name, "n", len(band), "X", xs, "Zmean", statistics.mean(p[2] for p in band) if band else None)

    # legs
    legs = [p for p in P if abs(p[0]) >= 5.70]
    print("legs Z", [(round(c, 3), n) for c, n, *_ in cl1([p[2] for p in legs], 0.08) if n >= 8])
    print("legs Y", [(round(c, 3), n) for c, n, *_ in cl1([p[1] for p in legs], 0.06)])

    # --- image: find 12 pads by 0.50 mm regular lattice ---
    im = cv2.imread(str(IMG), cv2.IMREAD_GRAYSCALE)
    H, W = im.shape
    # OCR said A1 ~ (0.451, 0.725) Vision BL; A12 (0.580, 0.715)
    a1 = (int(0.451 * W), int((1 - 0.725) * H))
    a12 = (int(0.580 * W), int((1 - 0.715) * H))
    print("A1px", a1, "A12px", a12, "span", a12[0] - a1[0])
    ppm = (a12[0] - a1[0]) / 5.50
    print("ppm from OCR A1-A12", ppm)
    ox = (a1[0] + a12[0]) / 2
    oy = (a1[1] + a12[1]) / 2

    # crop A-row band and find dark rectangles
    y0, y1 = max(0, int(oy - 40)), min(H, int(oy + 40))
    x0, x1 = max(0, int(ox - 220)), min(W, int(ox + 220))
    band = im[y0:y1, x0:x1]
    cv2.imwrite(str(OUT / "arow_band.png"), band)
    _, bw = cv2.threshold(band, 90, 255, cv2.THRESH_BINARY_INV)
    n, lab, stats, cent = cv2.connectedComponentsWithStats(bw, 8)
    pads = []
    for i in range(1, n):
        x, y, ww, hh, area = stats[i]
        if 6 <= ww <= 30 and 20 <= hh <= 80 and area > 40:
            pads.append((cent[i][0] + x0, cent[i][1] + y0, ww, hh))
    pads.sort(key=lambda t: t[0])
    print("A-band pads", len(pads))
    for p in pads:
        print(f"  {(p[0]-ox)/ppm:+7.3f}  {(oy-p[1])/ppm:+6.3f}  {p[2]/ppm:.3f}x{p[3]/ppm:.3f}")

    # B-row band from OCR B12/B1
    b12 = (int(0.467 * W), int((1 - 0.579) * H))
    b1 = (int(0.631 * W), int((1 - 0.582) * H))
    print("B12px", b12, "B1px", b1)
    by = (b12[1] + b1[1]) / 2
    y0, y1 = max(0, int(by - 80)), min(H, int(by + 80))
    x0, x1 = max(0, int(ox - 280)), min(W, int(ox + 280))
    bband = im[y0:y1, x0:x1]
    cv2.imwrite(str(OUT / "brow_band.png"), bband)
    blur = cv2.GaussianBlur(bband, (5, 5), 0)
    # expected r for Ø0.40 ≈ 0.20*ppm
    r = max(3, int(0.20 * ppm))
    circles = cv2.HoughCircles(
        blur,
        cv2.HOUGH_GRADIENT,
        dp=1.1,
        minDist=int(0.25 * ppm),
        param1=60,
        param2=12,
        minRadius=max(2, r - 4),
        maxRadius=r + 8,
    )
    circs = []
    if circles is not None:
        for x, y, rr in circles[0]:
            circs.append((x + x0, y + y0, rr))
    circs.sort(key=lambda t: (round((t[1] - oy) / 8), t[0]))
    print("B circles", len(circs), "expect r_px", r)
    for c in circs:
        print(f"  {(c[0]-ox)/ppm:+7.3f}  {(oy-c[1])/ppm:+6.3f}  d={2*c[2]/ppm:.3f}")

    vis = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
    cv2.circle(vis, a1, 6, (0, 255, 0), 2)
    cv2.circle(vis, a12, 6, (0, 255, 0), 2)
    cv2.circle(vis, b12, 6, (255, 0, 0), 2)
    cv2.circle(vis, b1, 6, (255, 0, 0), 2)
    for c in circs:
        cv2.circle(vis, (int(c[0]), int(c[1])), int(c[2]), (0, 180, 255), 1)
    cv2.imwrite(str(OUT / "layout_a_marked.png"), vis)

    rec = {
        "ppm_ocr_a": ppm,
        "smt_z_solder": smt_z_solder,
        "a_pads": [
            {"x": (p[0] - ox) / ppm, "y": (oy - p[1]) / ppm, "w": p[2] / ppm, "h": p[3] / ppm}
            for p in pads
        ],
        "b_circles": [
            {"x": (c[0] - ox) / ppm, "y": (oy - c[1]) / ppm, "d": 2 * c[2] / ppm} for c in circs
        ],
    }
    (OUT / "LAYOUT_PRECISE.json").write_text(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
