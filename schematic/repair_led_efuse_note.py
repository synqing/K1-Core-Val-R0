#!/usr/bin/env python3
"""Centre the clipped LED eFuse settings note inside box 2."""
from __future__ import annotations

import argparse
import json
import sys

from execute_canonical_container import JOBS, PAGE, PROJECT, SNAPSHOTS, load_fixture_executor
from wire_led_efuse_support import NOTE


REJECTED = "canonical-led-efuse-support-wire-2026-08-28"
TX = "canonical-led-efuse-note-anchor-repair-2026-08-28"
PAYLOAD = JOBS / f"{TX}-payload.json"
TARGET = [1435, 3645]


def rows(source: str) -> list[list]:
    return [json.loads(line) for line in source.splitlines() if line.strip()]


def prepare() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    base.validate_repository_state(base.MUTATION_STATE, base.MUTATION_LEDGER)
    before = base.source_snapshot()
    snapshot = SNAPSHOTS / f"{TX}-before.json"
    snapshot.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")
    intended = "Repair the clipped box-2 LED eFuse settings note by centring it at x=1435 y=3645"
    base.begin_transaction(
        base.MUTATION_STATE, base.MUTATION_LEDGER, transaction_id=TX,
        project_uuid=PROJECT, document_uuid=PAGE, scope="POWER_LED", stage="text",
        kind="repair", repairs_transaction_id=REJECTED, intended_delta=intended,
        snapshot_path=snapshot, expected_checks=[
            "the complete note begins with U4 SET and ends with ITIMER NC inside box 2",
            "the note remains clear of symbols, nets and the lower border",
            "the electrical source and component count do not change",
            "the whole canvas remains modal-free and unchanged outside the note",
        ],
    )
    all_rows = rows(before["source"])
    notes = [record for record in all_rows if record[0] == "TEXT" and len(record) > 5 and record[5] == NOTE]
    if len(notes) != 1:
        raise SystemExit(f"expected one LED eFuse note, found {len(notes)}")
    notes[0][2:4] = TARGET
    payload = {
        "source": "\n".join(json.dumps(record, separators=(",", ":")) for record in all_rows),
        "expectedSourceHash": before["source_hash"],
        "expectedDocumentUuid": PAGE,
        "skipConfirmation": True,
    }
    PAYLOAD.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"PRE_SOURCE_HASH={before['source_hash']}")
    print(f"PAYLOAD={PAYLOAD}")
    return 0


def record() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    before = json.loads((SNAPSHOTS / f"{TX}-before.json").read_text())
    after = base.source_snapshot()
    notes = [record for record in rows(after["source"])
             if record[0] == "TEXT" and len(record) > 5 and record[5] == NOTE]
    if len(notes) != 1 or notes[0][2:4] != TARGET:
        raise SystemExit(f"LED eFuse note read-back mismatch: {notes}")
    if before["census"]["components"] != after["census"]["components"]:
        raise SystemExit("LED eFuse note repair changed component count")
    if before["census"]["net_counts"] != after["census"]["net_counts"]:
        raise SystemExit("LED eFuse note repair changed endpoint net counts")
    semantic = JOBS / f"{TX}-semantic.json"
    semantic.write_text(json.dumps({
        "schema_version": 1, "transaction_id": TX, "project_uuid": PROJECT,
        "document_uuid": PAGE, "scope": "POWER_LED", "stage": "text",
        "intended_delta": "Repair the clipped box-2 LED eFuse settings note by centring it at x=1435 y=3645",
        "pre_source_hash": before["source_hash"], "post_source_hash": after["source_hash"],
        "saved": True, "affected": ["LED eFuse settings note"],
        "note_position": TARGET, "census": after["census"],
    }, indent=2, sort_keys=True) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic)
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"SEMANTIC={semantic}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "record"))
    args = parser.parse_args()
    return prepare() if args.action == "prepare" else record()


if __name__ == "__main__":
    sys.exit(main())
