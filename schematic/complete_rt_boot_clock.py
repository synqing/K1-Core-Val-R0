#!/usr/bin/env python3
"""Complete and tidy the RT1062 boot, reset, clock and external flash domain."""
from __future__ import annotations

import argparse
import json
import sys

from execute_canonical_container import JOBS, PAGE, PROJECT, SNAPSHOTS, load_fixture_executor
from repair_power_buck import component_records
from wire_led_efuse_support import endpoint, points_for, source_rows


TX = "canonical-rt-boot-clock-completion-2026-08-28"
NOTE = "RT BOOT: 10 INTERNAL / 01 SERIAL DOWNLOADER | U7 3.07V supervisor | CT OPEN = 20ms"

DEVICES = {
    "R10": {
        "deviceUuid": "6593321c1e554b2f9070c57621ba8753",
        "designator": "R10-RTC", "name": "10k", "mpn": "RC0402FR-0710KL",
        "supplier": "LCSC", "supplierId": "C60490", "x": 3700, "y": 4310,
    },
    "R11": {
        "deviceUuid": "6593321c1e554b2f9070c57621ba8753",
        "designator": "R11-RTC", "name": "10k", "mpn": "RC0402FR-0710KL",
        "supplier": "LCSC", "supplierId": "C60490", "x": 3880, "y": 4310,
    },
    "C35": {
        "deviceUuid": "e0d07da0770348cfae7a47f2b8f74050",
        "designator": "C35-RTDBG", "name": "8.2pF", "mpn": "GRM1555C1H8R2CA01D",
        "supplier": "LCSC", "supplierId": "C76984", "x": 3095, "y": 4200,
    },
    "C36": {
        "deviceUuid": "e0d07da0770348cfae7a47f2b8f74050",
        "designator": "C36-RTDBG", "name": "8.2pF", "mpn": "GRM1555C1H8R2CA01D",
        "supplier": "LCSC", "supplierId": "C76984", "x": 3335, "y": 4200,
    },
    "U8": {
        "deviceUuid": "e3b39f39139e446ead7a11dd4da2f61f",
        "designator": "U8-RTDBG", "name": "64Mbit / 3V", "mpn": "IS25LP064A-JBLE",
        "supplier": "LCSC", "supplierId": "C412831", "x": 3575, "y": 4515,
    },
    "R68": {
        "deviceUuid": "59cbc61ba08043769ad3f7c9a6f84ca6",
        "designator": "R68-RTDBG", "name": "2.2M", "mpn": "RC0402FR-072M2L",
        "supplier": "LCSC", "supplierId": "C138015", "x": 3095, "y": 4415,
    },
    "R69": {
        "deviceUuid": "6593321c1e554b2f9070c57621ba8753",
        "designator": "R69-RTDBG", "name": "10k", "mpn": "RC0402FR-0710KL",
        "supplier": "LCSC", "supplierId": "C60490", "x": 3335, "y": 4415,
    },
}

MOVES = {
    "U7-RTC": (3070, 4310),
    "C18-RTC": (3230, 4310),
    "R12-RTC": (3370, 4310),
    "SW1-RTC": (3515, 4310),
}

CONNECTIONS = {
    "U7-RTC": {"1": "POR_B", "2": "GND", "3": "RT_RESET_REQ_N", "5": "3V3", "6": "3V3"},
    "C18-RTC": {"1": "3V3", "2": "GND"},
    "R12-RTC": {"1": "3V3", "2": "POR_B"},
    "SW1-RTC": {"1": "GND", "2": "RT_RESET_REQ_N"},
    "R10-RTC": {"1": "BOOT_MODE0", "2": "GND"},
    "R11-RTC": {"1": "BOOT_MODE1", "2": "3V3"},
    "R13-RTDBG": {"1": "XTALO", "2": "XTALO_Y"},
    "R14-RTDBG": {"1": "3V3", "2": "FLEXSPI_D2"},
    "R68-RTDBG": {"1": "XTALI", "2": "GND"},
    "R69-RTDBG": {"1": "3V3", "2": "FLEXSPI_D3"},
    "C35-RTDBG": {"1": "XTALI", "2": "GND"},
    "C36-RTDBG": {"1": "XTALO_Y", "2": "GND"},
    "C37-RTDBG": {"1": "3V3", "2": "GND"},
    "C38-RTDBG": {"1": "3V3", "2": "GND"},
    "Y1-RTDBG": {"1": "XTALI", "2": "GND", "3": "XTALO_Y", "4": "GND"},
    "U8-RTDBG": {
        "1": "FLEXSPI_SS0", "2": "FLEXSPI_D1", "3": "FLEXSPI_D2", "4": "GND",
        "5": "FLEXSPI_D0", "6": "FLEXSPI_SCLK", "7": "FLEXSPI_D3", "8": "3V3",
    },
}


