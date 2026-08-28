#!/usr/bin/env python3
"""Wire and document the source-derived LED TPS259474L support network in box 2."""
from __future__ import annotations

import argparse
import json
import sys

from execute_canonical_container import JOBS, PAGE, PROJECT, SNAPSHOTS, load_fixture_executor
from repair_power_buck import component_records


TX = "canonical-led-efuse-support-wire-2026-08-28"
PAYLOAD = JOBS / f"{TX}-payload.json"
NOTE = "U4 SET: EN=5V_SYS | OVLO=GND | ILIM≈0.96A | dVdt=2.2nF | PG/PGTH/ITIMER NC"
CONNECTIONS = {
    "U4-PWR2": {
        "1": "5V_SYS",
        "2": "GND",
        "7": "LED_EFUSE_DVDT",
        "8": "GND",
        "9": "LED_EFUSE_ILIM",
    },
    "R8-PWR2": {"1": "LED_EFUSE_ILIM", "2": "GND"},
    "C68-PWR2": {"1": "LED_EFUSE_DVDT", "2": "GND"},
}


def source_rows(source: str) -> list[list]:
    return [json.loads(line) for line in source.splitlines() if line.strip()]


def endpoint(pin: dict) -> tuple[int, int]:
    return int(round(float(pin["x"]))), int(round(-float(pin["y"])))


def points_for(pin: dict) -> list[list[int]]:
    x, y = endpoint(pin)
    rotation = int(pin.get("rotation") or 0) % 360
    if rotation == 0:
        return [[x + 20, y, x, y]]
    if rotation == 180:
        return [[x - 20, y, x, y]]
    if rotation == 90:
        return [[x, y - 20, x, y]]
    if rotation == 270:
        return [[x, y + 20, x, y]]
    raise SystemExit(f"unsupported pin rotation {rotation}")


def load_pin_map(base, live: dict[str, dict]) -> dict[str, dict[str, dict]]:
    results = base.run_batch([
        {"tool": "list_schematic_component_pins", "tag": ref, "args": {
            "componentPrimitiveId": live[ref]["primitive_id"], "expectedDocumentUuid": PAGE}}
        for ref in CONNECTIONS
    ], "canonical-led-efuse-support-pins")
    parsed = base.parse_live_pins(results)
    mapped: dict[str, dict[str, dict]] = {}
    for ref, pins in parsed.items():
        mapped[ref] = {str(pin.get("pinNumber")): pin for pin in pins}
        missing = set(CONNECTIONS[ref]) - set(mapped[ref])
        if missing:
            raise SystemExit(f"{ref} missing pins {sorted(missing)}")
    return mapped


