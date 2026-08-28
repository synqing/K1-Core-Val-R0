#!/usr/bin/env python3
"""Repair ESP32-S3 service USB, reset timing and physical recovery access."""
from __future__ import annotations

import argparse
import json
import sys

from complete_rt_boot_clock import remove_records_and_endpoint_wires
from complete_rt_power import all_components
from execute_canonical_container import JOBS, PAGE, PROJECT, SNAPSHOTS, load_fixture_executor
from inspect_live_components import endpoint_net_map
from repair_power_buck import component_records
from wire_led_efuse_support import endpoint, points_for, source_rows


TX = "canonical-esp-service-electrical-repair-2026-08-28"
PIDS_PATH = JOBS / f"{TX}-pids.json"
STAGE_PATH = JOBS / f"{TX}-stages.json"
INTENDED = (
    "Replace the invalid service-USB VBUS-to-nonexistent-module-pin path with a self-powered "
    "100 k/100 k VBUS sense divider to ESP GPIO15; add 22 ohm D+/D- series resistors and DNP "
    "tuning capacitors; connect every USB-C VBUS, ground and shield contact; correct EN timing "
    "to 10 k/1 uF; and replace the incomplete four-pin UART header with direct GND, 3V3, TX, RX, "
    "EN and BOOT access"
)

DEVICES = {
    "C42": {
        "deviceUuid": "d7cfbc3b990d4f4892dd720a635a2d32", "designator": "C42-ESP",
        "name": "1uF", "mpn": "GRM155R61A105KE15D", "supplierId": "C76999",
        "x": 4365, "y": 4362,
    },
    "J6": {
        "deviceUuid": "5f08146151b14d08af630cc4cd9d0168", "designator": "J6-ESP",
        "name": "RECOVERY 1x6", "mpn": "PREC006SAAN-RC", "supplierId": "",
        "x": 4750, "y": 4300,
    },
    "R71": {
        "deviceUuid": "0cc9cee0c09e4a1c8b41e9d1feefa5b2", "designator": "R71-ESP",
        "name": "100k", "mpn": "RC0402FR-07100KL", "supplierId": "C60491",
        "x": 4450, "y": 3890,
    },
    "R72": {
        "deviceUuid": "0cc9cee0c09e4a1c8b41e9d1feefa5b2", "designator": "R72-ESP",
        "name": "100k", "mpn": "RC0402FR-07100KL", "supplierId": "C60491",
        "x": 4580, "y": 3890,
    },
    "R73": {
        "deviceUuid": "8bef1d5fc0144eac931ff4a7b9204fb5", "designator": "R73-ESP",
        "name": "22R", "mpn": "RC0402FR-0722RL", "supplierId": "",
        "x": 4120, "y": 4140,
    },
    "R74": {
        "deviceUuid": "8bef1d5fc0144eac931ff4a7b9204fb5", "designator": "R74-ESP",
        "name": "22R", "mpn": "RC0402FR-0722RL", "supplierId": "",
        "x": 4120, "y": 4080,
    },
}

CONNECTIONS = {
    "U9-ESP": {
        "8": "ESP_USB_VBUS_SENSE", "13": "USB_DM_S3", "14": "USB_DP_S3",
        "36": "ESP_UART0_RX", "37": "ESP_UART0_TX",
    },
    "U10-ESP": {
        "1": "USB_DP", "2": "GND", "3": "USB_DM",
        "4": "USB_DM_ESD", "5": "S3_VBUS", "6": "USB_DP_ESD",
    },
    "J7-ESP": {
        "A1": "GND", "A4": "S3_VBUS", "A5": "USB_CC1", "A6": "USB_DP",
        "A7": "USB_DM", "A9": "S3_VBUS", "A12": "GND",
        "B1": "GND", "B4": "S3_VBUS", "B5": "USB_CC2", "B6": "USB_DP",
        "B7": "USB_DM", "B9": "S3_VBUS", "B12": "GND", "1": "GND",
    },
    "C42-ESP": {"1": "ESP_EN", "2": "GND"},
    "C43-ESP": {"1": "USB_DP_S3", "2": "GND"},
    "C44-ESP": {"1": "USB_DM_S3", "2": "GND"},
    "J6-ESP": {
        "1": "GND", "2": "3V3", "3": "ESP_UART0_TX",
        "4": "ESP_UART0_RX", "5": "ESP_EN", "6": "ESP_GPIO0",
    },
    "R71-ESP": {"1": "S3_VBUS", "2": "ESP_USB_VBUS_SENSE"},
    "R72-ESP": {"1": "ESP_USB_VBUS_SENSE", "2": "GND"},
    "R73-ESP": {"1": "USB_DP_ESD", "2": "USB_DP_S3"},
    "R74-ESP": {"1": "USB_DM_ESD", "2": "USB_DM_S3"},
}

