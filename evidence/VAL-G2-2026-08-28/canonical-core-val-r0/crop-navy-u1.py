#!/usr/bin/env python3
"""Crop the navy 3D-preview board strip and the left U1 region.

The 3D canvas background can contain a few navy-ish pixels. Prefer the densest
navy cluster in the upper half of the frame so the U1 click is on the board,
not the empty workspace.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image


def navy_hits(im: Image.Image):
    px = im.load()
    w, h = im.size
    hits = []
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            r, g, b = px[x, y][:3]
            if 10 <= r <= 70 and 20 <= g <= 90 and 70 <= b <= 160 and b > r + 20 and b > g:
                hits.append((x, y))
    return hits


def bbox(hits):
    xs = [p[0] for p in hits]
    ys = [p[1] for p in hits]
    return min(xs), min(ys), max(xs), max(ys)


def densest_cluster(hits, cell=48):
    buckets = defaultdict(list)
    for x, y in hits:
        buckets[(x // cell, y // cell)].append((x, y))
    key = max(buckets, key=lambda k: len(buckets[k]))
    return buckets[key]


def main() -> int:
    src = Path(sys.argv[1])
    navy_out = Path(sys.argv[2])
    u1_out = Path(sys.argv[3])
    im = Image.open(src).convert("RGB")
    w, h = im.size
    hits = navy_hits(im)
    if len(hits) < 40:
        print(json.dumps({"ok": False, "src": str(src), "hits": len(hits)}))
        return 1
    upper = [p for p in hits if p[1] < int(h * 0.45)]
    use = upper if len(upper) >= 20 else hits
    cluster = densest_cluster(use)
    if len(cluster) >= 12:
        use = cluster
    x0, y0, x1, y1 = bbox(use)
    pad = 24
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(w, x1 + pad)
    y1 = min(h, y1 + pad)
    # Keep a usable board strip if the cluster is a tiny speck
    if (x1 - x0) < 180 or (y1 - y0) < 80:
        x0, y0, x1, y1 = bbox(hits)
        x0 = max(0, x0 - pad)
        y0 = max(0, y0 - pad)
        x1 = min(w, x1 + pad)
        y1 = min(h, y1 + pad)
    navy = im.crop((x0, y0, x1, y1))
    navy.save(navy_out)
    uw = max(220, int((x1 - x0) * 0.42))
    uh = y1 - y0
    u1 = im.crop((x0, y0, min(w, x0 + uw), y1))
    u1.save(u1_out)
    u1_css = [int(x0 + uw * 0.38), int(y0 + uh * 0.48)]
    print(json.dumps({
        "ok": True,
        "src": str(src),
        "hits": len(hits),
        "used": len(use),
        "navy_box": [x0, y0, x1, y1],
        "navy": str(navy_out),
        "u1": str(u1_out),
        "u1_css": u1_css,
        "navy_size": list(navy.size),
        "u1_size": list(u1.size),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