def pin_map(base, live: dict[str, dict], stem: str) -> dict[str, dict[str, dict]]:
    results = base.run_batch([
        {"tool": "list_schematic_component_pins", "tag": ref, "args": {
            "componentPrimitiveId": live[ref]["primitive_id"], "expectedDocumentUuid": PAGE}}
        for ref in live
    ], stem)
    parsed = base.parse_live_pins(results)
    return {ref: {str(pin["pinNumber"]): pin for pin in parsed[ref]} for ref in live}


def remove_records_and_endpoint_wires(rows: list[list], removed_pids: set[str], points: set[tuple[int, int]]) -> list[list]:
    wire_ids: set[str] = set()
    for row in rows:
        if row[0] != "WIRE":
            continue
        for x1, y1, x2, y2 in row[2]:
            if (int(x1), int(y1)) in points or (int(x2), int(y2)) in points:
                wire_ids.add(str(row[1]))
    output = []
    for row in rows:
        record_id = str(row[1]) if len(row) > 1 else ""
        parent_id = str(row[2]) if row[0] == "ATTR" and len(row) > 2 else ""
        if record_id in removed_pids or parent_id in removed_pids:
            continue
        if record_id in wire_ids or parent_id in wire_ids:
            continue
        output.append(row)
    return output


def record_normalized_live_state() -> int:
    """Record the live state after EasyEDA accepted then normalised set_document_source."""
    base = load_fixture_executor()
    base.assert_identity()
    before = json.loads((SNAPSHOTS / f"{TX}-before.json").read_text())
    if base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE}).get("saved") is not True:
        raise SystemExit("explicit save of normalized RT boot/clock source was not confirmed")
    after = base.source_snapshot()
    final_live = component_records(after["source"])
    missing = sorted(set(CONNECTIONS) - set(final_live))
    if missing:
        raise SystemExit(f"normalized live state is missing {missing}")
    pins = pin_map(base, {ref: final_live[ref] for ref in CONNECTIONS}, f"{TX}-normalized-pins")
    endpoint_topology: dict[str, str] = {}
    for ref, expected in CONNECTIONS.items():
        for pin_number, net_name in expected.items():
            if pin_number not in pins[ref]:
                raise SystemExit(f"normalized {ref} missing pin {pin_number}")
            endpoint_topology[
                json.dumps(points_for(pins[ref][pin_number]), separators=(",", ":"))
            ] = net_name
    expected_names = {
        "R10-RTC": "10k", "R11-RTC": "10k", "C35-RTDBG": "8.2pF",
        "C36-RTDBG": "8.2pF", "U8-RTDBG": "64Mbit / 3V",
        "R68-RTDBG": "2.2M", "R69-RTDBG": "10k",
    }
    for ref, name in expected_names.items():
        if after["source"].count(f'"Designator","{ref}"') != 1:
            raise SystemExit(f"normalized {ref} missing or duplicated")
        if f'"Name","{name}"' not in after["source"]:
            raise SystemExit(f"normalized {ref} value mismatch")
    if "IS25WP064A" in after["source"] or "18pF" in after["source"]:
        raise SystemExit("normalized live state still contains obsolete flash or load caps")
    if after["census"]["components"] != before["census"]["components"] + 2:
        raise SystemExit("normalized live component count differs from the declared replacement")
    if sum(row[0] == "TEXT" and len(row) > 5 and row[5] == NOTE
           for row in source_rows(after["source"])) != 1:
        raise SystemExit("normalized RT boot/clock note missing or duplicated")

    semantic_path = JOBS / f"{TX}-semantic.json"
    semantic_path.write_text(json.dumps({
        "schema_version": 1, "transaction_id": TX, "project_uuid": PROJECT,
        "document_uuid": PAGE, "scope": "RT_BOOT_CLOCK", "stage": "repair",
        "intended_delta": (
            "Move reset and boot support into box 4; complete the TPS3808G33 reset circuit; "
            "set passive internal-boot straps to 10; replace the 1.8 V flash with a 3 V part; "
            "correct the 6 pF crystal load network and add the NXP XTALI bias resistor"
        ),
        "pre_source_hash": before["source_hash"], "post_source_hash": after["source_hash"],
        "saved": True, "affected": sorted(CONNECTIONS),
        "endpoint_topology": endpoint_topology, "settings_note": NOTE,
        "component_count": after["census"]["components"], "census": after["census"],
        "normalization_note": (
            "EasyEDA accepted and persisted the source but normalised its serialized form, "
            "so the bridge compared the live normalised hash against the payload hash and reported a false negative."
        ),
    }, indent=2, sort_keys=True) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic_path)
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"SEMANTIC={semantic_path}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


