#!/usr/bin/env python3
"""Reconcile the timed-out POWER_BUCK transaction with one guarded source write."""
from __future__ import annotations

import argparse
import json
import sys

from execute_canonical_container import JOBS, PAGE, PROJECT, SNAPSHOTS, load_fixture_executor
from repair_power_buck import TX, component_records


OLD = {"e2050", "e1834"}
NEW_L1 = "e24569"
NEW_C10 = "e24607"
PAYLOAD = JOBS / f"{TX}-reconcile-payload.json"
CURRENT_SNAPSHOT = SNAPSHOTS / f"{TX}-after-timeout-before-source-reconcile.json"


def rows(source: str) -> list[list]:
    return [json.loads(line) for line in source.splitlines() if line.strip()]


def belongs(record: list, roots: set[str]) -> bool:
    record_id = record[1] if len(record) > 1 and isinstance(record[1], str) else None
    parent_id = record[2] if record and record[0] == "ATTR" and len(record) > 2 else None
    return record_id in roots or parent_id in roots


def wire_net_map(all_rows: list[list]) -> dict[str, str]:
    return {
        str(record[2]): str(record[4])
        for record in all_rows
        if record[0] == "ATTR" and len(record) > 4 and record[3] == "NET"
    }


def prepare() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    state = json.loads(base.MUTATION_STATE.read_text())
    active = state.get("active_transaction") or {}
    if state.get("state") != "IN_FLIGHT" or active.get("transaction_id") != TX:
        raise SystemExit(f"expected in-flight {TX}, found {state.get('state')} {active.get('transaction_id')}")
    current = base.source_snapshot()
    CURRENT_SNAPSHOT.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
    all_rows = rows(current["source"])
    record_ids = {str(r[1]) for r in all_rows if len(r) > 1 and isinstance(r[1], str)}
    required = OLD | {NEW_L1, NEW_C10}
    if required - record_ids:
        raise SystemExit(f"required repair roots missing: {sorted(required - record_ids)}")

    output: list[list] = []
    for record in all_rows:
        if belongs(record, OLD):
            continue
        if record[0] == "ATTR" and len(record) > 4 and record[2] == NEW_L1:
            if record[3] == "Designator":
                record[4] = "L1-PWR2"
            elif record[3] == "Name":
                record[4] = "2.2uH"
        if record[0] == "ATTR" and len(record) > 4 and record[2] == NEW_C10:
            if record[3] == "Designator":
                record[4] = "C10-PWR2"
            elif record[3] == "Name":
                record[4] = "100nF"
        output.append(record)

    head = next((record for record in output if record[0] == "HEAD"), None)
    if not head or not isinstance(head[1], dict):
        raise SystemExit("schematic HEAD record missing")
    max_id = int(head[1].get("maxId") or 0)
    additions = [
        ("3V3", [[1715, 4520, 1735, 4520]]),
        ("GND", [[1875, 4510, 1855, 4510]]),
        ("5V_SYS", [[1875, 4540, 1855, 4540]]),
    ]
    existing_wires = {
        json.dumps(record[2], separators=(",", ":"))
        for record in output if record[0] == "WIRE"
    }
    for net_name, points in additions:
        key = json.dumps(points, separators=(",", ":"))
        if key in existing_wires:
            raise SystemExit(f"wire already exists at intended U3 endpoint: {net_name} {points}")
        max_id += 1
        wire_id = f"e{max_id}"
        output.append(["WIRE", wire_id, points, "st11", 0])
        max_id += 1
        attr_id = f"e{max_id}"
        x1, y1, x2, y2 = points[0]
        output.append(["ATTR", attr_id, wire_id, "NET", net_name, 0, 1,
                       (x1 + x2) / 2, (y1 + y2) / 2, 0, "st4", 0])
    head[1]["maxId"] = max_id

    if sum(record[0] == "COMPONENT" for record in output) != 183:
        raise SystemExit("reconciled source must contain 183 total components including frame")
    if sum(record[0] == "RECT" for record in output) != 10:
        raise SystemExit("reconciled source must preserve the ten domain rectangles")
    designators = [str(record[4]) for record in output
                   if record[0] == "ATTR" and len(record) > 4 and record[3] == "Designator"]
    if designators.count("L1-PWR2") != 1 or designators.count("C10-PWR2") != 1:
        raise SystemExit("replacement buck designators are not unique")
    if "L?" in designators or "C?" in designators:
        raise SystemExit("unassigned replacement designator survived reconciliation")
    net_map = wire_net_map(output)
    for net_name, points in additions:
        matching = [record for record in output if record[0] == "WIRE" and record[2] == points]
        if len(matching) != 1 or net_map.get(str(matching[0][1])) != net_name:
            raise SystemExit(f"failed to materialise {net_name} at {points}")

    payload = {
        "source": "\n".join(json.dumps(record, separators=(",", ":")) for record in output),
        "expectedSourceHash": current["source_hash"],
        "expectedDocumentUuid": PAGE,
        "skipConfirmation": True,
    }
    PAYLOAD.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"CURRENT_SOURCE_HASH={current['source_hash']}")
    print(f"PAYLOAD={PAYLOAD}")
    return 0


