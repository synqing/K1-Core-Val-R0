#!/usr/bin/env python3
"""Repair the rejected USB eFuse support placement by containing it in box 1."""
from __future__ import annotations

import json
import sys

from execute_canonical_container import JOBS, PAGE, PROJECT, SNAPSHOTS, load_fixture_executor
from repair_power_buck import component_records


REJECTED = "canonical-usb-efuse-support-place-2026-08-28"
TX = "canonical-usb-efuse-support-layout-repair-2026-08-28"
POSITIONS = {
    "R63-PWR1": (150, 3800),
    "R2-PWR1": (300, 3800),
    "R64-PWR1": (450, 3800),
    "R65-PWR1": (600, 3800),
    "R66-PWR1": (750, 3800),
    "R67-PWR1": (600, 3700),
    "C67-PWR1": (750, 3700),
}


def main() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    base.validate_repository_state(base.MUTATION_STATE, base.MUTATION_LEDGER)
    before = base.source_snapshot()
    live = component_records(before["source"])
    missing = [ref for ref in POSITIONS if ref not in live]
    if missing:
        raise SystemExit(f"support components missing before repair: {missing}")
    snapshot = SNAPSHOTS / f"{TX}-before.json"
    snapshot.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")
    intended = (
        "Repair rejected PWR1 support placement by moving the complete threshold, PG and dVdt "
        "network into the empty lower area of box 1 within x=0..910"
    )
    base.begin_transaction(
        base.MUTATION_STATE, base.MUTATION_LEDGER, transaction_id=TX,
        project_uuid=PROJECT, document_uuid=PAGE, scope="POWER_ENTRY", stage="move",
        kind="repair", repairs_transaction_id=REJECTED, intended_delta=intended,
        snapshot_path=snapshot, expected_checks=[
            "all seven support parts are visibly inside box 1",
            "the support parts form two tidy rows with readable labels",
            "no component overlaps another component or the box border",
            "boxes 2 through 10 and unrelated box-1 components remain unmoved",
        ],
    )
    jobs = []
    for index, (ref, (x, y)) in enumerate(POSITIONS.items()):
        jobs.append({"tool": "modify_schematic_component", "tag": ref, "args": {
            "primitiveId": live[ref]["primitive_id"], "x": x, "y": y,
            "saveAfter": index == len(POSITIONS) - 1, "expectedDocumentUuid": PAGE}})
    base.run_batch(jobs, "canonical-usb-efuse-support-layout-repair")
    if base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE}).get("saved") is not True:
        raise SystemExit("explicit canonical save was not confirmed")
    after = base.source_snapshot()
    reread = component_records(after["source"])
    wrong = {ref: reread.get(ref) for ref, (x, y) in POSITIONS.items()
             if reread.get(ref, {}).get("x") != x or reread.get(ref, {}).get("y") != y}
    if wrong:
        raise SystemExit(f"support position read-back mismatch: {wrong}")
    semantic = JOBS / f"{TX}-semantic.json"
    semantic.write_text(json.dumps({
        "schema_version": 1, "transaction_id": TX, "project_uuid": PROJECT,
        "document_uuid": PAGE, "scope": "POWER_ENTRY", "stage": "move",
        "intended_delta": intended, "pre_source_hash": before["source_hash"],
        "post_source_hash": after["source_hash"], "saved": True,
        "affected": list(POSITIONS), "positions": POSITIONS, "census": after["census"],
    }, indent=2, sort_keys=True) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic)
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"SEMANTIC={semantic}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
