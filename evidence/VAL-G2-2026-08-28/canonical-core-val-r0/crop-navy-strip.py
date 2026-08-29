#!/usr/bin/env python3
"""Find the thin navy PCB strip in a 3D-preview screenshot and crop U1."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image


def is_navy(rgb) -> bool:
    r, g, b = rgb[:3]
    # Live 3D preview solder-mask is near (0, 24, 64)–(0, 24, 72), not mid-blue UI chrome.
    return r <= 16 and 12 <= g <= 40 and 48 <= b <= 96 and b >= g + 24


def main() -> int:
    src = Path(sys.argv[1])
    navy_out = Path(sys.argv[2])
    u1_out = Path(sys.argv[3])
    im = Image.open(src).convert("RGB")
    w, h = im.size
    px = im.load()
    row_counts = []
    for y in range(h):
        n = 0
        for x in range(0, w, 2):
            if is_navy(px[x, y]):
                n += 1
        row_counts.append(n)
    best_y = max(range(h), key=lambda y: row_counts[y])
    thresh = max(12, int(row_counts[best_y] * 0.35))
    y0 = best_y
    y1 = best_y
    while y0 > 0 and row_counts[y0 - 1] >= thresh:
        y0 -= 1
    while y1 + 1 < h and row_counts[y1 + 1] >= thresh:
        y1 += 1
    xs = []
    for y in range(y0, y1 + 1):
        for x in range(0, w, 1):
            if is_navy(px[x, y]):
                xs.append(x)
    if not xs or (y1 - y0) < 8:
        print(json.dumps({"ok": False, "src": str(src), "best_y": best_y, "row": row_counts[best_y]}))
        return 1
    x0, x1 = min(xs), max(xs)
    pad_x, pad_y = 16, 28
    box = (
        max(0, x0 - pad_x),
        max(0, y0 - pad_y),
        min(w, x1 + pad_x),
        min(h, y1 + pad_y),
    )
    navy = im.crop(box)
    navy.save(navy_out)
    nw, nh = navy.size
    u1 = navy.crop((0, 0, max(180, int(nw * 0.34)), nh))
    u1.save(u1_out)
    print(json.dumps({
        "ok": True,
        "src": str(src),
        "best_y": best_y,
        "row_hits": row_counts[best_y],
        "box": list(box),
        "navy_size": list(navy.size),
        "u1_size": list(u1.size),
        "navy": str(navy_out),
        "u1": str(u1_out),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
