#!/usr/bin/env python3
"""Build a guarded EasyEDA set_document_source payload for exact record IDs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
from easyeda_source_format import require_v2  # V2/V3 serialisation guard



CANONICAL_PAGE = "1435cb46f39e48c8a8aadbb84ca81603"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--ids", nargs="+")
    parser.add_argument("--type", choices=("WIRE", "TEXT", "RECT", "COMPONENT"))
    parser.add_argument("--records", nargs="+", help="mixed records as TYPE:ID")
    args = parser.parse_args()

    snapshot = json.loads(args.snapshot.read_text())
    document_uuid = snapshot.get("documentUuid") or snapshot.get("document_uuid")
    if document_uuid != CANONICAL_PAGE:
        raise SystemExit(f"wrong document: {document_uuid}")
    source_hash = snapshot.get("sourceHash") or snapshot.get("source_hash")
    if not source_hash:
        raise SystemExit("snapshot is missing sourceHash")

    require_v2(snapshot["source"], tool="easyeda_remove_source_records")

    rows = [json.loads(line) for line in snapshot["source"].splitlines() if line.strip()]
    if args.records:
        expected_types = {}
        for item in args.records:
            record_type, separator, record_id = item.partition(":")
            if not separator or record_type not in {"WIRE", "TEXT", "RECT", "COMPONENT"} or not record_id:
                raise SystemExit(f"invalid --records item: {item}")
            expected_types[record_id] = record_type
    else:
        if not args.ids or not args.type:
            raise SystemExit("use --records TYPE:ID ... or both --type and --ids")
        expected_types = {record_id: args.type for record_id in args.ids}
    wanted = set(expected_types)
    records = {row[1]: row for row in rows if len(row) > 1 and isinstance(row[1], str)}
    missing = wanted - set(records)
    if missing:
        raise SystemExit(f"record IDs not found: {sorted(missing)}")
    wrong_type = {
        record_id: {"expected": expected_types[record_id], "actual": records[record_id][0]}
        for record_id in wanted if records[record_id][0] != expected_types[record_id]
    }
    if wrong_type:
        raise SystemExit(f"record type mismatch: {wrong_type}")

    output_rows = []
    removed = []
    for row in rows:
        record_id = row[1] if len(row) > 1 and isinstance(row[1], str) else None
        parent_id = row[2] if row and row[0] == "ATTR" and len(row) > 2 else None
        if record_id in wanted or parent_id in wanted:
            removed.append(record_id)
            continue
        output_rows.append(row)

    if sum(row[0] == "RECT" for row in output_rows) != 10:
        raise SystemExit("the ten Captain-authored domain rectangles were not preserved")
    initial_components = sum(row[0] == "COMPONENT" for row in rows)
    expected_components = initial_components - sum(record_type == "COMPONENT" for record_type in expected_types.values())
    if sum(row[0] == "COMPONENT" for row in output_rows) != expected_components:
        raise SystemExit("unexpected canonical component count during source repair")
    if any(row[1] in wanted for row in output_rows if len(row) > 1 and isinstance(row[1], str)):
        raise SystemExit("requested source record survived removal")

    payload = {
        "source": "\n".join(json.dumps(row, separators=(",", ":")) for row in output_rows),
        "expectedSourceHash": source_hash,
        "expectedDocumentUuid": CANONICAL_PAGE,
        "skipConfirmation": True,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"SOURCE_HASH={source_hash}")
    print(f"REQUESTED_RECORDS={len(wanted)}")
    print(f"REMOVED_ROWS={len(removed)}")
    print(f"OUTPUT={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