def prepare() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    base.validate_repository_state(base.MUTATION_STATE, base.MUTATION_LEDGER)
    before = base.source_snapshot()
    live = component_records(before["source"])
    missing = [ref for ref in CONNECTIONS if ref not in live]
    if missing:
        raise SystemExit(f"LED eFuse support components missing before wiring: {missing}")
    pins = load_pin_map(base, live)
    snapshot = SNAPSHOTS / f"{TX}-before.json"
    snapshot.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")
    intended = (
        "Wire the LED TPS259474L EN, OVLO, GND, ILM and dVdt support in box 2 and "
        "visibly record the deliberately unused PG, PGTH and ITIMER pins"
    )
    base.begin_transaction(
        base.MUTATION_STATE, base.MUTATION_LEDGER, transaction_id=TX,
        project_uuid=PROJECT, document_uuid=PAGE, scope="POWER_LED", stage="wire",
        kind="normal", intended_delta=intended, snapshot_path=snapshot,
        expected_checks=[
            "U4 EN remains on 5V_SYS; OVLO and GND are on GND",
            "U4 ILM and R8 form LED_EFUSE_ILIM; U4 DVDT and C68 form LED_EFUSE_DVDT",
            "the settings note is completely inside box 2 and readable",
            "no duplicate endpoint stubs, modal, or unrelated movement is visible",
        ],
    )

    all_rows = source_rows(before["source"])
    target_endpoints = {
        endpoint(pins[ref][pin_number])
        for ref, spec in CONNECTIONS.items() for pin_number in spec
    }
    remove_wire_ids: set[str] = set()
    for record in all_rows:
        if record[0] != "WIRE":
            continue
        for segment in record[2]:
            if ((int(segment[0]), int(segment[1])) in target_endpoints
                    or (int(segment[2]), int(segment[3])) in target_endpoints):
                remove_wire_ids.add(str(record[1]))

    output = []
    for record in all_rows:
        record_id = str(record[1]) if len(record) > 1 and isinstance(record[1], str) else None
        parent_id = str(record[2]) if record[0] == "ATTR" and len(record) > 2 else None
        if record_id in remove_wire_ids or parent_id in remove_wire_ids:
            continue
        output.append(record)

    head = next((record for record in output if record[0] == "HEAD"), None)
    if not head or not isinstance(head[1], dict):
        raise SystemExit("schematic HEAD record missing")
    max_id = int(head[1].get("maxId") or 0)
    expected_geometry: dict[str, str] = {}
    for ref, spec in CONNECTIONS.items():
        for pin_number, net_name in spec.items():
            points = points_for(pins[ref][pin_number])
            max_id += 1
            wire_id = f"e{max_id}"
            output.append(["WIRE", wire_id, points, "st11", 0])
            max_id += 1
            attr_id = f"e{max_id}"
            x1, y1, x2, y2 = points[0]
            output.append(["ATTR", attr_id, wire_id, "NET", net_name, 0, 1,
                           (x1 + x2) / 2, (y1 + y2) / 2, 0, "st4", 0])
            expected_geometry[json.dumps(points, separators=(",", ":"))] = net_name
    if not any(record[0] == "FONTSTYLE" and record[1] == "st15" for record in output):
        output.append(["FONTSTYLE", "st15", None, "#1F5AA6", None, 10, None, 1, None, None, 0, 2])
    max_id += 1
    output.append(["TEXT", f"e{max_id}", 980, 3645, 0, NOTE, "st15", 0])
    head[1]["maxId"] = max_id

    if sum(record[0] == "COMPONENT" for record in output) != 190:
        raise SystemExit("LED eFuse wiring changed the component count")
    if sum(record[0] == "RECT" for record in output) != 10:
        raise SystemExit("LED eFuse wiring changed the domain rectangles")
    if sum(record[0] == "TEXT" and len(record) > 5 and record[5] == NOTE for record in output) != 1:
        raise SystemExit("LED eFuse settings note is not unique")
    net_attrs = {str(record[2]): str(record[4]) for record in output
                 if record[0] == "ATTR" and len(record) > 4 and record[3] == "NET"}
    observed_geometry = {
        json.dumps(record[2], separators=(",", ":")): net_attrs.get(str(record[1]))
        for record in output if record[0] == "WIRE"
        and json.dumps(record[2], separators=(",", ":")) in expected_geometry
    }
    if observed_geometry != expected_geometry:
        raise SystemExit("prepared LED eFuse endpoint topology differs from the declaration")
    payload = {
        "source": "\n".join(json.dumps(record, separators=(",", ":")) for record in output),
        "expectedSourceHash": before["source_hash"],
        "expectedDocumentUuid": PAGE,
        "skipConfirmation": True,
    }
    PAYLOAD.write_text(json.dumps(payload, indent=2) + "\n")
    (JOBS / f"{TX}-expected-geometry.json").write_text(
        json.dumps(expected_geometry, indent=2, sort_keys=True) + "\n")
    print(f"PRE_SOURCE_HASH={before['source_hash']}")
    print(f"PAYLOAD={PAYLOAD}")
    return 0


def record() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    before = json.loads((SNAPSHOTS / f"{TX}-before.json").read_text())
    after = base.source_snapshot()
    all_rows = source_rows(after["source"])
    expected_geometry = json.loads((JOBS / f"{TX}-expected-geometry.json").read_text())
    net_attrs = {str(record[2]): str(record[4]) for record in all_rows
                 if record[0] == "ATTR" and len(record) > 4 and record[3] == "NET"}
    observed_geometry = {
        json.dumps(record[2], separators=(",", ":")): net_attrs.get(str(record[1]))
        for record in all_rows if record[0] == "WIRE"
        and json.dumps(record[2], separators=(",", ":")) in expected_geometry
    }
    if observed_geometry != expected_geometry:
        raise SystemExit("live LED eFuse endpoint topology differs from the prepared topology")
    if sum(record[0] == "TEXT" and len(record) > 5 and record[5] == NOTE for record in all_rows) != 1:
        raise SystemExit("live LED eFuse settings note is missing or duplicated")
    semantic = JOBS / f"{TX}-semantic.json"
    semantic.write_text(json.dumps({
        "schema_version": 1, "transaction_id": TX, "project_uuid": PROJECT,
        "document_uuid": PAGE, "scope": "POWER_LED", "stage": "wire",
        "intended_delta": (
            "Wire the LED TPS259474L EN, OVLO, GND, ILM and dVdt support in box 2 and "
            "visibly record the deliberately unused PG, PGTH and ITIMER pins"),
        "pre_source_hash": before["source_hash"], "post_source_hash": after["source_hash"],
        "saved": True, "affected": list(CONNECTIONS), "endpoint_topology": expected_geometry,
        "settings_note": NOTE, "census": after["census"],
    }, indent=2, sort_keys=True) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic)
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"SEMANTIC={semantic}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=("prepare", "record"))
    args = ap.parse_args()
    return prepare() if args.action == "prepare" else record()


if __name__ == "__main__":
    sys.exit(main())
