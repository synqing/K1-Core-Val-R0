#!/usr/bin/env python3
"""ONE command: run the dual-grammar (V2 2.2.40.8 / V3 3.2.149) fault battery.

Runs, in order:

  1. easyeda_source_format --self-test
       - grammar detection, V3 record parsing, V2-shaped normalisation
       - RECORD-SHAPE DRIFT cases (renamed field, removed field, null coordinate,
         renamed LINE->WIRE join key) — every one expected to go RED
       - TRUNCATED RECORD cases (cut payload, cut header, missing separator)
       - REAL-SNAPSHOT DIFFERENTIAL: the same schematic page captured on both
         hosts must yield an identical designator set, wire set, wire geometry,
         component anchors and wire->net map. This is the only check here with an
         EXTERNAL denominator.

  2. check_schematic_connectivity --self-test
       - the existing drawing-oracle battery (RED, abstention, tolerance-guard
         controls) plus the V3 grammar control, the V3 fail-closed cases, and the
         CROSS-GRAMMAR EQUALITY check that the same sheet in both grammars
         produces an IDENTICAL report.

Exit 0 = PASS, 1 = FAIL. Read-only; never touches EasyEDA or a bridge.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

HARNESS = pathlib.Path(__file__).resolve().parent
STEPS = [
    ("source-format + record-shape-drift + real-snapshot differential",
     [sys.executable, str(HARNESS / "easyeda_source_format.py"), "--self-test"]),
    ("connectivity oracle battery + cross-grammar equality",
     [sys.executable, str(HARNESS / "check_schematic_connectivity.py"), "--self-test"]),
]


def main() -> int:
    failed = []
    for name, cmd in STEPS:
        print(f"\n=== {name} ===", flush=True)
        rc = subprocess.run(cmd).returncode
        print(f"--- exit {rc} ---")
        if rc != 0:
            failed.append(f"{name} (exit {rc})")
    print()
    if failed:
        print("V3_GRAMMAR_BATTERY=FAIL")
        for item in failed:
            print(f"  failed: {item}")
        return 1
    print("V3_GRAMMAR_BATTERY=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