def main() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    base.validate_repository_state(base.MUTATION_STATE, base.MUTATION_LEDGER)
    before = base.source_snapshot()
    before_live = component_records(before["source"])
    required = set(MOVES) | {
        "R10-RTC", "R11-RTC", "C35-RTDBG", "C36-RTDBG", "U8-RTDBG",
        "R13-RTDBG", "R14-RTDBG", "C37-RTDBG", "C38-RTDBG", "Y1-RTDBG",
    }
    missing = sorted(required - set(before_live))
    if missing:
        raise SystemExit(f"missing RT boot/clock components: {missing}")
    old_targets = {ref: before_live[ref] for ref in required}
    old_pins = pin_map(base, old_targets, f"{TX}-old-pins")

    snapshot_path = SNAPSHOTS / f"{TX}-before.json"
    snapshot_path.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")
    intended = (
        "Move reset and boot support into box 4; complete the TPS3808G33 reset circuit; "
        "set passive internal-boot straps to 10; replace the 1.8 V flash with a 3 V part; "
        "correct the 6 pF crystal load network and add the NXP XTALI bias resistor"
    )
    base.begin_transaction(
        base.MUTATION_STATE, base.MUTATION_LEDGER, transaction_id=TX,
        project_uuid=PROJECT, document_uuid=PAGE, scope="RT_BOOT_CLOCK", stage="repair",
        kind="normal", intended_delta=intended, snapshot_path=snapshot_path,
        expected_checks=[
            "box 4 contains one orderly reset, strap, flash and 24 MHz clock implementation",
            "U8 is IS25LP064A-JBLE / 3 V and has D0-D3, SCLK and SS0",
            "boot defaults are BOOT_MODE1 high and BOOT_MODE0 low through 10 k straps",
            "no old 1.8 V flash, 100 k straps, 18 pF load parts, duplicates, modal or overlap remains",
        ],
    )

    add_jobs = [
        {"tool": "add_schematic_component", "tag": tag, "args": {
            "deviceUuid": spec["deviceUuid"], "x": spec["x"], "y": spec["y"],
            "rotation": 0, "addIntoBom": True, "addIntoPcb": True, "saveAfter": False,
            "expectedDocumentUuid": PAGE}}
        for tag, spec in DEVICES.items()
    ]
    pids = base.extract_pids(base.run_batch(add_jobs, f"{TX}-add"))
    if set(pids) != set(DEVICES):
        raise SystemExit(f"replacement/support primitive IDs incomplete: {pids}")

    modify_jobs = []
    for ref, (x, y) in MOVES.items():
        modify_jobs.append({"tool": "modify_schematic_component", "tag": f"move-{ref}", "args": {
            "primitiveId": before_live[ref]["primitive_id"], "x": x, "y": y,
            "saveAfter": False, "expectedDocumentUuid": PAGE}})
    for tag, spec in DEVICES.items():
        modify_jobs.append({"tool": "modify_schematic_component", "tag": f"designate-{tag}", "args": {
            "primitiveId": pids[tag], "designator": spec["designator"], "name": spec["name"],
            "manufacturerId": spec["mpn"], "supplier": spec["supplier"],
            "supplierId": spec["supplierId"], "addIntoBom": True, "addIntoPcb": True,
            "saveAfter": False, "expectedDocumentUuid": PAGE}})
    modify_jobs.append({"tool": "add_schematic_text", "tag": "note", "args": {
        "x": 3500, "y": 4050, "content": NOTE, "fontSize": 10, "bold": True,
        "textColor": "#1F5AA6", "saveAfter": True, "expectedDocumentUuid": PAGE}})
    base.run_batch(modify_jobs, f"{TX}-move-designate")

    staged = base.source_snapshot()
    staged_live = component_records(staged["source"])
    final_refs = set(CONNECTIONS)
    missing_final = sorted(final_refs - set(staged_live))
    if missing_final:
        raise SystemExit(f"staged RT boot/clock refs missing: {missing_final}")
    new_targets = {ref: staged_live[ref] for ref in final_refs}
    new_pins = pin_map(base, new_targets, f"{TX}-new-pins")
    for ref, expected in CONNECTIONS.items():
        absent = sorted(set(expected) - set(new_pins[ref]))
        if absent:
            raise SystemExit(f"{ref} missing expected pins {absent}")

    points = {
        endpoint(pin)
        for pinset in old_pins.values() for pin in pinset.values()
    } | {
        endpoint(pin)
        for pinset in new_pins.values() for pin in pinset.values()
    }
    removed_pids = {
        before_live[ref]["primitive_id"]
        for ref in ("R10-RTC", "R11-RTC", "C35-RTDBG", "C36-RTDBG", "U8-RTDBG")
    }
    rows = remove_records_and_endpoint_wires(source_rows(staged["source"]), removed_pids, points)
    head = next(row for row in rows if row[0] == "HEAD")
    max_id = int(head[1].get("maxId") or 0)
    expected_geometry: dict[str, str] = {}
    for ref, connections in CONNECTIONS.items():
        for pin_number, net_name in connections.items():
            geometry = points_for(new_pins[ref][pin_number])
            max_id += 1
            wire_id = f"e{max_id}"
            rows.append(["WIRE", wire_id, geometry, "st11", 0])
            max_id += 1
            attr_id = f"e{max_id}"
            x1, y1, x2, y2 = geometry[0]
            rows.append(["ATTR", attr_id, wire_id, "NET", net_name, 0, 1,
                         (x1 + x2) / 2, (y1 + y2) / 2, 0, "st4", 0])
            expected_geometry[json.dumps(geometry, separators=(",", ":"))] = net_name
    head[1]["maxId"] = max_id

    expected_count = before["census"]["components"] + 2
    if sum(row[0] == "COMPONENT" for row in rows) != expected_count:
        raise SystemExit("RT boot/clock replacement produced the wrong component count")
    source = "\n".join(json.dumps(row, separators=(",", ":")) for row in rows)
    result = base.run_batch([{"tool": "set_document_source", "tag": "commit", "args": {
        "source": source, "expectedSourceHash": staged["source_hash"], "skipConfirmation": True,
        "expectedDocumentUuid": PAGE}}], f"{TX}-commit")
    (JOBS / f"{TX}-set-source-result.json").write_text(json.dumps(result, indent=2) + "\n")
    if base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE}).get("saved") is not True:
        raise SystemExit("explicit save was not confirmed")

    after = base.source_snapshot()
    final_live = component_records(after["source"])
    expected_names = {
        "R10-RTC": "10k", "R11-RTC": "10k", "C35-RTDBG": "8.2pF",
        "C36-RTDBG": "8.2pF", "U8-RTDBG": "64Mbit / 3V",
        "R68-RTDBG": "2.2M", "R69-RTDBG": "10k",
    }
    for ref, name in expected_names.items():
        if ref not in final_live or after["source"].count(f'"Designator","{ref}"') != 1:
            raise SystemExit(f"{ref} missing or duplicated")
        if f'"Name","{name}"' not in after["source"]:
            raise SystemExit(f"{ref} value mismatch: {name}")
    if "IS25WP064A" in after["source"] or "18pF" in after["source"]:
        raise SystemExit("obsolete 1.8 V flash or crystal-load value remains")
    if sum(row[0] == "TEXT" and len(row) > 5 and row[5] == NOTE
           for row in source_rows(after["source"])) != 1:
        raise SystemExit("RT boot/clock settings note missing or duplicated")

    semantic_path = JOBS / f"{TX}-semantic.json"
    semantic_path.write_text(json.dumps({
        "schema_version": 1, "transaction_id": TX, "project_uuid": PROJECT,
        "document_uuid": PAGE, "scope": "RT_BOOT_CLOCK", "stage": "repair",
        "intended_delta": intended, "pre_source_hash": before["source_hash"],
        "post_source_hash": after["source_hash"], "saved": True,
        "affected": sorted(final_refs), "replacement_primitive_ids": pids,
        "endpoint_topology": expected_geometry, "settings_note": NOTE,
        "component_count": after["census"]["components"], "census": after["census"],
    }, indent=2, sort_keys=True) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic_path)
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"SEMANTIC={semantic_path}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-normalized-live-state", action="store_true")
    args = parser.parse_args()
    sys.exit(record_normalized_live_state() if args.record_normalized_live_state else main())
