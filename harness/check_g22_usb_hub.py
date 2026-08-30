#!/usr/bin/env python3
"""Fail-closed G2.2 USB2422 + J1 semantic gate (D-049 / D-050).

Refuses PASS when J1 is unwired, the USB2422 transform is unproven, required
support pins are open, straps are wrong, DN1/DN2/UP are broken, the S3 XOR is
same-net or double-fitted, F6 IN is 5V_PROTECTED, R85/R90/R94/C123 are an
unauthorised same-net bypass, XTALOUT is on GND, RBIAS shares XTALIN, or a
west-column USB2422 signal is shorted onto 3V3.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from extract_electrical_graph import _load_source
from g22_usb_hub import analyse


def print_counts(report) -> None:
    c = report.counts
    print(
        "COUNTS "
        f"files_inspected={c.get('files_inspected', 0)} "
        f"easyeda_records_parsed={c.get('easyeda_records_parsed', 0)} "
        f"components_inspected={c.get('components_inspected', 0)} "
        f"connector_pins_resolved={c.get('connector_pins_resolved', 0)} "
        f"usb2422_pins_resolved={c.get('usb2422_pins_resolved', 0)} "
        f"nets_inspected={c.get('nets_inspected', 0)} "
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
    straps = report.straps or {}
    print(
        "USB_HUB "
        f"ok={report.ok} unresolved={report.unresolved} "
        f"j1_wired={report.paths.get('j1_functional_wired')} "
        f"cfg_sel={straps.get('CFG_SEL')} "
        f"non_rem_10={straps.get('non_rem_10')} "
        f"u20_proof={report.transform.get('u20_proof_pins_matched')}"
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
