#!/usr/bin/env python3
"""Place the source-derived USB/input TPS259474L support network in box 1."""
from __future__ import annotations

import json
import sys

from execute_canonical_container import JOBS, PAGE, PROJECT, SNAPSHOTS, load_fixture_executor
from repair_power_buck import component_records


TX = "canonical-usb-efuse-support-place-2026-08-28"
PARTS = {
    "R63": {"device": "a5926b750ba841648b265e220285a203", "x": 800, "y": 4420,
             "name": "1.05M", "mpn": "RC0402FR-071M05L", "supplier": "C477184"},
    "R64": {"device": "b70eff1cd1c44161bba95073d4971133", "x": 1100, "y": 4420,
             "name": "324k", "mpn": "RC0402FR-07324KL", "supplier": "C185426"},
    "R65": {"device": "c9201f77db114454a552303c9321dd4e", "x": 800, "y": 4320,
             "name": "274k", "mpn": "RC0402FR-07274KL", "supplier": "C185435"},
    "R66": {"device": "0cc9cee0c09e4a1c8b41e9d1feefa5b2", "x": 950, "y": 4320,
             "name": "100k", "mpn": "RC0402FR-07100KL", "supplier": ""},
    "R67": {"device": "6593321c1e554b2f9070c57621ba8753", "x": 1100, "y": 4320,
             "name": "10k", "mpn": "RC0402FR-0710KL", "supplier": "C60490"},
    "C67": {"device": "d035f356c56945668c9534741df47111", "x": 1100, "y": 4220,
             "name": "2.2nF", "mpn": "GRM155R71H222KA01D", "supplier": "C77022"},
}


def main() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    base.validate_repository_state(base.MUTATION_STATE, base.MUTATION_LEDGER)
    before = base.source_snapshot()
    live = component_records(before["source"])
    for designator in ("U1-PWR1", "R1-PWR1", "R2-PWR1"):
        if designator not in live:
            raise SystemExit(f"missing required existing component {designator}")
    collisions = [f"{ref}-PWR1" for ref in PARTS if f"{ref}-PWR1" in live]
    if collisions:
        raise SystemExit(f"support components already exist: {collisions}")
    snapshot = SNAPSHOTS / f"{TX}-before.json"
    snapshot.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")
    intended = (
        "Place and identify the complete USB/input eFuse support network in box 1: "
        "2.5 A ILM tuning, UVLO/OVLO ladder, PGTH divider, PG pull-up and dVdt capacitor"
    )
    base.begin_transaction(
        base.MUTATION_STATE, base.MUTATION_LEDGER, transaction_id=TX,
        project_uuid=PROJECT, document_uuid=PAGE, scope="POWER_ENTRY",
        stage="place", kind="normal", intended_delta=intended, snapshot_path=snapshot,
        expected_checks=[
            "six new support parts appear exactly once in box 1",
            "R1-PWR1 reads 1.33k and R2-PWR1 is moved into the threshold ladder",
            "all new designators carry the PWR1 suffix and all values are readable",
            "the box border title and unrelated components remain unchanged without overlap",
        ],
    )
    add_jobs = [
        {"tool": "add_schematic_component", "tag": ref, "args": {
            "deviceUuid": spec["device"], "x": spec["x"], "y": spec["y"], "rotation": 0,
            "addIntoBom": True, "addIntoPcb": True, "saveAfter": False,
            "expectedDocumentUuid": PAGE}}
        for ref, spec in PARTS.items()
    ]
    pids = base.extract_pids(base.run_batch(add_jobs, "canonical-usb-efuse-support-place"))
    if set(pids) != set(PARTS):
        raise SystemExit(f"support placement primitive mismatch: {pids}")
    (JOBS / "usb-efuse-support-pids.json").write_text(json.dumps(pids, indent=2, sort_keys=True) + "\n")

    modify_jobs = []
    for ref, spec in PARTS.items():
        modify_jobs.append({"tool": "modify_schematic_component", "tag": ref, "args": {
            "primitiveId": pids[ref], "designator": f"{ref}-PWR1", "name": spec["name"],
            "manufacturerId": spec["mpn"], "supplier": "LCSC", "supplierId": spec["supplier"],
            "addIntoBom": True, "addIntoPcb": True, "saveAfter": False,
            "expectedDocumentUuid": PAGE}})
    modify_jobs.extend([
        {"tool": "modify_schematic_component", "tag": "R1", "args": {
            "primitiveId": live["R1-PWR1"]["primitive_id"], "designator": "R1-PWR1",
            "name": "1.33k", "manufacturerId": "RC0402FR-071K33L",
            "supplier": "LCSC", "supplierId": "C276261", "addIntoBom": True,
            "addIntoPcb": True, "saveAfter": False, "expectedDocumentUuid": PAGE}},
        {"tool": "modify_schematic_component", "tag": "R2", "args": {
            "primitiveId": live["R2-PWR1"]["primitive_id"], "x": 950, "y": 4420,
            "designator": "R2-PWR1", "name": "100k", "addIntoBom": True,
            "addIntoPcb": True, "saveAfter": True, "expectedDocumentUuid": PAGE}},
    ])
    base.run_batch(modify_jobs, "canonical-usb-efuse-support-designate")
    if base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE}).get("saved") is not True:
        raise SystemExit("explicit canonical save was not confirmed")

    after = base.source_snapshot()
    reread = component_records(after["source"])
    expected_designators = [f"{ref}-PWR1" for ref in PARTS] + ["R1-PWR1", "R2-PWR1"]
    missing = [ref for ref in expected_designators if ref not in reread]
    if missing:
        raise SystemExit(f"support components missing after read-back: {missing}")
    for ref in expected_designators:
        if after["source"].count(f'\"Designator\",\"{ref}\"') != 1:
            raise SystemExit(f"support designator not unique: {ref}")
    semantic = JOBS / f"{TX}-semantic.json"
    semantic.write_text(json.dumps({
        "schema_version": 1, "transaction_id": TX, "project_uuid": PROJECT,
        "document_uuid": PAGE, "scope": "POWER_ENTRY", "stage": "place",
        "intended_delta": intended, "pre_source_hash": before["source_hash"],
        "post_source_hash": after["source_hash"], "saved": True,
        "affected": expected_designators, "primitive_ids": pids, "census": after["census"],
    }, indent=2, sort_keys=True) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic)
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"SEMANTIC={semantic}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
