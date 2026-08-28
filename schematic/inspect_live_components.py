#!/usr/bin/env python3
"""Read back selected canonical EasyEDA schematic components and their live pins."""
from __future__ import annotations

import argparse
import json
import sys

from execute_canonical_container import PAGE, load_fixture_executor
from repair_power_buck import component_records


def records(source: str) -> list[list]:
    return [json.loads(line) for line in source.splitlines() if line.strip()]


def endpoint_net_map(source: str) -> dict[tuple[int, int], list[str]]:
    rows = records(source)
    wire_nets = {
        str(row[2]): str(row[4])
        for row in rows
        if row[0] == "ATTR" and len(row) > 4 and row[3] == "NET"
    }
    endpoints: dict[tuple[int, int], set[str]] = {}
    for row in rows:
        if row[0] != "WIRE":
            continue
        net = wire_nets.get(str(row[1]))
        if not net:
            continue
        for x1, y1, x2, y2 in row[2]:
            endpoints.setdefault((int(x1), int(y1)), set()).add(net)
            endpoints.setdefault((int(x2), int(y2)), set()).add(net)
    return {point: sorted(nets) for point, nets in endpoints.items()}


def component_attributes(source: str, primitive_id: str) -> dict[str, str]:
    return {
        str(row[3]): str(row[4])
        for row in records(source)
        if row[0] == "ATTR" and len(row) > 4 and str(row[2]) == primitive_id
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("designator", nargs="+")
    args = parser.parse_args()

    base = load_fixture_executor()
    base.assert_identity()
    snapshot = base.source_snapshot()
    live = component_records(snapshot["source"])
    missing = [designator for designator in args.designator if designator not in live]
    if missing:
        raise SystemExit(f"missing live designators: {missing}")

    results = base.run_batch([
        {
            "tool": "list_schematic_component_pins",
            "tag": designator,
            "args": {
                "componentPrimitiveId": live[designator]["primitive_id"],
                "expectedDocumentUuid": PAGE,
            },
        }
        for designator in args.designator
    ], "canonical-live-component-inspection")
    pins = base.parse_live_pins(results)
    nets = endpoint_net_map(snapshot["source"])
    for designator, component_pins in pins.items():
        for pin in component_pins:
            point = (int(round(float(pin["x"]))), int(round(-float(pin["y"]))))
            pin["net_names"] = nets.get(point, [])

    output = {
        "project_uuid": base.PROJECT,
        "document_uuid": PAGE,
        "source_hash": snapshot["source_hash"],
        "components": {
            designator: {
                **live[designator],
                "attributes": component_attributes(
                    snapshot["source"], live[designator]["primitive_id"]
                ),
                "pins": pins[designator],
            }
            for designator in args.designator
        },
    }
    json.dump(output, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
