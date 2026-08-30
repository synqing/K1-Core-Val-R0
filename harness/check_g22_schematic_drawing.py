#!/usr/bin/env python3
"""Fail-closed G2.2 schematic drawing gate (stacked Type-C, OCS picture-frames).

Electrical USB membership is check_g22_usb_hub.py. This checker refuses a
sheet whose Type-C symbols occupy the same pin field or whose OCS/EN nets
are drawn as picture frames. Zero parsed records cannot print PASS.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from extract_electrical_graph import _load_source
from g22_schematic_drawing import analyse


def print_counts(report) -> None:
    c = report.counts
    print(
        "COUNTS "
        f"files_inspected={c.get('files_inspected', 0)} "
        f"easyeda_records_parsed={c.get('easyeda_records_parsed', 0)} "
        f"components_inspected={c.get('components_inspected', 0)} "
        f"type_c_symbols={c.get('type_c_symbols', 0)} "
        f"nets_inspected={c.get('nets_inspected', 0)} "
        f"line_segments_inspected={c.get('line_segments_inspected', 0)} "
        f"assertions_executed={c.get('assertions_executed', 0)}"
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--json-stdout", action="store_true")
    ns = parser.parse_args(argv)

    source, _meta = _load_source(ns.source)
    report = analyse(source, source_path=str(ns.source))
    if ns.output:
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print_counts(report)
    print(
        "SCHEMATIC_DRAWING "
        f"ok={report.ok} unresolved={report.unresolved} "
        f"type_c={report.counts.get('type_c_symbols')} "
        f"stacked={len(report.stacked_pairs)} "
        f"picture_frames={len(report.picture_frames)}"
    )
    for item in report.errors:
        print(f"  ERROR {item}")
    for item in report.warnings:
        print(f"  WARN {item}")
    if ns.json_stdout:
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if report.unresolved or not report.ok:
        print("CHECK=FAIL")
        return 2
    print("CHECK=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
