#!/usr/bin/env python3
"""Read-only census of DRC-listed floating pins against live pin names and nets."""
from __future__ import annotations

import json
import re
from collections import defaultdict

from execute_canonical_container import JOBS, PAGE, load_fixture_executor
from repair_power_buck import component_records


FLOATING = {
    "C10-PWR2": ["1", "2"],
    "D1-PWR1": ["3", "4", "5", "6"],
    "J1-PWR1": ["B5", "B6", "B7", "B8", "B9", "B12", "1", "A1", "A4", "A5", "A6", "A7", "A8", "A9", "A12"],
    "J7-ESP": ["B8", "A8"],
    "J9-AUD": ["7", "8", "9", "10", "11", "12"],
    "SW1-RTC": ["3", "4"],
    "SW2-ESP": ["3", "4"],
    "SW3-ESP": ["3", "4"],
    "SW4-VAL": ["3", "4"],
    "U1-PWR1": ["10"],
    "U11-AUD": ["1", "2", "4"],
    "U12-NFC": ["2", "15", "17", "18", "19", "20", "23", "25", "28", "29", "31"],
    "U13-MOT": ["2", "3", "5", "7", "8", "11"],
    "U16-VAL": ["3", "4", "5"],
    "U4-PWR2": ["3"],
    "U5-PWR2": ["4"],
    "U6-RTC": [
        "G13", "G11", "G10", "G5", "G4", "G3", "G2", "G1", "F14", "F13", "F4", "F3", "F2", "F1",
        "E12", "E11", "E10", "E8", "E5", "E4", "E3", "E1", "D14", "D13", "D12", "D11", "D10", "D9",
        "D8", "D6", "D5", "D4", "D3", "D2", "D1", "C14", "C13", "C12", "C11", "C10", "C9", "C8",
        "C7", "C6", "C5", "C4", "C3", "C2", "C1", "B14", "B13", "B12", "B11", "B9", "B8", "B7",
        "B6", "B4", "B3", "B2", "B1", "A13", "A12", "A11", "A10", "A9", "A8", "A7", "A6", "A5",
        "A4", "A3", "A2", "P13", "P9", "P7", "P6", "P5", "P4", "P2", "N13", "N12", "N10", "N7",
        "N6", "N3", "M14", "M13", "M11", "M6", "M5", "M4", "M3", "L10", "L8", "L7", "L6", "L5",
        "K10", "K7", "K6", "J12", "J2", "H14", "H13", "H10", "H5", "H4", "H3", "H2", "H1",
    ],
    "U9-ESP": ["9", "10", "11", "12", "15", "16", "17", "23", "24", "25", "26", "28", "29", "30", "31", "32", "33", "34", "35"],
    "Y2-NFC": ["4", "3"],
}

POWER_RE = re.compile(
    r"VDD|VSS|GND|NVCC|AVDD|DVDD|VBUS|VIN|VOUT|3V3|5V|USB_OTG|VDDA|VDDHIGH|VDD_SOC|VDD_HIGH|VDD_SNVS",
    re.I,
)
SKIP = {
    ("C10-PWR2", "1"), ("C10-PWR2", "2"),
    ("U12-NFC", "15"), ("U12-NFC", "20"), ("U12-NFC", "23"),
}


def _pin_fields(pin: dict) -> dict:
    return {
        "number": str(pin.get("pinNumber") or pin.get("number") or pin.get("name") or ""),
        "name": str(pin.get("pinName") or pin.get("name") or pin.get("label") or ""),
        "net": str(pin.get("net") or pin.get("netName") or ""),
        "no_connect": pin.get("noConnected") if "noConnected" in pin else pin.get("no_connect"),
    }


def classify(designator: str, pin: dict) -> str:
    number = pin["number"]
    name = pin["name"]
    token = f"{name} {number}"
    if (designator, number) in SKIP:
        return "SKIP_FUNCTIONAL"
    if POWER_RE.search(token):
        return "POWER_OR_GND"
    if designator.startswith("SW") and number in {"3", "4"}:
        return "NC_UNUSED_THROW"
    if designator == "J7-ESP" and number in {"A8", "B8"}:
        return "NC_UNUSED_SBU"
    if designator.startswith("U6-") and "GPIO" in name.upper():
        return "NC_UNUSED_GPIO"
    if designator.startswith("U9-") and "GPIO" in name.upper():
        return "NC_UNUSED_GPIO"
    return "REVIEW"


def main() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    snap = base.source_snapshot()
    live = component_records(snap["source"])
    jobs = []
    missing = []
    for designator in FLOATING:
        if designator not in live:
            missing.append(designator)
            continue
        jobs.append({
            "tool": "list_schematic_component_pins",
            "tag": designator,
            "args": {
                "componentPrimitiveId": live[designator]["primitive_id"],
                "expectedDocumentUuid": PAGE,
            },
        })
    results = base.run_batch(jobs, "floating-pin-census") if jobs else []
    by_class = defaultdict(list)
    rows = []
    for result in results:
        designator = result.get("tag")
        pins = (result.get("result") or {}).get("pins") or (result.get("result") or [])
        if isinstance(pins, dict):
            pins = pins.get("pins") or pins.get("items") or []
        wanted = set(FLOATING.get(designator, []))
        for raw in pins:
            pin = _pin_fields(raw if isinstance(raw, dict) else {})
            if wanted and pin["number"] not in wanted and pin["name"] not in wanted:
                continue
            decision = classify(designator, pin)
            row = {"designator": designator, "decision": decision, **pin}
            rows.append(row)
            by_class[decision].append(f"{designator}.{pin['number']} {pin['name']}".strip())
    out = {
        "source_hash": snap["source_hash"],
        "missing": missing,
        "counts": {key: len(value) for key, value in sorted(by_class.items())},
        "by_class": {key: value for key, value in sorted(by_class.items())},
        "rows": rows,
    }
    path = JOBS / "floating-pin-census.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"HASH={snap['source_hash']}")
    print(f"MISSING={missing}")
    print(f"COUNTS={out['counts']}")
    print(f"OUT={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
