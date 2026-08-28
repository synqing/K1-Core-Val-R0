#!/usr/bin/env python3
"""Create a guarded source candidate that removes INA226 cursor-tail branches.

The VIN mapping is already corrected. EasyEDA committed two extra vertical
segments because wire mode remained active during rehydration. This repair
removes only those two branches and preserves every other record exactly.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


PROJECT_UUID = "09e9c541fd3d404082d4b92e55ae5336"
DOCUMENT_UUID = "1991698f35bf4c09b8de4bcf78bd2b7b"
EXPECTED_SOURCE_HASH = "44488:6f3a4e8d"

REPLACEMENTS = {
    "e14555": ["WIRE", "e14555", [[690, 1080, 775, 1080]], "st8", 0],
    "e14561": ["WIRE", "e14561", [[690, 1060, 775, 1060], [775, 1060, 775, 1070], [775, 1070, 690, 1070]], "st8", 0],
}

REMOVE_IDS: set[str] = set()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    snapshot = json.loads(args.snapshot.read_text())
    if snapshot.get("project_uuid") != PROJECT_UUID or snapshot.get("document_uuid") != DOCUMENT_UUID:
        raise SystemExit("identity mismatch in repair snapshot")
    if snapshot.get("source_hash") != EXPECTED_SOURCE_HASH:
        raise SystemExit(
            f"source hash mismatch: expected {EXPECTED_SOURCE_HASH}, found {snapshot.get('source_hash')}"
        )

    rows = [json.loads(line) for line in snapshot["source"].splitlines() if line.strip()]
    by_id = {row[1]: row for row in rows if len(row) > 1 and isinstance(row[1], str)}
    missing = (set(REPLACEMENTS) | REMOVE_IDS) - set(by_id)
    if missing:
        raise SystemExit(f"repair ids missing from snapshot: {sorted(missing)}")
    if by_id["e14428"][4] != "U2-PWR":
        raise SystemExit("Captain's U2-PWR designator is not present in the snapshot")
    if by_id["e14555"][2] != [[690, 1080, 775, 1080], [775, 1080, 775, 1105]]:
        raise SystemExit("unexpected pre-repair 5V_PROTECTED cursor-tail geometry")
    if by_id["e14561"][2] != [[690, 1060, 775, 1060], [775, 1060, 775, 1065], [775, 1070, 775, 1065], [775, 1070, 690, 1070], [825, 1115, 825, 1065], [825, 1065, 775, 1065]]:
        raise SystemExit("unexpected pre-repair 5V_SYS cursor-tail geometry")

    changed_ids: list[str] = []
    output_rows: list[list[object]] = []
    for row in rows:
        row_id = row[1] if len(row) > 1 and isinstance(row[1], str) else None
        if row_id in REMOVE_IDS:
            changed_ids.append(row_id)
            continue
        if row_id in REPLACEMENTS:
            output_rows.append(REPLACEMENTS[row_id])
            changed_ids.append(row_id)
        else:
            output_rows.append(row)

    if set(changed_ids) != set(REPLACEMENTS) | REMOVE_IDS:
        raise SystemExit("repair did not touch exactly the declared record set")
    if sum(row[0] == "RECT" for row in output_rows) != 10:
        raise SystemExit("Captain's ten rectangles were not preserved")
    designators = [row[4] for row in output_rows if row[0] == "ATTR" and len(row) > 4 and row[3] == "Designator"]
    if len(designators) != 21 or any(not ref.endswith("-PWR") for ref in designators):
        raise SystemExit(f"expected 21 -PWR designators, found {designators}")

    desired_source = "\n".join(json.dumps(row, separators=(",", ":")) for row in output_rows)
    payload = {
        "source": desired_source,
        "expectedSourceHash": snapshot["source_hash"],
        "expectedDocumentUuid": DOCUMENT_UUID,
        "skipConfirmation": True,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"OUTPUT={args.output}")
    print(f"CHANGED_RECORDS={len(changed_ids)}")
    print(f"RECTANGLES={sum(row[0] == 'RECT' for row in output_rows)}")
    print(f"COMPONENTS={sum(row[0] == 'COMPONENT' for row in output_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
