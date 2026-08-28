#!/usr/bin/env python3
"""Guarded repair: restore exact source records from a reference and remove exact current records."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
from easyeda_source_format import require_v2  # V2/V3 serialisation guard



PAGE = "1435cb46f39e48c8a8aadbb84ca81603"


def rows_for(snapshot: dict) -> list[list[object]]:
    require_v2(snapshot["source"], tool="easyeda_repair_source_swap")
    return [json.loads(line) for line in snapshot["source"].splitlines() if line.strip()]


def belongs(row: list[object], ids: set[str]) -> bool:
    record_id = row[1] if len(row) > 1 and isinstance(row[1], str) else None
    parent_id = row[2] if row and row[0] == "ATTR" and len(row) > 2 else None
    return record_id in ids or parent_id in ids


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("current", type=Path)
    ap.add_argument("reference", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--restore", nargs="+", required=True)
    ap.add_argument("--remove", nargs="+", required=True)
    ap.add_argument("--insert-before", required=True)
    args = ap.parse_args()

    current = json.loads(args.current.read_text())
    reference = json.loads(args.reference.read_text())
    if current.get("documentUuid") != PAGE or reference.get("documentUuid") != PAGE:
        raise SystemExit("document identity mismatch")
    restore = set(args.restore)
    remove = set(args.remove)
    if restore & remove:
        raise SystemExit("restore and remove sets overlap")

    current_rows = rows_for(current)
    reference_rows = rows_for(reference)
    current_ids = {row[1] for row in current_rows if len(row) > 1 and isinstance(row[1], str)}
    reference_ids = {row[1] for row in reference_rows if len(row) > 1 and isinstance(row[1], str)}
    if restore & current_ids:
        raise SystemExit(f"restore IDs unexpectedly exist in current source: {sorted(restore & current_ids)}")
    if restore - reference_ids:
        raise SystemExit(f"restore IDs missing from reference: {sorted(restore - reference_ids)}")
    if remove - current_ids:
        raise SystemExit(f"remove IDs missing from current source: {sorted(remove - current_ids)}")

    restored_rows = [row for row in reference_rows if belongs(row, restore)]
    output_rows: list[list[object]] = []
    inserted = False
    for row in current_rows:
        record_id = row[1] if len(row) > 1 and isinstance(row[1], str) else None
        if record_id == args.insert_before and not inserted:
            output_rows.extend(restored_rows)
            inserted = True
        if belongs(row, remove):
            continue
        output_rows.append(row)
    if not inserted:
        raise SystemExit(f"insert anchor missing: {args.insert_before}")

    if sum(row[0] == "RECT" for row in output_rows) != 10:
        raise SystemExit("domain rectangle count changed")
    if sum(row[0] == "COMPONENT" for row in output_rows) != 15:
        raise SystemExit("expected root plus fourteen electrical components")
    if sum(row[0] == "WIRE" for row in output_rows) != 36:
        raise SystemExit("expected thirty-six functional wires after swap")
    designators = [row[4] for row in output_rows if row[0] == "ATTR" and len(row) > 4 and row[3] == "Designator"]
    if len(designators) != 14 or any(str(ref).startswith("CS") for ref in designators):
        raise SystemExit(f"fixture-only designator survived: {designators}")

    payload = {
        "source": "\n".join(json.dumps(row, separators=(",", ":")) for row in output_rows),
        "expectedSourceHash": current["sourceHash"],
        "expectedDocumentUuid": PAGE,
        "skipConfirmation": True,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"RESTORED_ROWS={len(restored_rows)}")
    print(f"REMOVED_RECORDS={len(remove)}")
    print(f"OUTPUT={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
