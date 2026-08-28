#!/usr/bin/env python3
"""Place, designate or wire one source-derived pull-up as one visual transaction.

pg     — TPS62913 Power Good to 3V3 via R75-PWR2 (TI SLUSEA4 open-drain PG).
i2c_en — ST25R3916B I2C_EN high strap via R76-NFC (I2C mode, not NC).
"""
from __future__ import annotations

import json
import sys

from execute_canonical_container import JOBS, PAGE, PROJECT, SNAPSHOTS, load_fixture_executor
from repair_power_buck import component_records


RES_DEVICE = "6593321c1e554b2f9070c57621ba8753"
RES_MPN = "RC0402FR-0710KL"
RES_LCSC = "C60490"

CIRCUITS = {
    "pg": {
        "tx": "canonical-power-buck-pg-pullup-{stage}-2026-08-28",
        "scope": "POWER_BUCK",
        "ref": "R75",
        "designator": "R75-PWR2",
        "x": 1020,
        "y": 4480,
        "net": "BUCK_PG",
        "ic": "U3-PWR2",
        "ic_pin": "5",
        "rail": "3V3",
        "clear_ic_nc": True,
        "intended": {
            "place": (
                "Place RC0402FR-0710KL 10k R75-PWR2 in box 2 left of U3-PWR2, "
                "near the TPS62913 PG pin. Do not designate or wire."
            ),
            "designate": (
                "Designate R75-PWR2 as 10k RC0402FR-0710KL / C60490. "
                "Do not move or wire."
            ),
            "wire": (
                "Wire R75-PWR2 pin 1 to BUCK_PG, pin 2 to 3V3, and U3-PWR2 pin 5 "
                "to BUCK_PG. Do not move parts."
            ),
        },
        "checks": {
            "place": [
                "one new 0402 resistor sits in box 2 left of U3",
                "it does not overlap U3, C10 or L1",
                "no part appears outside box 2",
                "component count increases by exactly 1",
            ],
            "designate": [
                "R75-PWR2 exists exactly once",
                "it reads 10k",
                "no extra designator appears",
                "position stays at the placed coordinate",
            ],
            "wire": [
                "R75-PWR2 pin 1 is on BUCK_PG",
                "R75-PWR2 pin 2 is on 3V3",
                "U3-PWR2 pin 5 is on BUCK_PG",
                "census components stay at the post-place count",
            ],
        },
        "basis": [
            "TI TPS62913 datasheet SLUSEA4: PG is open-drain and requires a pull-up when used",
            "K1 validation board uses PG; do not NC it",
            "Captain schDrcLog 2026-08-28 unused-pin hygiene item 2",
        ],
    },
    "i2c_en": {
        "tx": "canonical-nfc-i2c-en-pullup-{stage}-2026-08-28",
        "scope": "NFC",
        "ref": "R76",
        "designator": "R76-NFC",
        "x": 1680,
        "y": 3240,
        "net": "NFC_I2C_EN",
        "ic": "U12-NFC",
        "ic_pin": "20",
        "rail": "3V3",
        "clear_ic_nc": False,
        "intended": {
            "place": (
                "Place RC0402FR-0710KL 10k R76-NFC in box 7 between J10 and U12 "
                "as the ST25R3916B I2C_EN high strap. Do not designate or wire."
            ),
            "designate": (
                "Designate R76-NFC as 10k RC0402FR-0710KL / C60490. "
                "Do not move or wire."
            ),
            "wire": (
                "Wire R76-NFC pin 1 to NFC_I2C_EN, pin 2 to 3V3, and U12-NFC "
                "pin 20 I2C_EN to NFC_I2C_EN. Do not move parts."
            ),
        },
        "checks": {
            "place": [
                "one new 0402 resistor sits in box 7 between J10 and U12",
                "it does not overlap U12, J10 or the regulator-cap row",
                "no part appears outside box 7",
                "component count increases by exactly 1",
            ],
            "designate": [
                "R76-NFC exists exactly once",
                "it reads 10k",
                "no extra designator appears",
                "position stays at the placed coordinate",
            ],
            "wire": [
                "R76-NFC pin 1 is on NFC_I2C_EN",
                "R76-NFC pin 2 is on 3V3",
                "U12-NFC pin 20 is on NFC_I2C_EN",
                "census components stay at the post-place count",
            ],
        },
        "basis": [
            "ST25R3916B: I2C_EN high selects I2C; floating is not a valid strap",
            "FIXTURE-PLAN uses I2C_SDA/SCL, so I2C_EN must be held high",
            "Captain schDrcLog 2026-08-28 listed U12-NFC.20 as floating",
        ],
    },
}


def _args() -> tuple[str, str]:
    if len(sys.argv) != 3 or sys.argv[1] not in CIRCUITS or sys.argv[2] not in {"place", "designate", "wire"}:
        raise SystemExit("usage: repair_pullup.py pg|i2c_en place|designate|wire")
    return sys.argv[1], sys.argv[2]


