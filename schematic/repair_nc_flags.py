#!/usr/bin/env python3
"""Mark unused pins with the EasyEDA No Connect cross, one domain at a time."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from execute_canonical_container import JOBS, PAGE, PROJECT, SNAPSHOTS, load_fixture_executor
from repair_power_buck import component_records


REPO = Path("/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0")
APPLY = REPO / "harness/easyeda_set_pin_noconnect.mjs"

GROUPS = {
    "nfc": {
        "tx": "canonical-nfc-unused-nc-2026-08-28",
        "scope": "NFC",
        "pins": {
            "U12-NFC": ["2", "17", "18", "19", "25", "28", "29", "31"],
        },
        "intended": (
            "Mark unused ST25R3916B pins with the No Connect cross in box 7: "
            "TAD2, EXT_LM, AAT_A, AAT_B, TAD1, MCU_CLK, BSS and MOSI. "
            "Do not mark RFO2, RFI2 or I2C_EN."
        ),
        "checks": [
            "unused U12 pins show the NC cross",
            "I2C_EN RFO2 and RFI2 stay unmarked",
            "R76-NFC wiring is untouched",
            "census component count stays 230",
        ],
        "basis": [
            "ST25R3916B I2C mode leaves MOSI, BSS, MCU_CLK, TAD and AAT unused",
            "EasyEDA No Connect is the pin NO_CONNECT attr / green cross",
            "Captain unused-pin hygiene item 3",
        ],
    },
    "switch_sbu": {
        "tx": "canonical-switch-sbu-nc-2026-08-28",
        "scope": "HYGIENE",
        "pins": {
            "J7-ESP": ["A8", "B8"],
            "SW1-RTC": ["3", "4"],
            "SW2-ESP": ["3", "4"],
            "SW3-ESP": ["3", "4"],
            "SW4-VAL": ["3", "4"],
        },
        "intended": (
            "Mark unused switch throws and USB-C SBU pins with the No Connect cross. "
            "Do not mark power or used UART/CC pins."
        ),
        "checks": [
            "SW1-SW4 pins 3 and 4 show NC crosses",
            "J7-ESP A8 and B8 show NC crosses",
            "used switch and USB pins stay wired",
            "census component count stays 230",
        ],
        "basis": [
            "4-pin switches use only one throw pair",
            "USB-C SBU1/SBU2 are unused on this board",
            "Captain unused-pin hygiene item 3",
        ],
    },
}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in GROUPS:
        raise SystemExit("usage: repair_nc_flags.py nfc|switch_sbu")
    group_id = sys.argv[1]
    spec = GROUPS[group_id]
    tx = spec["tx"]

    base = load_fixture_executor()
    base.assert_identity()
    base.validate_repository_state(base.MUTATION_STATE, base.MUTATION_LEDGER)
    before = base.source_snapshot()
    live = component_records(before["source"])
    requested = []
    for designator, numbers in spec["pins"].items():
        if designator not in live:
            raise SystemExit(f"{designator} missing")
        for number in numbers:
            requested.append({
                "designator": designator,
                "componentPrimitiveId": live[designator]["primitive_id"],
                "pinNumber": number,
                "noConnect": True,
            })

    snapshot = SNAPSHOTS / f"{tx}-before.json"
    snapshot.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")
    base.begin_transaction(
        base.MUTATION_STATE,
        base.MUTATION_LEDGER,
        transaction_id=tx,
        project_uuid=PROJECT,
        document_uuid=PAGE,
        scope=spec["scope"],
        stage="repair",
        kind="normal",
        intended_delta=spec["intended"],
        snapshot_path=snapshot,
        expected_checks=spec["checks"],
    )

    payload = JOBS / f"{tx}-payload.json"
    applied_path = JOBS / f"{tx}-applied.json"
    payload.write_text(json.dumps({"pins": requested, "out": str(applied_path)}, indent=2) + "\n")
    proc = subprocess.run(
        ["node", str(APPLY), str(payload)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        print(proc.stdout[-2000:])
        print(proc.stderr[-2000:])
        raise SystemExit(f"noconnect apply failed rc={proc.returncode}")
    applied = json.loads(applied_path.read_text()) if applied_path.exists() else json.loads(proc.stdout)
    if not applied.get("ok"):
        raise SystemExit(f"noconnect apply rejected: {applied}")
    if not applied.get("applied"):
        raise SystemExit("noconnect apply changed nothing")

    if base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE}).get("saved") is not True:
        raise SystemExit("explicit canonical save was not confirmed")

    after = base.source_snapshot()
    if after["source_hash"] == before["source_hash"]:
        raise SystemExit("source hash did not change")

    semantic = JOBS / f"{tx}-semantic.json"
    semantic.write_text(json.dumps({
        "schema_version": 1,
        "transaction_id": tx,
        "project_uuid": PROJECT,
        "document_uuid": PAGE,
        "scope": spec["scope"],
        "stage": "repair",
        "intended_delta": spec["intended"],
        "pre_source_hash": before["source_hash"],
        "post_source_hash": after["source_hash"],
        "saved": True,
        "affected": [f"{row.get('designator')}.{row.get('pinNumber')}" for row in applied.get("applied", [])],
        "census": {k: after["census"][k] for k in ("components", "wires", "texts", "rectangles")},
        "applied": applied.get("applied"),
        "skipped": applied.get("skipped"),
        "source_basis": spec["basis"],
    }, indent=2, sort_keys=True) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic)
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"CENSUS={after['census']['components']}/{after['census']['wires']}")
    print(f"APPLIED={len(applied.get('applied') or [])}")
    print(f"SKIPPED={len(applied.get('skipped') or [])}")
    print(f"SEMANTIC={semantic}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