NOTES = [
    (4240, 3845, "SERVICE USB: SELF-POWERED | VBUS SENSE 100k/100k -> GPIO15 | NO BACK-POWER"),
    (4590, 4410, "RECOVERY: GND | 3V3 | TX | RX | EN | BOOT"),
]

SERVICE_NOTE = "SERVICE USB: SELF-POWERED | VBUS SENSE 100k/100k -> GPIO15 | NO BACK-POWER"
SERVICE_NOTE_REPAIRED = "SELF-POWERED USB | VBUS SENSE -> GPIO15 | NO BACK-POWER"


def active(base) -> None:
    state = json.loads(base.MUTATION_STATE.read_text())
    if state.get("state") != "IN_FLIGHT" or state.get("active_transaction", {}).get("transaction_id") != TX:
        raise SystemExit(f"{TX} is not the active transaction")


def save_stage(name: str, snapshot: dict) -> None:
    stages = json.loads(STAGE_PATH.read_text()) if STAGE_PATH.exists() else {}
    stages[name] = {"source_hash": snapshot["source_hash"], "census": snapshot["census"]}
    STAGE_PATH.write_text(json.dumps(stages, indent=2, sort_keys=True) + "\n")


def save_pre_write(name: str, snapshot: dict) -> None:
    """Persist the live EasyEDA source immediately before each write stage."""
    path = SNAPSHOTS / f"{TX}-before-{name}.json"
    path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")


def pin_maps(base, targets: dict[str, dict], stem: str) -> dict[str, dict[str, dict]]:
    results = base.run_batch([
        {"tool": "list_schematic_component_pins", "tag": ref, "args": {
            "componentPrimitiveId": record["primitive_id"], "expectedDocumentUuid": PAGE}}
        for ref, record in targets.items()
    ], stem)
    parsed = base.parse_live_pins(results)
    return {ref: {str(pin["pinNumber"]): pin for pin in pins} for ref, pins in parsed.items()}


def set_source(base, rows: list[list], expected_hash: str, stem: str) -> dict:
    source = "\n".join(json.dumps(row, separators=(",", ":")) for row in rows)
    try:
        result = base.mcp_call("set_document_source", {
            "source": source, "expectedSourceHash": expected_hash, "skipConfirmation": True,
            "expectedDocumentUuid": PAGE,
        }, timeout=240)
    except SystemExit as exc:
        result = {"bridge_message": str(exc)}
    (JOBS / f"{TX}-{stem}-set-source-result.json").write_text(json.dumps(result, indent=2) + "\n")
    if base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE}).get("saved") is not True:
        raise SystemExit(f"save after {stem} was not confirmed")
    return base.source_snapshot()


