#!/usr/bin/env python3
"""Repair the canonical 5 V to 3.3 V TPS62913 circuit as one visual transaction."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from execute_canonical_container import JOBS, PAGE, PROJECT, SNAPSHOTS, load_fixture_executor


TX = "canonical-power-buck-electrical-repair-2026-08-28"
PIDS_PATH = JOBS / "container-2-pids.json"
INDUCTOR_DEVICE = "18344e62735d41d9b5d16655a0354a82"  # XGL4030-222MEC / C6616463
CAP_DEVICE = "5ad32f6891c644b1a27268ae1b8659ab"  # GRM155R71C104KA88D


def component_records(source: str) -> dict[str, dict]:
    components: dict[str, dict] = {}
    designators: dict[str, str] = {}
    for line in source.splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, list) or not record:
            continue
        if record[0] == "COMPONENT" and len(record) >= 6:
            components[str(record[1])] = {
                "primitive_id": str(record[1]),
                "library_name": str(record[2]),
                "x": float(record[3]),
                "y": float(record[4]),
                "rotation": float(record[5]),
            }
        elif record[0] == "ATTR" and len(record) >= 5 and record[3] == "Designator":
            designators[str(record[4])] = str(record[2])
    return {designator: components[pid] for designator, pid in designators.items() if pid in components}


def main() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    base.validate_repository_state(base.MUTATION_STATE, base.MUTATION_LEDGER)
    before = base.source_snapshot()
    records = component_records(before["source"])
    required = ["U3-PWR2", "L1-PWR2", "C10-PWR2"]
    missing = [ref for ref in required if ref not in records]
    if missing:
        raise SystemExit(f"missing canonical buck components: {missing}")

    old_l1 = records["L1-PWR2"]
    old_c10 = records["C10-PWR2"]
    snapshot_path = SNAPSHOTS / f"{TX}-before.json"
    snapshot_path.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")
    intended = (
        "Correct the TPS62913 5 V to 3.3 V circuit in domain box 2: replace L1 with a "
        "2.2 uH XGL4030-222MEC, replace C10 with 100 nF, and connect VO to 3V3, "
        "PSNS to GND and S-CONF to 5V_SYS"
    )
    base.begin_transaction(
        base.MUTATION_STATE,
        base.MUTATION_LEDGER,
        transaction_id=TX,
        project_uuid=PROJECT,
        document_uuid=PAGE,
        scope="POWER_BUCK",
        stage="repair",
        kind="normal",
        intended_delta=intended,
        snapshot_path=snapshot_path,
        expected_checks=[
            "L1-PWR2 is present exactly once and reads 2.2uH",
            "C10-PWR2 is present exactly once and reads 100nF",
            "U3-PWR2 shows 3V3 at VO, GND at PSNS and 5V_SYS at S-CONF",
            "box 2 remains readable with no overlap duplicate or unrelated movement",
        ],
    )

    jobs = [
        {"tool": "delete_schematic_component", "tag": "delete-old-l1", "args": {
            "primitiveId": old_l1["primitive_id"], "saveAfter": False,
            "expectedDocumentUuid": PAGE}},
        {"tool": "delete_schematic_component", "tag": "delete-old-c10", "args": {
            "primitiveId": old_c10["primitive_id"], "saveAfter": False,
            "expectedDocumentUuid": PAGE}},
        {"tool": "add_schematic_component", "tag": "L1", "args": {
            "deviceUuid": INDUCTOR_DEVICE, "x": old_l1["x"], "y": old_l1["y"],
            "rotation": old_l1["rotation"], "addIntoBom": True, "addIntoPcb": True,
            "saveAfter": False, "expectedDocumentUuid": PAGE}},
        {"tool": "add_schematic_component", "tag": "C10", "args": {
            "deviceUuid": CAP_DEVICE, "x": old_c10["x"], "y": old_c10["y"],
            "rotation": old_c10["rotation"], "addIntoBom": True, "addIntoPcb": True,
            "saveAfter": False, "expectedDocumentUuid": PAGE}},
    ]
    pids = base.extract_pids(base.run_batch(jobs, "canonical-power-buck-replace"))
    if not all(tag in pids for tag in ("L1", "C10")):
        raise SystemExit(f"replacement primitive IDs missing: {pids}")

    existing = json.loads(PIDS_PATH.read_text())
    existing.update({"L1": pids["L1"], "C10": pids["C10"]})
    PIDS_PATH.write_text(json.dumps(existing, indent=2, sort_keys=True) + "\n")

    base.run_batch([
        {"tool": "modify_schematic_component", "tag": "L1", "args": {
            "primitiveId": pids["L1"], "designator": "L1-PWR2", "name": "2.2uH",
            "manufacturer": "Coilcraft", "manufacturerId": "XGL4030-222MEC",
            "supplier": "LCSC", "supplierId": "C6616463", "addIntoBom": True,
            "addIntoPcb": True, "saveAfter": False, "expectedDocumentUuid": PAGE}},
        {"tool": "modify_schematic_component", "tag": "C10", "args": {
            "primitiveId": pids["C10"], "designator": "C10-PWR2", "name": "100nF",
            "manufacturer": "Murata", "manufacturerId": "GRM155R71C104KA88D",
            "addIntoBom": True, "addIntoPcb": True, "saveAfter": False,
            "expectedDocumentUuid": PAGE}},
    ], "canonical-power-buck-designate")

    base.run_batch([
        {"tool": "connect_schematic_pins_to_nets", "tag": "L1", "args": {
            "componentPrimitiveId": pids["L1"], "connections": [
                {"pinNumber": "1", "net": "BUCK_SW"}, {"pinNumber": "2", "net": "3V3"}],
            "saveAfter": False, "expectedDocumentUuid": PAGE}},
        {"tool": "connect_schematic_pins_to_nets", "tag": "C10", "args": {
            "componentPrimitiveId": pids["C10"], "connections": [
                {"pinNumber": "1", "net": "BUCK_SS"}, {"pinNumber": "2", "net": "GND"}],
            "saveAfter": False, "expectedDocumentUuid": PAGE}},
        {"tool": "connect_schematic_pins_to_nets", "tag": "U3", "args": {
            "componentPrimitiveId": records["U3-PWR2"]["primitive_id"], "connections": [
                {"pinNumber": "3", "net": "3V3"},
                {"pinNumber": "7", "net": "GND"},
                {"pinNumber": "10", "net": "5V_SYS"}],
            "saveAfter": True, "expectedDocumentUuid": PAGE}},
    ], "canonical-power-buck-wire")
    if base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE}).get("saved") is not True:
        raise SystemExit("explicit canonical save was not confirmed")

    after = base.source_snapshot()
    reread = component_records(after["source"])
    for designator, expected_name in (("L1-PWR2", "2.2uH"), ("C10-PWR2", "100nF")):
        if designator not in reread:
            raise SystemExit(f"{designator} missing after repair")
        if after["source"].count(f'\"Designator\",\"{designator}\"') != 1:
            raise SystemExit(f"{designator} is not unique after repair")
        if f'\"Name\",\"{expected_name}\"' not in after["source"]:
            raise SystemExit(f"{designator} name {expected_name} missing after repair")

    readback = base.run_batch([
        {"tool": "list_schematic_component_pins", "tag": tag, "args": {
            "componentPrimitiveId": pid, "expectedDocumentUuid": PAGE}}
        for tag, pid in (("U3", records["U3-PWR2"]["primitive_id"]),
                         ("L1", pids["L1"]), ("C10", pids["C10"]))
    ], "canonical-power-buck-readback")
    semantic_path = JOBS / f"{TX}-semantic.json"
    semantic_path.write_text(json.dumps({
        "schema_version": 1, "transaction_id": TX, "project_uuid": PROJECT,
        "document_uuid": PAGE, "scope": "POWER_BUCK", "stage": "repair",
        "intended_delta": intended, "pre_source_hash": before["source_hash"],
        "post_source_hash": after["source_hash"], "saved": True,
        "affected": ["U3-PWR2", "L1-PWR2", "C10-PWR2"],
        "replacement_primitive_ids": pids, "pin_readback": readback,
        "census": after["census"],
    }, indent=2, sort_keys=True) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic_path)
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"SEMANTIC={semantic_path}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
