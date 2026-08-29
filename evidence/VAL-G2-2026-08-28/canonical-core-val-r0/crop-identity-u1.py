#!/usr/bin/env python3
"""Tight U1 crop from the navy 3D board, padded to gate minimum 640x360."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image


def is_board(p):
    r, g, b = p[:3]
    return r <= 20 and 15 <= g <= 50 and 55 <= b <= 110 and b > g + 20


def main() -> int:
    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    im = Image.open(src).convert("RGB")
    w, h = im.size
    px = im.load()
    xs, ys = [], []
    for y in range(h):
        for x in range(w):
            if is_board(px[x, y]):
                xs.append(x)
                ys.append(y)
    if not xs:
        print(json.dumps({"ok": False, "src": str(src), "err": "no board"}))
        return 1
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    # Left 48% of the board strip is U1 / cut-out; pad to 640x360 minimum.
    uw = max(int((x1 - x0) * 0.50), 640)
    uh = max(y1 - y0 + 80, 360)
    cx0 = max(0, x0 - 20)
    cy0 = max(0, y0 - 40)
    cx1 = min(w, cx0 + uw)
    cy1 = min(h, cy0 + uh)
    if cx1 - cx0 < 640:
        cx0 = max(0, cx1 - 640)
    if cy1 - cy0 < 360:
        cy0 = max(0, cy1 - 360)
        cy1 = min(h, cy0 + 360)
    crop = im.crop((cx0, cy0, cx1, cy1))
    crop.save(out)
    print(json.dumps({
        "ok": True,
        "src": str(src),
        "out": str(out),
        "board": [x0, y0, x1, y1],
        "crop": [cx0, cy0, cx1, cy1],
        "size": list(crop.size),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
