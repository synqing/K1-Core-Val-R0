#!/usr/bin/env python3
"""Finish box-4 reset readability with one local request wire."""
from __future__ import annotations

import json
import sys

from complete_rt_boot_clock import NOTE, pin_map, remove_records_and_endpoint_wires
from execute_canonical_container import JOBS, PAGE, PROJECT, SNAPSHOTS, load_fixture_executor
from inspect_live_components import endpoint_net_map
from repair_power_buck import component_records
from wire_led_efuse_support import endpoint, points_for, source_rows


REJECTED = "canonical-rt-boot-clock-layout-repair2-2026-08-28"
TX = "canonical-rt-boot-clock-layout-repair3-2026-08-28"
SWITCH_TARGET = [3100, 4110]
SWITCH_REQUEST_PIN = "1"
SWITCH_GROUND_PIN = "2"
NET_ATTR_VISIBLE = 1
INTENDED = (
    "Move SW1 clear of the UART row and replace the two long RT_RESET_REQ_N endpoint stubs "
    "with one named local wire from the switch to U7 MR#"
)


def build_local_wire(u7_point: tuple[int, int], switch_point: tuple[int, int]) -> list[list[int]]:
    u7_x, u7_y = u7_point
    sw_x, sw_y = switch_point
    elbow_x = min(u7_x, sw_x) - 65
    return [
        [sw_x, sw_y, elbow_x, sw_y],
        [elbow_x, sw_y, elbow_x, u7_y],
        [elbow_x, u7_y, u7_x, u7_y],
    ]


