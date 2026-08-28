#!/usr/bin/env python3
"""ST25R3916B internal-regulator decoupling: six 2.2 µF capacitors to GND.

STEVAL-ST25R3916B uses GRM155R60J225ME15D on the internal rails.
VDD_A / VDD_D / VDD_RF / VDD_AM / VDD_DR / AGDC are regulator outputs —
they must not be driven from NFC_5V or 3V3.
"""
from __future__ import annotations

import json
import sys

from execute_canonical_container import JOBS, PAGE, PROJECT, SNAPSHOTS, load_fixture_executor
from repair_power_buck import component_records


CAP_DEVICE = "7a962641d03c47e8b5f4e029ea26d5a9"
CAP_MPN = "GRM155R60J225ME15D"
CAP_LCSC = "C76993"

# One source-derived row between the matching caps (y=2822) and J10 (y=3108).
CAPS = [
    {"ref": "C92", "designator": "C92-NFC", "net": "NFC_VDD_D", "x": 1070, "y": 2960},
    {"ref": "C93", "designator": "C93-NFC", "net": "NFC_VDD_A", "x": 1220, "y": 2960},
    {"ref": "C94", "designator": "C94-NFC", "net": "NFC_VDD_RF", "x": 1370, "y": 2960},
    {"ref": "C95", "designator": "C95-NFC", "net": "NFC_VDD_AM", "x": 1520, "y": 2960},
    {"ref": "C96", "designator": "C96-NFC", "net": "NFC_VDD_DR", "x": 1670, "y": 2960},
    {"ref": "C97", "designator": "C97-NFC", "net": "NFC_AGDC", "x": 1820, "y": 2960},
]


def _stage() -> str:
    if len(sys.argv) != 2 or sys.argv[1] not in {"place", "designate", "wire"}:
        raise SystemExit("usage: repair_nfc_regulator_caps.py place|designate|wire")
    return sys.argv[1]


