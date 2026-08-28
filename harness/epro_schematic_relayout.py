#!/usr/bin/env python3
"""G2.2 geometry-only schematic relayout.

This transformer is forbidden from changing electrical semantics. The G2.1
repair transformer already did that work. Allowed mutations are positions,
rotations, wire/label/junction geometry, notes, groups, sheet size and
title-block annotation.

A write is refused until:

1. a layout plan is supplied;
2. the candidate graph is extracted after the geometry rewrite;
3. ``check_electrical_equivalence`` reports PASS against the G2.1 reference.

Tonight this command extracts a graph or refuses a write. It does not invent
placement.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
from extract_electrical_graph import extract_electrical_graph, _load_source, _pin_bindings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="G2.1 V3 source dump")
    parser.add_argument("-o", "--output", type=Path, help="graph JSON (extract mode)")
    parser.add_argument("--pin-bindings", type=Path)
    parser.add_argument("--role", default="G2.2_CANDIDATE")
    parser.add_argument("--layout", type=Path, help="future geometry plan; required to write")
    parser.add_argument("--write", type=Path, help="future rewritten source; refused tonight")
    args = parser.parse_args(argv)

    if args.write or args.layout:
        print("RELAYOUT=REFUSED")
        print(
            "G2.2 may not write geometry until a layout plan exists and the "
            "electrical-graph invariant can be checked against the official "
            "G2.1 freeze. Tonight's job is extract-only."
        )
        return 2

    source, _meta = _load_source(args.source)
    graph = extract_electrical_graph(
        source,
        source_path=str(args.source),
        pin_bindings=_pin_bindings(args.pin_bindings),
        role=args.role,
        official_freeze=False,
    )
    if args.output:
        import json

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(
        "RELAYOUT=EXTRACT_ONLY "
        f"designators={graph['counts']['designators']} "
        f"nets={graph['counts']['named_nets']} "
        f"nc={graph['counts']['nc']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