def main() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    base.validate_repository_state(base.MUTATION_STATE, base.MUTATION_LEDGER)
    before = base.source_snapshot()
    live = component_records(before["source"])
    targets = {ref: live[ref] for ref in ("U7-RTC", "SW1-RTC")}
    old_pins = pin_map(base, targets, f"{TX}-old-pins")
    snapshot_path = SNAPSHOTS / f"{TX}-before.json"
    snapshot_path.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")
    base.begin_transaction(
        base.MUTATION_STATE, base.MUTATION_LEDGER, transaction_id=TX,
        project_uuid=PROJECT, document_uuid=PAGE, scope="RT_BOOT_CLOCK", stage="move",
        kind="repair", repairs_transaction_id=REJECTED, intended_delta=INTENDED,
        snapshot_path=snapshot_path, expected_checks=[
            "SW1 clears both the settings note and R17 UART row",
            "one continuous local wire joins SW1 to U7 MR#",
            "RT_RESET_REQ_N is named once outside the U7 symbol body",
            "the remaining U7 and SW1 endpoint nets and component count are unchanged",
        ],
    )
    base.run_batch([{"tool": "modify_schematic_component", "tag": "SW1", "args": {
        "primitiveId": live["SW1-RTC"]["primitive_id"],
        "x": SWITCH_TARGET[0], "y": SWITCH_TARGET[1], "saveAfter": True,
        "expectedDocumentUuid": PAGE}}], f"{TX}-move")
    staged = base.source_snapshot()
    staged_live = component_records(staged["source"])
    new_targets = {ref: staged_live[ref] for ref in ("U7-RTC", "SW1-RTC")}
    new_pins = pin_map(base, new_targets, f"{TX}-new-pins")
    points = {
        endpoint(old_pins["U7-RTC"]["3"]), endpoint(old_pins["SW1-RTC"][SWITCH_REQUEST_PIN]),
        endpoint(old_pins["SW1-RTC"][SWITCH_GROUND_PIN]), endpoint(new_pins["U7-RTC"]["3"]),
        endpoint(new_pins["SW1-RTC"][SWITCH_REQUEST_PIN]), endpoint(new_pins["SW1-RTC"][SWITCH_GROUND_PIN]),
    }
    rows = remove_records_and_endpoint_wires(source_rows(staged["source"]), set(), points)
    head = next(row for row in rows if row[0] == "HEAD")
    max_id = int(head[1].get("maxId") or 0)
    u7_x, u7_y = endpoint(new_pins["U7-RTC"]["3"])
    sw_x, sw_y = endpoint(new_pins["SW1-RTC"][SWITCH_REQUEST_PIN])
    local_wire = build_local_wire((u7_x, u7_y), (sw_x, sw_y))
    max_id += 1
    local_id = f"e{max_id}"
    rows.append(["WIRE", local_id, local_wire, "st11", 0])
    max_id += 1
    local_x = int(sum(segment[0] + segment[2] for segment in local_wire) / (2 * len(local_wire)))
    local_y = int(sum(segment[1] + segment[3] for segment in local_wire) / (2 * len(local_wire)))
    rows.append(["ATTR", f"e{max_id}", local_id, "NET", "RT_RESET_REQ_N", 0, NET_ATTR_VISIBLE,
                 local_x, local_y, 0, "st4", 0])

    ground_geometry = points_for(new_pins["SW1-RTC"][SWITCH_GROUND_PIN])
    max_id += 1
    ground_id = f"e{max_id}"
    rows.append(["WIRE", ground_id, ground_geometry, "st11", 0])
    max_id += 1
    x1, y1, x2, y2 = ground_geometry[0]
    rows.append(["ATTR", f"e{max_id}", ground_id, "NET", "GND", 0, 1,
                 (x1 + x2) / 2, (y1 + y2) / 2, 0, "st4", 0])
    head[1]["maxId"] = max_id

    source = "\n".join(json.dumps(row, separators=(",", ":")) for row in rows)
    try:
        result = base.mcp_call("set_document_source", {
            "source": source, "expectedSourceHash": staged["source_hash"],
            "skipConfirmation": True, "expectedDocumentUuid": PAGE,
        }, timeout=240)
    except SystemExit as exc:
        result = {"bridge_message": str(exc)}
    (JOBS / f"{TX}-set-source-result.json").write_text(json.dumps(result, indent=2) + "\n")
    if base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE}).get("saved") is not True:
        raise SystemExit("explicit save of final reset layout repair was not confirmed")
    after = base.source_snapshot()
    after_live = component_records(after["source"])
    if [int(after_live["SW1-RTC"]["x"]), int(after_live["SW1-RTC"]["y"])] != SWITCH_TARGET:
        raise SystemExit("SW1 final position mismatch")
    if before["census"]["components"] != after["census"]["components"]:
        raise SystemExit("final reset layout repair changed component count")
    final_pins = pin_map(base, {ref: after_live[ref] for ref in ("U7-RTC", "SW1-RTC")}, f"{TX}-final-pins")
    nets = endpoint_net_map(after["source"])
    for ref, pin_number, net_name in (
        ("U7-RTC", "3", "RT_RESET_REQ_N"),
        ("SW1-RTC", SWITCH_REQUEST_PIN, "RT_RESET_REQ_N"),
        ("SW1-RTC", SWITCH_GROUND_PIN, "GND"),
    ):
        actual = nets.get(endpoint(final_pins[ref][pin_number]), [])
        if actual != [net_name]:
            raise SystemExit(f"{ref}.{pin_number} nets {actual} != {[net_name]}")
    if sum(row[0] == "TEXT" and len(row) > 5 and row[5] == NOTE
           for row in source_rows(after["source"])) != 1:
        raise SystemExit("RT settings note changed during reset layout repair")

    semantic_path = JOBS / f"{TX}-semantic.json"
    semantic_path.write_text(json.dumps({
        "schema_version": 1, "transaction_id": TX, "project_uuid": PROJECT,
        "document_uuid": PAGE, "scope": "RT_BOOT_CLOCK", "stage": "move",
        "intended_delta": INTENDED, "pre_source_hash": before["source_hash"],
        "post_source_hash": after["source_hash"], "saved": True,
        "affected": ["U7-RTC", "SW1-RTC"], "switch_position": SWITCH_TARGET,
        "local_reset_wire": local_wire,
        "endpoint_nets": {
            "U7.3": "RT_RESET_REQ_N",
            f"SW1.{SWITCH_REQUEST_PIN}": "RT_RESET_REQ_N",
            f"SW1.{SWITCH_GROUND_PIN}": "GND",
        },
        "component_count": after["census"]["components"], "census": after["census"],
    }, indent=2, sort_keys=True) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic_path)
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"SEMANTIC={semantic_path}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