def main() -> int:
    stage = _stage()
    tx = f"canonical-nfc-regulator-decouple-{stage}-2026-08-28"
    intended = {
        "place": (
            "Place six GRM155R60J225ME15D 2.2uF 0402 capacitors C92-NFC..C97-NFC "
            "inside box 7 between the matching row and J10, one per ST25R3916B "
            "internal regulator rail. Do not designate or wire."
        ),
        "designate": (
            "Designate C92-NFC..C97-NFC as 2.2uF GRM155R60J225ME15D / C76993. "
            "Do not move or wire."
        ),
        "wire": (
            "Wire C92-NFC..C97-NFC pin 1 to NFC_VDD_D / NFC_VDD_A / NFC_VDD_RF / "
            "NFC_VDD_AM / NFC_VDD_DR / NFC_AGDC and pin 2 to GND. Do not move parts."
        ),
    }[stage]
    checks = {
        "place": [
            "six new undesignated or designated 0402 capacitors sit in box 7",
            "they do not overlap U12, Y2, L2, L3 or the matching caps",
            "no part appears outside box 7",
            "component count increases by exactly 6",
        ],
        "designate": [
            "C92-NFC through C97-NFC exist exactly once",
            "each reads 2.2uF",
            "no extra designator appears",
            "positions stay on the placed row",
        ],
        "wire": [
            "each new capacitor pin 1 is on its ST regulator net",
            "each new capacitor pin 2 is on GND",
            "U12 regulator pins remain on those same nets",
            "census components stay at the post-place count",
        ],
    }[stage]

    base = load_fixture_executor()
    base.assert_identity()
    base.validate_repository_state(base.MUTATION_STATE, base.MUTATION_LEDGER)
    before = base.source_snapshot()
    live = component_records(before["source"])
    if "U12-NFC" not in live:
        raise SystemExit("U12-NFC missing")
    pids_path = JOBS / "nfc-regulator-decouple-pids.json"
    if stage == "place":
        for spec in CAPS:
            if spec["designator"] in live:
                raise SystemExit(f"{spec['designator']} already exists")
    elif stage == "designate":
        if not pids_path.exists():
            raise SystemExit("nfc-regulator-decouple-pids.json missing")
        already = [spec["designator"] for spec in CAPS if spec["designator"] in live]
        if already:
            raise SystemExit(f"already designated {already}")
    else:
        missing = [spec["designator"] for spec in CAPS if spec["designator"] not in live]
        if missing:
            raise SystemExit(f"missing {missing}")

    snapshot = SNAPSHOTS / f"{tx}-before.json"
    snapshot.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")
    base.begin_transaction(
        base.MUTATION_STATE,
        base.MUTATION_LEDGER,
        transaction_id=tx,
        project_uuid=PROJECT,
        document_uuid=PAGE,
        scope="NFC",
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
                "tag": spec["ref"],
                "args": {
                    "deviceUuid": CAP_DEVICE,
                    "x": spec["x"],
                    "y": spec["y"],
                    "rotation": 0,
                    "addIntoBom": True,
                    "addIntoPcb": True,
                    "saveAfter": False,
                    "expectedDocumentUuid": PAGE,
                },
            }
            for spec in CAPS
        ]
        jobs[-1]["args"]["saveAfter"] = True
        placed = base.extract_pids(base.run_batch(jobs, f"{tx}-place"))
        if set(placed) != {spec["ref"] for spec in CAPS}:
            raise SystemExit(f"place pid mismatch {placed}")
        pids_path.write_text(json.dumps(placed, indent=2) + "\n")
        affected = list(placed.values())
    elif stage == "designate":
        placed = json.loads(pids_path.read_text())
        jobs = [
            {
                "tool": "modify_schematic_component",
                "tag": spec["ref"],
                "args": {
                    "primitiveId": placed[spec["ref"]],
                    "designator": spec["designator"],
                    "name": "2.2uF",
                    "manufacturerId": CAP_MPN,
                    "supplier": "LCSC",
                    "supplierId": CAP_LCSC,
                    "addIntoBom": True,
                    "addIntoPcb": True,
                    "saveAfter": False,
                    "expectedDocumentUuid": PAGE,
                },
            }
            for spec in CAPS
        ]
        jobs[-1]["args"]["saveAfter"] = True
        base.run_batch(jobs, f"{tx}-designate")
        affected = [spec["designator"] for spec in CAPS]
    else:
        jobs = [
            {
                "tool": "connect_schematic_pins_to_nets",
                "tag": spec["ref"],
                "args": {
                    "componentPrimitiveId": live[spec["designator"]]["primitive_id"],
                    "connections": [
                        {"pinNumber": "1", "net": spec["net"]},
                        {"pinNumber": "2", "net": "GND"},
                    ],
                    "saveAfter": False,
                    "expectedDocumentUuid": PAGE,
                },
            }
            for spec in CAPS
        ]
        jobs[-1]["args"]["saveAfter"] = True
        base.run_batch(jobs, f"{tx}-wire")
        affected = [spec["designator"] for spec in CAPS] + ["U12-NFC"]

    if base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE}).get("saved") is not True:
        raise SystemExit("explicit canonical save was not confirmed")

    after = base.source_snapshot()
    reread = component_records(after["source"])
    if stage != "place":
        for spec in CAPS:
            if spec["designator"] not in reread:
                raise SystemExit(f"{spec['designator']} missing after {stage}")
    if after["source_hash"] == before["source_hash"]:
        raise SystemExit("source hash did not change")

    semantic = JOBS / f"{tx}-semantic.json"
    semantic.write_text(json.dumps({
        "schema_version": 1,
        "transaction_id": tx,
        "project_uuid": PROJECT,
        "document_uuid": PAGE,
        "scope": "NFC",
        "stage": stage,
        "intended_delta": intended,
        "pre_source_hash": before["source_hash"],
        "post_source_hash": after["source_hash"],
        "saved": True,
        "affected": affected,
        "census": {k: after["census"][k] for k in ("components", "wires", "texts", "rectangles")},
        "source_basis": [
            "ST25R3916B: VDD_A/D/RF/AM/DR and AGDC are internal regulator outputs",
            "STEVAL-ST25R3916B C100/C205/C207/C212/C214/C216 GRM155R60J225ME15D 2.2uF",
            "Captain schDrcLog 2026-08-28 single-pin NFC_VDD_* and NFC_AGDC",
        ],
    }, indent=2, sort_keys=True) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic)
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"CENSUS={after['census']['components']}/{after['census']['wires']}")
    print(f"SEMANTIC={semantic}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