def record() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    before = json.loads((SNAPSHOTS / f"{TX}-before.json").read_text())
    after = base.source_snapshot()
    all_rows = rows(after["source"])
    roots = component_records(after["source"])
    if any(root in {str(record[1]) for record in all_rows if len(record) > 1 and isinstance(record[1], str)}
           for root in OLD):
        raise SystemExit("old buck component root survived source reconciliation")
    if roots.get("L1-PWR2", {}).get("primitive_id") != NEW_L1:
        raise SystemExit("L1-PWR2 did not resolve to the replacement inductor")
    if roots.get("C10-PWR2", {}).get("primitive_id") != NEW_C10:
        raise SystemExit("C10-PWR2 did not resolve to the replacement capacitor")
    net_map = wire_net_map(all_rows)
    expected = {
        json.dumps([[1715, 4520, 1735, 4520]], separators=(",", ":")): "3V3",
        json.dumps([[1875, 4510, 1855, 4510]], separators=(",", ":")): "GND",
        json.dumps([[1875, 4540, 1855, 4540]], separators=(",", ":")): "5V_SYS",
    }
    observed = {}
    for record in all_rows:
        if record[0] == "WIRE":
            key = json.dumps(record[2], separators=(",", ":"))
            if key in expected:
                observed[key] = net_map.get(str(record[1]))
    if observed != expected:
        raise SystemExit(f"U3 fixed-pin net read-back mismatch: {observed}")
    semantic_path = JOBS / f"{TX}-semantic.json"
    semantic_path.write_text(json.dumps({
        "schema_version": 1,
        "transaction_id": TX,
        "project_uuid": PROJECT,
        "document_uuid": PAGE,
        "scope": "POWER_BUCK",
        "stage": "repair",
        "intended_delta": ("Correct the TPS62913 5 V to 3.3 V circuit in domain box 2: replace L1 with a "
                           "2.2 uH XGL4030-222MEC, replace C10 with 100 nF, and connect VO to 3V3, "
                           "PSNS to GND and S-CONF to 5V_SYS"),
        "pre_source_hash": before["source_hash"],
        "post_source_hash": after["source_hash"],
        "saved": True,
        "affected": ["U3-PWR2", "L1-PWR2", "C10-PWR2"],
        "replacement_primitive_ids": {"L1": NEW_L1, "C10": NEW_C10},
        "fixed_pin_nets": {"U3.3.VO": "3V3", "U3.7.PSNS": "GND", "U3.10.S-CONF": "5V_SYS"},
        "census": after["census"],
    }, indent=2, sort_keys=True) + "\n")
    pids_path = JOBS / "container-2-pids.json"
    pids = json.loads(pids_path.read_text())
    pids.update({"L1": NEW_L1, "C10": NEW_C10})
    pids_path.write_text(json.dumps(pids, indent=2, sort_keys=True) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic_path)
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"SEMANTIC={semantic_path}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=("prepare", "record"))
    args = ap.parse_args()
    return prepare() if args.action == "prepare" else record()


if __name__ == "__main__":
    sys.exit(main())
