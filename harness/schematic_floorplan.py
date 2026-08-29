#!/usr/bin/env python3
"""Signal-weighted schematic floorplan.

Writes JSON and a self-contained HTML decision board. GND is excluded from
placement weight. Declared reading flow overrides residual graph weight.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
from schematic_domains import (
    DOMAINS,
    adjacency_from_membership,
    declared_region_boxes,
    domain_for_designator,
)


def membership_from_graph(graph: dict) -> dict[str, set[str]]:
    nets_by_des = defaultdict(set)
    pins = (graph.get("pin_membership") or {}).get("pins") or {}
    for key, row in pins.items():
        des = row.get("designator")
        net = row.get("net")
        if des and net:
            nets_by_des[des].add(net)
        for extra in row.get("nets") or []:
            if des and extra:
                nets_by_des[des].add(extra)
    # Identity still places designators that have no bound pins.
    for designator in graph.get("identity") or {}:
        nets_by_des.setdefault(designator, set())
    return dict(nets_by_des)


def build_floorplan(graph: dict) -> dict:
    membership = membership_from_graph(graph)
    domains = defaultdict(list)
    for designator in sorted(graph.get("identity") or {}):
        domains[domain_for_designator(designator)].append(designator)
    adjacency = adjacency_from_membership(membership)
    regions = declared_region_boxes()
    placed = {}
    for domain, designators in domains.items():
        box = regions[domain]
        cols = max(1, int(box["w"] / 240))
        for index, designator in enumerate(designators):
            col = index % cols
            row = index // cols
            placed[designator] = {
                "domain": domain,
                "x": box["x"] + 140 + col * 240,
                "y": box["y"] + 200 + row * 200,
                "rotation": 0,
            }
    return {
        "schema": "k1.schematic-floorplan.v1",
        "domains": {k: domains.get(k, []) for k in DOMAINS},
        "domain_counts": {k: len(domains.get(k, [])) for k in DOMAINS},
        "regions": regions,
        "adjacency": adjacency,
        "placements": placed,
        "units": "schematic_0.01_inch",
        "note": "Soft regions. Domain walls must not terminate wires.",
    }


UNIT_MM = 0.254  # 1 schematic unit = 0.01 inch


def render_html(plan: dict) -> str:
    scale = 0.045
    max_x = max(r["x"] + r["w"] for r in plan["regions"].values()) + 400
    max_y = max(r["y"] + r["h"] for r in plan["regions"].values()) + 400
    width = max_x * scale
    height = max_y * scale + 36
    weights = plan["adjacency"]["weights"]
    regions = []
    for name, box in plan["regions"].items():
        count = plan["domain_counts"].get(name, 0)
        w_mm = box["w"] * UNIT_MM
        h_mm = box["h"] * UNIT_MM
        regions.append(
            f'<g data-domain="{name}">'
            f'<rect x="{box["x"]*scale:.1f}" y="{box["y"]*scale:.1f}" '
            f'width="{box["w"]*scale:.1f}" height="{box["h"]*scale:.1f}" '
            f'class="region"/>'
            f'<text x="{(box["x"]+120)*scale:.1f}" y="{(box["y"]+360)*scale:.1f}" '
            f'class="title">{name} · {count} parts</text>'
            f'<text x="{(box["x"]+120)*scale:.1f}" y="{(box["y"]+620)*scale:.1f}" '
            f'class="dim">{box["w"]} × {box["h"]} su · {w_mm:.0f} × {h_mm:.0f} mm</text>'
            f"</g>"
        )
    # adjacency strokes between region centres, thickness ~ weight
    strokes = []
    centres = {
        name: (box["x"] + box["w"] / 2, box["y"] + box["h"] / 2)
        for name, box in plan["regions"].items()
    }
    if weights:
        peak = max(weights.values())
    else:
        peak = 1
    for key, value in weights.items():
        left, right = key.split("|")
        if left not in centres or right not in centres:
            continue
        x1, y1 = centres[left]
        x2, y2 = centres[right]
        sw = 0.6 + 4.0 * (value / peak)
        strokes.append(
            f'<line x1="{x1*scale:.1f}" y1="{y1*scale:.1f}" '
            f'x2="{x2*scale:.1f}" y2="{y2*scale:.1f}" '
            f'class="seam" stroke-width="{sw:.2f}"/>'
        )
    order = " → ".join(plan["adjacency"]["reading_order"])
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8"/>
<title>K1-CORE-VAL-R0 schematic soft-region floorplan</title>
<style>
  body {{ margin: 24px; font: 16px/1.45 ui-sans-serif, Helvetica, sans-serif; color: #111; background: #f4f1ea; }}
  h1 {{ font-size: 22px; margin: 0 0 8px; }}
  .meta {{ max-width: 72rem; }}
  svg {{ background: #fff; border: 1px solid #222; margin-top: 16px; }}
  .region {{ fill: #f7f3e8; stroke: #222; stroke-width: 1.2; stroke-dasharray: 6 4; }}
  .title {{ font: 600 11px ui-sans-serif; fill: #111; }}
  .dim {{ font: 10px ui-sans-serif; fill: #333; }}
  .seam {{ stroke: #444; fill: none; opacity: 0.45; }}
  .scale {{ font: 10px ui-sans-serif; fill: #111; }}
  table {{ border-collapse: collapse; margin-top: 16px; }}
  td, th {{ border: 1px solid #333; padding: 4px 8px; font-size: 13px; }}
  @media print {{ .card {{ break-inside: avoid; }} }}
</style>
</head>
<body>
<main class="card">
<h1>Schematic soft-region floorplan (proposal)</h1>
<p class="meta">Scale: 1 SVG pixel = {1/scale:.1f} schematic units. 1 schematic unit = 0.01 inch = 0.254 mm. Sheet extents {max_x * UNIT_MM:.0f} × {max_y * UNIT_MM:.0f} mm. Regions are visual organisation aids and must not fragment wiring. GND is excluded from placement weight. Power and high-fanout rails are downweighted. Buses collapse to one interface. Declared reading flow overrides residual weight.</p>
<p class="meta"><strong>Reading flow:</strong> {order}</p>
<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-label="Soft-region schematic floorplan">
{''.join(strokes)}
{''.join(regions)}
<g class="scalebar">
  <line x1="16" y1="{height-18:.1f}" x2="{16 + (1000*scale):.1f}" y2="{height-18:.1f}" stroke="#111" stroke-width="2"/>
  <text class="scale" x="16" y="{height-6:.1f}">1000 su = {1000 * UNIT_MM:.0f} mm</text>
</g>
</svg>
<table>
<caption>Residual signal adjacency after GND exclusion</caption>
<tr><th>Seam</th><th>Weight</th></tr>
{''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k,v in list(weights.items())[:24])}
</table>
<p class="meta">Coordinates remain proposals until this board is accepted. This is not PCB geometry and not JLC-LAYOUT-READY.</p>
</main>
</body>
</html>
"""


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--html", type=Path)
    args = parser.parse_args(argv)
    graph = json.loads(args.graph.read_text(encoding="utf-8"))
    if not (graph.get("identity") or {}):
        raise SystemExit("schematic_floorplan: 0 designators; failing closed")
    plan = build_floorplan(graph)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    if args.html:
        args.html.parent.mkdir(parents=True, exist_ok=True)
        args.html.write_text(render_html(plan), encoding="utf-8")
    print(
        "FLOORPLAN=OK "
        f"designators={sum(plan['domain_counts'].values())} "
        f"domains={sum(1 for n in plan['domain_counts'].values() if n)} "
        f"seams={len(plan['adjacency']['weights'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
