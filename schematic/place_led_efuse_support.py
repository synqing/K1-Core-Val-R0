#!/usr/bin/env python3
"""Place the minimal TI-supported LED eFuse dVdt support and correct ILM tuning."""
from __future__ import annotations

import json
import sys

from execute_canonical_container import JOBS, PAGE, PROJECT, SNAPSHOTS, load_fixture_executor
from repair_power_buck import component_records


TX = "canonical-led-efuse-support-place-2026-08-28"
C68_DEVICE = "d035f356c56945668c9534741df47111"


def main() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    base.validate_repository_state(base.MUTATION_STATE, base.MUTATION_LEDGER)
    before = base.source_snapshot()
    live = component_records(before["source"])
    for ref in ("U4-PWR2", "R8-PWR2"):
        if ref not in live:
            raise SystemExit(f"missing {ref}")
    if "C68-PWR2" in live:
        raise SystemExit("C68-PWR2 already exists")
    snapshot = SNAPSHOTS / f"{TX}-before.json"
    snapshot.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")
    intended = "Place C68-PWR2 2.2nF for LED eFuse dVdt and correct R8-PWR2 ILM tuning to 3.48k (~0.96 A)"
    base.begin_transaction(
        base.MUTATION_STATE, base.MUTATION_LEDGER, transaction_id=TX,
        project_uuid=PROJECT, document_uuid=PAGE, scope="POWER_LED", stage="place",
        kind="normal", intended_delta=intended, snapshot_path=snapshot,
        expected_checks=[
            "C68-PWR2 appears exactly once inside box 2",
            "C68-PWR2 reads 2.2nF and R8-PWR2 reads 3.48k",
            "neither part overlaps U4 or another box-2 component",
            "the box border title and unrelated components remain unchanged",
        ],
    )
    placed = base.extract_pids(base.run_batch([
        {"tool": "add_schematic_component", "tag": "C68", "args": {
            "deviceUuid": C68_DEVICE, "x": 1615, "y": 3900, "rotation": 0,
            "addIntoBom": True, "addIntoPcb": True, "saveAfter": False,
            "expectedDocumentUuid": PAGE}},
    ], "canonical-led-efuse-support-place"))
    if "C68" not in placed:
        raise SystemExit("C68 primitive ID missing")
    base.run_batch([
        {"tool": "modify_schematic_component", "tag": "C68", "args": {
            "primitiveId": placed["C68"], "designator": "C68-PWR2", "name": "2.2nF",
            "manufacturerId": "GRM155R71H222KA01D", "supplier": "LCSC",
            "supplierId": "C77022", "addIntoBom": True, "addIntoPcb": True,
            "saveAfter": False, "expectedDocumentUuid": PAGE}},
        {"tool": "modify_schematic_component", "tag": "R8", "args": {
            "primitiveId": live["R8-PWR2"]["primitive_id"], "designator": "R8-PWR2",
            "name": "3.48k", "manufacturerId": "RC0402FR-073K48L", "supplier": "LCSC",
            "supplierId": "C185418", "addIntoBom": True, "addIntoPcb": True,
            "saveAfter": True, "expectedDocumentUuid": PAGE}},
    ], "canonical-led-efuse-support-designate")
    if base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE}).get("saved") is not True:
        raise SystemExit("explicit canonical save was not confirmed")
    after = base.source_snapshot()
    reread = component_records(after["source"])
    if reread.get("C68-PWR2", {}).get("primitive_id") != placed["C68"]:
        raise SystemExit("C68-PWR2 read-back mismatch")
    if after["source"].count('\"Designator\",\"C68-PWR2\"') != 1:
        raise SystemExit("C68-PWR2 is not unique")
    semantic = JOBS / f"{TX}-semantic.json"
    semantic.write_text(json.dumps({
        "schema_version": 1, "transaction_id": TX, "project_uuid": PROJECT,
        "document_uuid": PAGE, "scope": "POWER_LED", "stage": "place",
        "intended_delta": intended, "pre_source_hash": before["source_hash"],
        "post_source_hash": after["source_hash"], "saved": True,
        "affected": ["R8-PWR2", "C68-PWR2"], "primitive_ids": placed,
        "census": after["census"],
    }, indent=2, sort_keys=True) + "\n")
    (JOBS / "led-efuse-support-pids.json").write_text(json.dumps(placed, indent=2) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic)
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"SEMANTIC={semantic}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
