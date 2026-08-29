#!/usr/bin/env python3
"""Tighter STEP isolation: SMT tails, TH pins, legs. Independent of prior notes."""
from __future__ import annotations

import json
import re
import statistics
from collections import defaultdict
from pathlib import Path

STP = Path(__file__).resolve().parent / "datasheets/_extract/GT-USB-7005A.stp"
OUT = Path(__file__).resolve().parent / "_h0_measure"


def pts():
    text = STP.read_text(errors="replace")
    out = []
    for m in re.finditer(
        r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*([eE0-9.+-]+)\s*,\s*([eE0-9.+-]+)\s*,\s*([eE0-9.+-]+)\s*\)",
        text,
    ):
        out.append((float(m.group(1)), float(m.group(2)), float(m.group(3))))
    return out


def cl1(vals, tol):
    if not vals:
        return []
    s = sorted(vals)
    g = [[s[0]]]
    for v in s[1:]:
        if abs(v - g[-1][-1]) <= tol:
            g[-1].append(v)
        else:
            g.append([v])
    return [(statistics.mean(x), len(x), min(x), max(x)) for x in g]


def main():
    P = pts()
    print("n", len(P))
    # SMT tails: Z far rear, |X|<=3.0, Y near 0.4, thin in Y
    smt = [p for p in P if p[2] <= -4.20 and abs(p[0]) <= 3.05 and 0.25 <= p[1] <= 0.55]
    print("smt_strict", len(smt))
    print("smt Y", cl1([p[1] for p in smt], 0.01))
    print("smt Z", cl1([p[2] for p in smt], 0.05))
    # pair left/right edges of 0.20 mm tails -> centres
    xcl = cl1([p[0] for p in smt], 0.03)
    print("smt X raw", [(round(c, 3), n) for c, n, *_ in xcl])
    # pair adjacent clusters ~0.20 apart
    xs = [c for c, n, *_ in xcl if n >= 8]
    centres = []
    i = 0
    while i < len(xs) - 1:
        if abs(xs[i + 1] - xs[i] - 0.20) < 0.04:
            centres.append((xs[i] + xs[i + 1]) / 2)
            i += 2
        else:
            i += 1
    print("smt centres", [round(c, 3) for c in centres], "n", len(centres))
    smt_y = statistics.mean(p[1] for p in smt) if smt else None
    print("smt_y_mean", smt_y)

    # shell min Y among |X|<4.4 (body, not legs)
    body = [p for p in P if abs(p[0]) <= 4.40]
    print("body Y", min(p[1] for p in body), max(p[1] for p in body))
    print("sink", smt_y - min(p[1] for p in body) if smt_y else None)

    # TH pins: should be two staggered rows. Look at points with
    # |X| in 0.2..3.1, Z mid-body (-3.6..-2.0), Y below SMT (into board or above)
    # In STEP, +Y is up. SMT at +0.40 = PCB top. TH go downward toward -Y.
    th = [
        p
        for p in P
        if 0.20 <= abs(p[0]) <= 3.10 and -3.70 <= p[2] <= -2.10 and -0.90 <= p[1] <= 1.40
    ]
    print("th cand", len(th))
    print("th X", [(round(c, 3), n) for c, n, *_ in cl1([p[0] for p in th], 0.05) if n >= 15])
    print("th Y", [(round(c, 3), n) for c, n, *_ in cl1([p[1] for p in th], 0.04) if n >= 10])
    print("th Z", [(round(c, 3), n) for c, n, *_ in cl1([p[2] for p in th], 0.08) if n >= 10])

    # lowest Y of points that look like pin tips: |X| at 0.50-ish bands, Y < 0
    tips = [p for p in P if 0.20 <= abs(p[0]) <= 3.10 and p[1] < 0.10 and -3.70 <= p[2] <= -2.00]
    print("tips", len(tips), "ymin", min((p[1] for p in tips), default=None))
    print("tips Y", cl1([p[1] for p in tips], 0.03)[:8])

    # legs: |X|>=5.5
    legs = [p for p in P if abs(p[0]) >= 5.50]
    print("legs", len(legs))
    print("leg X", [(round(c, 3), n) for c, n, *_ in cl1([p[0] for p in legs], 0.06)])
    print("leg Y", [(round(c, 3), n) for c, n, *_ in cl1([p[1] for p in legs], 0.06)])
    print("leg Z", [(round(c, 3), n) for c, n, *_ in cl1([p[2] for p in legs], 0.10)])

    # Does any metal form a bottom clamp at a fixed Y below SMT?
    # Look at points with |X|>=5.5 (tabs) Y distribution vs SMT
    if smt_y is not None:
        print("leg Y relative to SMT", [(round(smt_y - c, 3), n) for c, n, *_ in cl1([p[1] for p in legs], 0.06)])

    # write
    rec = {
        "n": len(P),
        "smt_n": len(smt),
        "smt_y_mean": smt_y,
        "smt_centres": centres,
        "body_ymin": min(p[1] for p in body),
        "sink": (smt_y - min(p[1] for p in body)) if smt_y else None,
        "on_160_protrusion": ((smt_y - min(p[1] for p in body)) - 1.60) if smt_y else None,
        "th_x": cl1([p[0] for p in th], 0.05),
        "th_y": cl1([p[1] for p in th], 0.04),
        "leg_x": cl1([p[0] for p in legs], 0.06),
        "leg_y": cl1([p[1] for p in legs], 0.06),
        "leg_z": cl1([p[2] for p in legs], 0.10),
    }
    (OUT / "STEP2.json").write_text(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
