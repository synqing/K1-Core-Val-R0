#!/usr/bin/env python3
"""Repair box-4 spacing without changing RT boot/clock electrical topology."""
from __future__ import annotations

import argparse
import json
import sys

from complete_rt_boot_clock import CONNECTIONS, NOTE, pin_map, remove_records_and_endpoint_wires
from execute_canonical_container import JOBS, PAGE, PROJECT, SNAPSHOTS, load_fixture_executor
from repair_power_buck import component_records
from inspect_live_components import endpoint_net_map
from wire_led_efuse_support import endpoint, points_for, source_rows


REJECTED = "canonical-rt-boot-clock-completion-2026-08-28"
TX = "canonical-rt-boot-clock-layout-repair-2026-08-28"
MOVES = {
    "U7-RTC": (3120, 4310),
    "C18-RTC": (3300, 4310),
    "R12-RTC": (3450, 4310),
    "SW1-RTC": (3610, 4310),
    "R10-RTC": (3770, 4310),
    "R11-RTC": (3910, 4310),
}
NOTE_TARGET = [3500, 4110]
INTENDED = (
    "Redistribute the box-4 reset row for border and label clearance and move the RT boot "
    "settings note into the empty band between the crystal-load and UART rows"
)


def record_normalized_live_state() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    before = json.loads((SNAPSHOTS / f"{TX}-before.json").read_text())
    if base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE}).get("saved") is not True:
        raise SystemExit("explicit save of normalized layout repair was not confirmed")
    after = base.source_snapshot()
    live = component_records(after["source"])
    for ref, xy in MOVES.items():
        actual = [int(live[ref]["x"]), int(live[ref]["y"])]
        if actual != list(xy):
            raise SystemExit(f"normalized {ref} position mismatch {actual} != {xy}")
    notes = [row for row in source_rows(after["source"])
             if row[0] == "TEXT" and len(row) > 5 and row[5] == NOTE]
    if len(notes) != 1 or notes[0][2:4] != NOTE_TARGET:
        raise SystemExit(f"normalized RT note position mismatch: {notes}")
    if before["census"]["components"] != after["census"]["components"]:
        raise SystemExit("normalized layout repair changed component count")
    pins = pin_map(base, {ref: live[ref] for ref in MOVES}, f"{TX}-normalized-pins")
    net_map = endpoint_net_map(after["source"])
    endpoint_topology: dict[str, str] = {}
    for ref in MOVES:
        for pin_number, net_name in CONNECTIONS[ref].items():
            pin = pins[ref][pin_number]
            actual = net_map.get(endpoint(pin), [])
            if actual != [net_name]:
                raise SystemExit(f"normalized {ref}.{pin_number} nets {actual} != {[net_name]}")
            endpoint_topology[
                json.dumps(points_for(pin), separators=(",", ":"))
            ] = net_name
    semantic_path = JOBS / f"{TX}-semantic.json"
    semantic_path.write_text(json.dumps({
        "schema_version": 1, "transaction_id": TX, "project_uuid": PROJECT,
        "document_uuid": PAGE, "scope": "RT_BOOT_CLOCK", "stage": "move",
        "intended_delta": INTENDED,
        "pre_source_hash": before["source_hash"], "post_source_hash": after["source_hash"],
        "saved": True, "affected": sorted(MOVES),
        "positions": {ref: list(xy) for ref, xy in MOVES.items()},
        "settings_note_position": NOTE_TARGET, "endpoint_topology": endpoint_topology,
        "component_count": after["census"]["components"], "census": after["census"],
        "normalization_note": (
            "EasyEDA persisted the repair and normalised its source before the bridge hash comparison."
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
    live = component_records(before["source"])
    missing = sorted(set(MOVES) - set(live))
    if missing:
        raise SystemExit(f"missing reset-row components: {missing}")
    old_pins = pin_map(base, {ref: live[ref] for ref in MOVES}, f"{TX}-old-pins")
    snapshot_path = SNAPSHOTS / f"{TX}-before.json"
    snapshot_path.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")
    intended = INTENDED
    base.begin_transaction(
        base.MUTATION_STATE, base.MUTATION_LEDGER, transaction_id=TX,
        project_uuid=PROJECT, document_uuid=PAGE, scope="RT_BOOT_CLOCK", stage="move",
        kind="repair", repairs_transaction_id=REJECTED, intended_delta=intended,
        snapshot_path=snapshot_path, expected_checks=[
            "U7 left-side labels clear the box border",
            "reset row symbols and their designators do not overlap",
            "the settings note does not touch the UART resistor row",
            "all endpoint nets and the component count remain unchanged",
        ],
    )

    base.run_batch([
        {"tool": "modify_schematic_component", "tag": ref, "args": {
            "primitiveId": live[ref]["primitive_id"], "x": xy[0], "y": xy[1],
            "saveAfter": index == len(MOVES) - 1, "expectedDocumentUuid": PAGE}}
        for index, (ref, xy) in enumerate(MOVES.items())
    ], f"{TX}-move")
    staged = base.source_snapshot()
    staged_live = component_records(staged["source"])
    new_pins = pin_map(base, {ref: staged_live[ref] for ref in MOVES}, f"{TX}-new-pins")
    points = {
        endpoint(pin) for pinset in old_pins.values() for pin in pinset.values()
    } | {
        endpoint(pin) for pinset in new_pins.values() for pin in pinset.values()
    }
    rows = remove_records_and_endpoint_wires(source_rows(staged["source"]), set(), points)
    notes = [row for row in rows if row[0] == "TEXT" and len(row) > 5 and row[5] == NOTE]
    if len(notes) != 1:
        raise SystemExit(f"expected one RT settings note, found {len(notes)}")
    notes[0][2:4] = NOTE_TARGET
    head = next(row for row in rows if row[0] == "HEAD")
    max_id = int(head[1].get("maxId") or 0)
    endpoint_topology: dict[str, str] = {}
    for ref in MOVES:
        for pin_number, net_name in CONNECTIONS[ref].items():
            geometry = points_for(new_pins[ref][pin_number])
            max_id += 1
            wire_id = f"e{max_id}"
            rows.append(["WIRE", wire_id, geometry, "st11", 0])
            max_id += 1
            attr_id = f"e{max_id}"
            x1, y1, x2, y2 = geometry[0]
            rows.append(["ATTR", attr_id, wire_id, "NET", net_name, 0, 1,
                         (x1 + x2) / 2, (y1 + y2) / 2, 0, "st4", 0])
            endpoint_topology[json.dumps(geometry, separators=(",", ":"))] = net_name
    head[1]["maxId"] = max_id
    source = "\n".join(json.dumps(row, separators=(",", ":")) for row in rows)
    result = base.mcp_call("set_document_source", {
        "source": source, "expectedSourceHash": staged["source_hash"],
        "skipConfirmation": True, "expectedDocumentUuid": PAGE,
    }, timeout=240)
    (JOBS / f"{TX}-set-source-result.json").write_text(json.dumps(result, indent=2) + "\n")
    if base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE}).get("saved") is not True:
        raise SystemExit("explicit save of RT boot/clock layout repair was not confirmed")

    after = base.source_snapshot()
    after_live = component_records(after["source"])
    for ref, xy in MOVES.items():
        actual = [int(after_live[ref]["x"]), int(after_live[ref]["y"])]
        if actual != list(xy):
            raise SystemExit(f"{ref} position mismatch {actual} != {xy}")
    after_notes = [row for row in source_rows(after["source"])
                   if row[0] == "TEXT" and len(row) > 5 and row[5] == NOTE]
    if len(after_notes) != 1 or after_notes[0][2:4] != NOTE_TARGET:
        raise SystemExit(f"RT settings note position mismatch: {after_notes}")
    if before["census"]["components"] != after["census"]["components"]:
        raise SystemExit("layout repair changed the component count")

    semantic_path = JOBS / f"{TX}-semantic.json"
    semantic_path.write_text(json.dumps({
        "schema_version": 1, "transaction_id": TX, "project_uuid": PROJECT,
        "document_uuid": PAGE, "scope": "RT_BOOT_CLOCK", "stage": "move",
        "intended_delta": intended, "pre_source_hash": before["source_hash"],
        "post_source_hash": after["source_hash"], "saved": True,
        "affected": sorted(MOVES), "positions": {ref: list(xy) for ref, xy in MOVES.items()},
        "settings_note_position": NOTE_TARGET, "endpoint_topology": endpoint_topology,
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
