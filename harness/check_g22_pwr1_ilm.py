#!/usr/bin/env python3
"""Fail-closed G2.2 PWR1 ILM / R1 semantic gate.

Refuses PASS when U1 pin-role reconstruction is unavailable, when U1-PWR1.9
is on a USB DP/DM net, when USB_EFUSE_ILIM is a one-endpoint stub, when D+
continuity is lost, or when R1's electrical value cannot be resolved without
trusting a stale partId.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from extract_electrical_graph import _load_source
from g22_pwr1_ilm import (
    EXPECTED_R1_OHMS,
    analyse,
    write_audit_markdown,
)


def print_counts(report) -> None:
    c = report.counts
    print(
        "COUNTS "
        f"files_inspected={c.get('files_inspected', 0)} "
        f"easyeda_records_parsed={c.get('easyeda_records_parsed', 0)} "
        f"components_inspected={c.get('components_inspected', 0)} "
        f"symbol_pins_resolved={c.get('symbol_pins_resolved', 0)} "
        f"nets_inspected={c.get('nets_inspected', 0)} "
        f"assertions_executed={c.get('assertions_executed', 0)}"
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--expect-r1-ohms", type=int, default=EXPECTED_R1_OHMS)
    parser.add_argument("--skip-r1-ohms", action="store_true")
    parser.add_argument("--audit-md", type=Path)
    parser.add_argument("--pre-json", type=Path, help="optional pre-fix IlmReport JSON for the ten-pin audit")
    args = parser.parse_args(argv)

    source, _meta = _load_source(args.source)
    expect = None if args.skip_r1_ohms else args.expect_r1_ohms
    report = analyse(source, source_path=str(args.source), expect_r1_ohms=expect)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.audit_md:
        pre = None
        if args.pre_json and args.pre_json.is_file():
            payload = json.loads(args.pre_json.read_text(encoding="utf-8"))
            from g22_pwr1_ilm import PinHit, IlmReport, TPS259474L_PINS
            pre = IlmReport(ok=False, unresolved=False)
            for pin, spec in TPS259474L_PINS.items():
                row = (payload.get("u1_pins") or {}).get(pin) or {}
                pre.u1_pins[pin] = PinHit(
                    pin=pin,
                    name=spec["name"],
                    xy=tuple(row.get("xy") or (0, 0)),
                    nets=list(row.get("nets") or []),
                    open=bool(row.get("open")),
                )
        write_audit_markdown(args.audit_md, pre=pre, post=report)

    print_counts(report)
    r1 = report.r1 or {}
    print(
        "R1 "
        f"electrical_ohms={r1.get('electrical_ohms')} "
        f"mpn={r1.get('mpn')} "
        f"partId={r1.get('partId')} "
        f"metadata_mismatch={r1.get('metadata_mismatch')}"
    )
    pin9 = report.u1_pins.get("9")
    print(
        "U1.9 "
        f"role={pin9.name if pin9 else None} "
        f"nets={pin9.nets if pin9 else None} "
        f"xy={pin9.xy if pin9 else None}"
    )
    if report.warnings:
        for item in report.warnings:
            print(f"WARNING {item}")
    if report.unresolved:
        print("G22_PWR1_ILM=UNRESOLVED")
        for item in report.errors:
            print(f"  {item}")
        return 2
    if not report.ok:
        print("G22_PWR1_ILM=FAIL")
        for item in report.errors:
            print(f"  {item}")
        return 2
    print("G22_PWR1_ILM=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
