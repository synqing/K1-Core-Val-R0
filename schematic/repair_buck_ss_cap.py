#!/usr/bin/env python3
"""Wire the TPS62913 soft-start capacitor C10-PWR2 as one visual transaction."""
from __future__ import annotations

import json
import sys

from execute_canonical_container import JOBS, PAGE, PROJECT, SNAPSHOTS, load_fixture_executor
from repair_power_buck import component_records


TX = "canonical-power-buck-ss-cap-wire-2026-08-28"
INTENDED = (
    "Wire C10-PWR2 as the TPS62913 NR/SS capacitor: pin 1 to BUCK_SS, pin 2 to GND. "
    "Do not move parts or change any other net."
)


def main() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    base.validate_repository_state(base.MUTATION_STATE, base.MUTATION_LEDGER)
    before = base.source_snapshot()
    records = component_records(before["source"])
    if "C10-PWR2" not in records or "U3-PWR2" not in records:
        raise SystemExit("C10-PWR2 or U3-PWR2 missing")
    c10 = records["C10-PWR2"]
    snapshot_path = SNAPSHOTS / f"{TX}-before.json"
    snapshot_path.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")

    base.begin_transaction(
        base.MUTATION_STATE,
        base.MUTATION_LEDGER,
        transaction_id=TX,
        project_uuid=PROJECT,
        document_uuid=PAGE,
        scope="POWER_BUCK",
        stage="wire",
        kind="normal",
        intended_delta=INTENDED,
        snapshot_path=snapshot_path,
        expected_checks=[
            "C10-PWR2 pin 1 is on BUCK_SS",
            "C10-PWR2 pin 2 is on GND",
            "U3-PWR2 NR/SS remains on BUCK_SS",
            "No other designator is added, removed or renamed",
        ],
    )

    base.run_batch([
        {
            "tool": "connect_schematic_pins_to_nets",
            "tag": "C10",
            "args": {
                "componentPrimitiveId": c10["primitive_id"],
                "connections": [
                    {"pinNumber": "1", "net": "BUCK_SS"},
                    {"pinNumber": "2", "net": "GND"},
                ],
                "saveAfter": True,
                "expectedDocumentUuid": PAGE,
            },
        }
    ], f"{TX}-wire")
    if base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE}).get("saved") is not True:
        raise SystemExit("explicit canonical save was not confirmed")

    after = base.source_snapshot()
    if after["census"]["components"] != before["census"]["components"]:
        raise SystemExit("component census changed")
    reread = component_records(after["source"])
    if "C10-PWR2" not in reread:
        raise SystemExit("C10-PWR2 missing after wire")

    readback = base.run_batch([
        {
            "tool": "list_schematic_component_pins",
            "tag": tag,
            "args": {
                "componentPrimitiveId": reread[designator]["primitive_id"],
                "expectedDocumentUuid": PAGE,
            },
        }
        for tag, designator in (("C10", "C10-PWR2"), ("U3", "U3-PWR2"))
    ], f"{TX}-readback")

    semantic_path = JOBS / f"{TX}-semantic.json"
    semantic_path.write_text(json.dumps({
        "schema_version": 1,
        "transaction_id": TX,
        "project_uuid": PROJECT,
        "document_uuid": PAGE,
        "scope": "POWER_BUCK",
        "stage": "wire",
        "intended_delta": INTENDED,
        "pre_source_hash": before["source_hash"],
        "post_source_hash": after["source_hash"],
        "saved": True,
        "affected": ["C10-PWR2", "U3-PWR2"],
        "c10_primitive_id": c10["primitive_id"],
        "pin_readback": readback,
        "census": {k: after["census"][k] for k in ("components", "wires", "texts", "rectangles")},
        "source_basis": [
            "TI TPS62913 datasheet SLUSEA4 NR/SS capacitor",
            "FIXTURE-PLAN C10 role buck_ss",
            "Captain schDrcLog 2026-08-28 BUCK_SS single-pin + C10-PWR2 floating",
        ],
    }, indent=2, sort_keys=True) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic_path)
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"SEMANTIC={semantic_path}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