def main() -> int:
    circuit_id, stage = _args()
    spec = CIRCUITS[circuit_id]
    tx = spec["tx"].format(stage=stage)
    intended = spec["intended"][stage]
    checks = spec["checks"][stage]
    designator = spec["designator"]
    ref = spec["ref"]

    base = load_fixture_executor()
    base.assert_identity()
    base.validate_repository_state(base.MUTATION_STATE, base.MUTATION_LEDGER)
    before = base.source_snapshot()
    live = component_records(before["source"])
    if spec["ic"] not in live:
        raise SystemExit(f"{spec['ic']} missing")
    pids_path = JOBS / f"{circuit_id}-pullup-pids.json"
    if stage == "place":
        if designator in live:
            raise SystemExit(f"{designator} already exists")
    elif stage == "designate":
        if not pids_path.exists():
            raise SystemExit(f"{pids_path.name} missing")
        if designator in live:
            raise SystemExit(f"{designator} already designated")
    elif designator not in live:
        raise SystemExit(f"{designator} missing")

    snapshot = SNAPSHOTS / f"{tx}-before.json"
    snapshot.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")
    base.begin_transaction(
        base.MUTATION_STATE,
        base.MUTATION_LEDGER,
        transaction_id=tx,
        project_uuid=PROJECT,
        document_uuid=PAGE,
        scope=spec["scope"],
        stage=stage,
        kind="normal",
        intended_delta=intended,
        snapshot_path=snapshot,
        expected_checks=checks,
    )

    if stage == "place":
        jobs = [
            {
                "tool": "add_schematic_component",
                "tag": ref,
                "args": {
                    "deviceUuid": RES_DEVICE,
                    "x": spec["x"],
                    "y": spec["y"],
                    "rotation": 0,
                    "addIntoBom": True,
                    "addIntoPcb": True,
                    "saveAfter": True,
                    "expectedDocumentUuid": PAGE,
                },
            }
        ]
        placed = base.extract_pids(base.run_batch(jobs, f"{tx}-place"))
        if ref not in placed:
            raise SystemExit(f"place pid missing {placed}")
        pids_path.write_text(json.dumps(placed, indent=2) + "\n")
        affected = [placed[ref]]
    elif stage == "designate":
        placed = json.loads(pids_path.read_text())
        jobs = [
            {
                "tool": "modify_schematic_component",
                "tag": ref,
                "args": {
                    "primitiveId": placed[ref],
                    "designator": designator,
                    "name": "10k",
                    "manufacturerId": RES_MPN,
                    "supplier": "LCSC",
                    "supplierId": RES_LCSC,
                    "addIntoBom": True,
                    "addIntoPcb": True,
                    "saveAfter": True,
                    "expectedDocumentUuid": PAGE,
                },
            }
        ]
        base.run_batch(jobs, f"{tx}-designate")
        affected = [designator]
    else:
        jobs = []
        if spec.get("clear_ic_nc"):
            jobs.append({
                "tool": "set_schematic_pin_no_connect",
                "tag": f"{spec['ic']}-clear-nc",
                "args": {
                    "componentPrimitiveId": live[spec["ic"]]["primitive_id"],
                    "pinNumber": spec["ic_pin"],
                    "noConnected": False,
                    "saveAfter": False,
                    "expectedDocumentUuid": PAGE,
                },
            })
        jobs.extend([
            {
                "tool": "connect_schematic_pins_to_nets",
                "tag": ref,
                "args": {
                    "componentPrimitiveId": live[designator]["primitive_id"],
                    "connections": [
                        {"pinNumber": "1", "net": spec["net"]},
                        {"pinNumber": "2", "net": spec["rail"]},
                    ],
                    "saveAfter": False,
                    "expectedDocumentUuid": PAGE,
                },
            },
            {
                "tool": "connect_schematic_pins_to_nets",
                "tag": spec["ic"],
                "args": {
                    "componentPrimitiveId": live[spec["ic"]]["primitive_id"],
                    "connections": [
                        {"pinNumber": spec["ic_pin"], "net": spec["net"]},
                    ],
                    "saveAfter": True,
                    "expectedDocumentUuid": PAGE,
                },
            },
        ])
        base.run_batch(jobs, f"{tx}-wire")
        affected = [designator, spec["ic"]]

    if base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE}).get("saved") is not True:
        raise SystemExit("explicit canonical save was not confirmed")

    after = base.source_snapshot()
    reread = component_records(after["source"])
    if stage != "place" and designator not in reread:
        raise SystemExit(f"{designator} missing after {stage}")
    if after["source_hash"] == before["source_hash"]:
        raise SystemExit("source hash did not change")

    semantic = JOBS / f"{tx}-semantic.json"
    semantic.write_text(json.dumps({
        "schema_version": 1,
        "transaction_id": tx,
        "project_uuid": PROJECT,
        "document_uuid": PAGE,
        "scope": spec["scope"],
        "stage": stage,
        "intended_delta": intended,
        "pre_source_hash": before["source_hash"],
        "post_source_hash": after["source_hash"],
        "saved": True,
        "affected": affected,
        "census": {k: after["census"][k] for k in ("components", "wires", "texts", "rectangles")},
        "source_basis": spec["basis"],
    }, indent=2, sort_keys=True) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic)
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"CENSUS={after['census']['components']}/{after['census']['wires']}")
    print(f"SEMANTIC={semantic}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
