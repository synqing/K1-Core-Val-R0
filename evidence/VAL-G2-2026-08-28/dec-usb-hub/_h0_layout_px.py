#!/usr/bin/env python3
"""Measure recommended PCB layout from pixels, scaled to labelled 5.50 mm A-span."""
from __future__ import annotations

import json
import statistics
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "_h0_measure"
IMG = HERE / "datasheets/_extract/hires/layout_a.png"
CROP = HERE / "datasheets/_extract/measured/crop_pcb_layout.png"


def blobs(path: Path, tag: str):
    im = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    h, w = im.shape
    # ink
    _, bw = cv2.threshold(im, 80, 255, cv2.THRESH_BINARY_INV)
    # close small gaps
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    bw = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, k)
    n, lab, stats, cent = cv2.connectedComponentsWithStats(bw, 8)
    items = []
    for i in range(1, n):
        x, y, ww, hh, area = stats[i]
        if area < 8 or area > 4000:
            continue
        items.append(
            {
                "x": float(cent[i][0]),
                "y": float(cent[i][1]),
                "w": int(ww),
                "h": int(hh),
                "area": int(area),
                "aspect": hh / max(ww, 1),
            }
        )
    vis = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
    for it in items:
        cv2.rectangle(
            vis,
            (int(it["x"] - it["w"] / 2), int(it["y"] - it["h"] / 2)),
            (int(it["x"] + it["w"] / 2), int(it["y"] + it["h"] / 2)),
            (0, 0, 255),
            1,
        )
    cv2.imwrite(str(OUT / f"{tag}_blobs.png"), vis)
    return im, items


def find_a_row(items):
    # tall thin pads, similar Y, 12 of them
    cands = [it for it in items if 1.6 <= it["aspect"] <= 5.5 and 4 <= it["w"] <= 25 and 12 <= it["h"] <= 70]
    # cluster by Y
    cands = sorted(cands, key=lambda z: z["y"])
    best = []
    for it in cands:
        band = [x for x in cands if abs(x["y"] - it["y"]) < 6]
        if len(band) > len(best):
            best = band
    best = sorted(best, key=lambda z: z["x"])
    return best


def find_circles_like(items, dmin, dmax):
    out = []
    for it in items:
        if abs(it["w"] - it["h"]) <= 4 and dmin <= (it["w"] + it["h"]) / 2 <= dmax:
            out.append(it)
    return out


def main():
    report = {}
    for tag, path in (("layout_a", IMG), ("crop_pcb", CROP)):
        im, items = blobs(path, tag)
        h, w = im.shape
        arow = find_a_row(items)
        print(f"\n=== {tag} {w}x{h} blobs={len(items)} arow={len(arow)} ===")
        if len(arow) < 8:
            # dump candidate sizes
            cands = sorted(items, key=lambda z: (-z["aspect"], z["area"]))[:30]
            for c in cands:
                print(f"  cand x={c['x']:.0f} y={c['y']:.0f} {c['w']}x{c['h']} a={c['aspect']:.2f}")
            report[tag] = {"arow_n": len(arow)}
            continue
        span_px = arow[-1]["x"] - arow[0]["x"]
        ppm = span_px / 5.50
        ox = (arow[0]["x"] + arow[-1]["x"]) / 2
        oy = statistics.mean(r["y"] for r in arow)
        print(f"  span_px={span_px:.1f} ppm={ppm:.3f} origin=({ox:.1f},{oy:.1f})")
        print(f"  pad {arow[0]['w']/ppm:.3f} x {arow[0]['h']/ppm:.3f} mm")
        a_mm = []
        for i, r in enumerate(arow):
            xm = (r["x"] - ox) / ppm
            ym = (oy - r["y"]) / ppm  # image Y down; +mm toward top of image = into board
            a_mm.append({"i": i + 1, "x": xm, "y": ym, "w": r["w"] / ppm, "h": r["h"] / ppm})
            print(f"  A? {i+1:2} x={xm:+7.3f} y={ym:+6.3f}")

        # circles: locators ~0.75 mm, B holes ~0.40 mm
        circs = find_circles_like(items, 0.25 * ppm, 1.20 * ppm)
        circ_mm = []
        print("  circles-like", len(circs))
        for c in sorted(circs, key=lambda z: (z["y"], z["x"])):
            xm = (c["x"] - ox) / ppm
            ym = (oy - c["y"]) / ppm
            d = (c["w"] + c["h"]) / 2 / ppm
            if abs(xm) > 8 or abs(ym) > 8:
                continue
            circ_mm.append({"x": xm, "y": ym, "d": d})
            print(f"    circ x={xm:+7.3f} y={ym:+6.3f} d={d:.3f}")

        # slots: elongated, not A-row
        slots = []
        for it in items:
            if it in arow:
                continue
            if it["w"] >= 0.6 * ppm and it["h"] >= 0.6 * ppm and it["area"] >= 40:
                xm = (it["x"] - ox) / ppm
                ym = (oy - it["y"]) / ppm
                if 4.5 <= abs(xm) <= 7.5 and -8 <= ym <= 3:
                    slots.append(
                        {
                            "x": xm,
                            "y": ym,
                            "w": it["w"] / ppm,
                            "h": it["h"] / ppm,
                        }
                    )
        slots.sort(key=lambda z: (z["y"], z["x"]))
        print("  slot-like")
        for s in slots:
            print(f"    slot x={s['x']:+7.3f} y={s['y']:+6.3f} {s['w']:.2f}x{s['h']:.2f}")

        report[tag] = {
            "ppm": ppm,
            "origin_px": [ox, oy],
            "arow": a_mm,
            "circles": circ_mm,
            "slots": slots,
            "pad_w_mm": statistics.mean(r["w"] / ppm for r in arow),
            "pad_h_mm": statistics.mean(r["h"] / ppm for r in arow),
        }

    (OUT / "LAYOUT_PX.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