def prune() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    base.validate_repository_state(base.MUTATION_STATE, base.MUTATION_LEDGER)
    before = base.source_snapshot()
    live = component_records(before["source"])
    old = {ref: live[ref] for ref in ("FB4-ESP", "J6-ESP", "C42-ESP")}
    pins = pin_maps(base, old, f"{TX}-old-pins")
    snapshot = SNAPSHOTS / f"{TX}-before.json"
    snapshot.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")
    base.begin_transaction(
        base.MUTATION_STATE, base.MUTATION_LEDGER, transaction_id=TX,
        project_uuid=PROJECT, document_uuid=PAGE, scope="ESP_SERVICE_USB", stage="repair",
        kind="normal", intended_delta=INTENDED, snapshot_path=snapshot,
        expected_checks=[
            "no service VBUS rail is connected to a nonexistent WROOM module pin",
            "USB-C has all duplicate VBUS and ground contacts plus shield connected",
            "GPIO19/20 USB paths include ESD, 22 ohm series parts and DNP tune capacitors",
            "GPIO15 receives divided VBUS sense without allowing USB back-power",
            "the physical recovery header exposes GND 3V3 TX RX EN and BOOT",
        ],
    )
    points = {endpoint(pin) for pinset in pins.values() for pin in pinset.values()}
    rows = remove_records_and_endpoint_wires(
        source_rows(before["source"]), {record["primitive_id"] for record in old.values()}, points,
    )
    after = set_source(base, rows, before["source_hash"], "prune")
    if after["census"]["components"] != 212:
        raise SystemExit(f"ESP prune expected 212 components, found {after['census']['components']}")
    save_stage("prune", after)
    print(f"STAGE=prune SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def add() -> int:
    base = load_fixture_executor()
    base.assert_identity(); active(base)
    before = base.source_snapshot()
    save_pre_write("add", before)
    jobs = [
        {"tool": "add_schematic_component", "tag": ref, "args": {
            "deviceUuid": spec["deviceUuid"], "x": spec["x"], "y": spec["y"],
            "rotation": 0, "addIntoBom": True, "addIntoPcb": True,
            "saveAfter": index == len(DEVICES) - 1, "expectedDocumentUuid": PAGE,
        }}
        for index, (ref, spec) in enumerate(DEVICES.items())
    ]
    pids = base.extract_pids(base.run_batch(jobs, f"{TX}-add"))
    if set(pids) != set(DEVICES):
        raise SystemExit(f"ESP add missing {sorted(set(DEVICES) - set(pids))}")
    PIDS_PATH.write_text(json.dumps(pids, indent=2, sort_keys=True) + "\n")
    after = base.source_snapshot()
    if after["census"]["components"] != 218:
        raise SystemExit(f"ESP add expected 218 components, found {after['census']['components']}")
    save_stage("add", after)
    print(f"STAGE=add SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def designate() -> int:
    base = load_fixture_executor()
    base.assert_identity(); active(base)
    pids = json.loads(PIDS_PATH.read_text())
    before = base.source_snapshot()
    save_pre_write("designate", before)
    live = component_records(before["source"])
    jobs = []
    for ref, spec in DEVICES.items():
        jobs.append({"tool": "modify_schematic_component", "tag": ref, "args": {
            "primitiveId": pids[ref], "designator": spec["designator"], "name": spec["name"],
            "manufacturerId": spec["mpn"], "supplier": "LCSC",
            "supplierId": spec["supplierId"], "addIntoBom": True, "addIntoPcb": True,
            "saveAfter": False, "expectedDocumentUuid": PAGE,
        }})
    for ref, net in (("C43-ESP", "USB D+"), ("C44-ESP", "USB D-")):
        jobs.append({"tool": "modify_schematic_component", "tag": ref, "args": {
            "primitiveId": live[ref]["primitive_id"], "name": f"DNP / 100pF {net} TUNE",
            "addIntoBom": False, "addIntoPcb": True, "saveAfter": False,
            "expectedDocumentUuid": PAGE,
        }})
    for index, (x, y, content) in enumerate(NOTES):
        jobs.append({"tool": "add_schematic_text", "tag": f"note-{index}", "args": {
            "x": x, "y": y, "content": content, "fontSize": 8, "bold": True,
            "textColor": "#1F5AA6", "saveAfter": index == len(NOTES) - 1,
            "expectedDocumentUuid": PAGE,
        }})
    base.run_batch(jobs, f"{TX}-designate")
    after = base.source_snapshot()
    final = component_records(after["source"])
    for spec in DEVICES.values():
        if spec["designator"] not in final or after["source"].count(f'"Designator","{spec["designator"]}"') != 1:
            raise SystemExit(f"missing or duplicate {spec['designator']}")
    save_stage("designate", after)
    print(f"STAGE=designate SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def label_repair() -> int:
    """Keep the service-USB caption fully inside the ESP domain box."""
    base = load_fixture_executor()
    base.assert_identity(); active(base)
    before = base.source_snapshot()
    save_pre_write("label-repair", before)
    rows = source_rows(before["source"])
    matches = [row for row in rows if row[0] == "TEXT" and len(row) > 5 and row[5] == SERVICE_NOTE]
    if len(matches) != 1:
        raise SystemExit(f"expected one service USB note, found {len(matches)}")
    matches[0][2] = 4500
    matches[0][3] = 3845
    matches[0][5] = SERVICE_NOTE_REPAIRED
    after = set_source(base, rows, before["source_hash"], "label-repair")
    repaired = [row for row in source_rows(after["source"])
                if row[0] == "TEXT" and len(row) > 5 and row[5] == SERVICE_NOTE_REPAIRED]
    if len(repaired) != 1 or repaired[0][2:4] != [4500, 3845]:
        raise SystemExit(f"service USB note repair did not persist: {repaired}")
    save_stage("label_repair", after)
    print(f"STAGE=label_repair SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def connect() -> int:
    base = load_fixture_executor()
    base.assert_identity(); active(base)
    before = base.source_snapshot()
    save_pre_write("connect", before)
    live = component_records(before["source"])
    targets = {ref: live[ref] for ref in CONNECTIONS}
    pins = pin_maps(base, targets, f"{TX}-connect-pins")
    for ref, mapping in CONNECTIONS.items():
        missing = sorted(set(mapping) - set(pins[ref]))
        if missing:
            raise SystemExit(f"{ref} missing pins {missing}")
    points = {endpoint(pins[ref][pin]) for ref, mapping in CONNECTIONS.items() for pin in mapping}
    rows = remove_records_and_endpoint_wires(source_rows(before["source"]), set(), points)
    head = next(row for row in rows if row[0] == "HEAD")
    max_id = int(head[1].get("maxId") or 0)
    topology = {}
    shown = set()
    for ref, mapping in CONNECTIONS.items():
        for pin_number, net in mapping.items():
            geometry = points_for(pins[ref][pin_number])
            max_id += 1; wire_id = f"e{max_id}"
            rows.append(["WIRE", wire_id, geometry, "st11", 0])
            max_id += 1
            x1, y1, x2, y2 = geometry[0]
            key = (ref, net)
            visible = 1 if key not in shown else 0
            # USB duplicate connector contacts and DNP endpoints are semantic, not label farms.
            if ref in ("J7-ESP", "C43-ESP", "C44-ESP"):
                visible = 0
            rows.append(["ATTR", f"e{max_id}", wire_id, "NET", net, 0, visible,
                         (x1 + x2) / 2, (y1 + y2) / 2, 0, "st4", 0])
            shown.add(key)
            topology[f"{ref}.{pin_number}"] = net
    head[1]["maxId"] = max_id
    after = set_source(base, rows, before["source_hash"], "connect")
    if after["census"]["components"] != 218:
        raise SystemExit("ESP connection changed the component count")
    nets = endpoint_net_map(after["source"])
    for ref, mapping in CONNECTIONS.items():
        for pin_number, expected in mapping.items():
            actual = nets.get(endpoint(pins[ref][pin_number]), [])
            if actual != [expected]:
                raise SystemExit(f"{ref}.{pin_number} nets {actual} != {[expected]}")
    for pin_number in ("A8", "B8"):
        if nets.get(endpoint(pins["J7-ESP"][pin_number]), []):
            raise SystemExit(f"J7 {pin_number} SBU contact must remain open")
    save_stage("connect", after)
    (JOBS / f"{TX}-topology.json").write_text(json.dumps(topology, indent=2, sort_keys=True) + "\n")
    print(f"STAGE=connect SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def declutter() -> int:
    """Hide redundant local endpoint labels without changing named-net topology."""
    base = load_fixture_executor()
    base.assert_identity(); active(base)
    before = base.source_snapshot()
    save_pre_write("declutter", before)
    live = component_records(before["source"])
    refs = ("U10-ESP", "J6-ESP", "R71-ESP", "R72-ESP", "R73-ESP", "R74-ESP")
    pins = pin_maps(base, {ref: live[ref] for ref in refs}, f"{TX}-declutter-pins")
    points = {endpoint(pin) for ref in refs for pin in pins[ref].values()}
    rows = source_rows(before["source"])
    wire_ids = {
        str(row[1]) for row in rows if row[0] == "WIRE"
        and any((int(x1), int(y1)) in points or (int(x2), int(y2)) in points
                for x1, y1, x2, y2 in row[2])
    }
    hidden = 0
    for row in rows:
        if (row[0] == "ATTR" and len(row) > 6 and str(row[2]) in wire_ids
                and row[3] == "NET" and row[6] == 1):
            row[6] = 0
            hidden += 1
    if hidden != 20:
        raise SystemExit(f"expected to hide 20 redundant ESP endpoint labels, found {hidden}")
    after = set_source(base, rows, before["source_hash"], "declutter")
    nets = endpoint_net_map(after["source"])
    all_live = component_records(after["source"])
    all_pins = pin_maps(base, {ref: all_live[ref] for ref in CONNECTIONS}, f"{TX}-declutter-verify-pins")
    for ref, mapping in CONNECTIONS.items():
        for pin_number, expected in mapping.items():
            actual = nets.get(endpoint(all_pins[ref][pin_number]), [])
            if actual != [expected]:
                raise SystemExit(f"declutter changed {ref}.{pin_number}: {actual} != {[expected]}")
    save_stage("declutter", after)
    print(f"STAGE=declutter SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def label_repair2() -> int:
    """Move the service caption off the TP1/TP2 row at useful inspection scale."""
    base = load_fixture_executor()
    base.assert_identity(); active(base)
    before = base.source_snapshot()
    save_pre_write("label-repair2", before)
    rows = source_rows(before["source"])
    matches = [row for row in rows
               if row[0] == "TEXT" and len(row) > 5 and row[5] == SERVICE_NOTE_REPAIRED]
    if len(matches) != 1:
        raise SystemExit(f"expected one repaired service USB note, found {len(matches)}")
    matches[0][2] = 4550
    matches[0][3] = 3940
    after = set_source(base, rows, before["source_hash"], "label-repair2")
    moved = [row for row in source_rows(after["source"])
             if row[0] == "TEXT" and len(row) > 5 and row[5] == SERVICE_NOTE_REPAIRED]
    if len(moved) != 1 or moved[0][2:4] != [4550, 3940]:
        raise SystemExit(f"service USB note second repair did not persist: {moved}")
    save_stage("label_repair2", after)
    print(f"STAGE=label_repair2 SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def record() -> int:
    base = load_fixture_executor()
    base.assert_identity(); active(base)
    before = json.loads((SNAPSHOTS / f"{TX}-before.json").read_text())
    after = base.source_snapshot()
    if after["census"]["components"] != 218:
        raise SystemExit(f"final ESP component count changed: {after['census']['components']}")
    rows = source_rows(after["source"])
    notes = [row for row in rows
             if row[0] == "TEXT" and len(row) > 5 and row[5] == SERVICE_NOTE_REPAIRED]
    if len(notes) != 1 or notes[0][2:4] != [4550, 3940]:
        raise SystemExit(f"final service USB caption mismatch: {notes}")
    live = component_records(after["source"])
    pins = pin_maps(base, {ref: live[ref] for ref in CONNECTIONS}, f"{TX}-record-verify-pins")
    nets = endpoint_net_map(after["source"])
    for ref, mapping in CONNECTIONS.items():
        for pin_number, expected in mapping.items():
            actual = nets.get(endpoint(pins[ref][pin_number]), [])
            if actual != [expected]:
                raise SystemExit(f"final {ref}.{pin_number} nets {actual} != {[expected]}")
    for pin_number in ("A8", "B8"):
        if nets.get(endpoint(pins["J7-ESP"][pin_number]), []):
            raise SystemExit(f"final J7 {pin_number} SBU contact must remain open")
    semantic = JOBS / f"{TX}-semantic.json"
    semantic.write_text(json.dumps({
        "schema_version": 1, "transaction_id": TX, "project_uuid": PROJECT,
        "document_uuid": PAGE, "scope": "ESP_SERVICE_USB", "stage": "repair",
        "intended_delta": INTENDED, "pre_source_hash": before["source_hash"],
        "post_source_hash": after["source_hash"], "saved": True,
        "affected": sorted(CONNECTIONS), "topology": json.loads((JOBS / f"{TX}-topology.json").read_text()),
        "component_count": after["census"]["components"], "census": after["census"],
        "service_caption": {"content": SERVICE_NOTE_REPAIRED, "x": 4550, "y": 3940},
        "visual_cleanup": "redundant local endpoint labels hidden; named-net topology unchanged",
        "deliberately_open": ["J7 A8 SBU1", "J7 B8 SBU2"],
        "source_basis": [
            "Espressif ESP32-S3 Hardware Design Guidelines latest: EN 10 k/1 uF, GPIO19/20 USB and reserved 22/33 ohm plus DNP capacitors",
            "Espressif ESP-USB self-powered device guidance: VBUS monitoring through a divider or comparator",
            "Espressif ESP32-S3-DevKitC-1 reference schematic: connector shield contacts to GND",
            "K1 contracts/usb-interface.md and contracts/debug-fabric.md",
        ],
    }, indent=2, sort_keys=True) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic)
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"SEMANTIC={semantic}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=(
        "prune", "add", "designate", "label_repair", "connect", "declutter",
        "label_repair2", "record"
    ))
    args = ap.parse_args()
    return globals()[args.stage]()


if __name__ == "__main__":
    sys.exit(main())
