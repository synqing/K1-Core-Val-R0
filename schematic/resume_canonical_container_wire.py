#!/usr/bin/env python3
"""Resume a canonical container transaction after a pin-alias mapping repair."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


REPO = Path("/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0")
CONTAINER_EXECUTOR = REPO / "schematic/execute_canonical_container.py"


def load_container_executor():
    spec = importlib.util.spec_from_file_location("canonical_container", CONTAINER_EXECUTOR)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load canonical container executor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("container", type=int, choices=range(2, 11))
    ap.add_argument("--transaction-id", required=True)
    args = ap.parse_args()

    canonical = load_container_executor()
    base = canonical.load_fixture_executor()
    plan, layout = canonical.build_canonical_inputs()
    base.PLAN = canonical.CANONICAL_PLAN
    base.LAYOUT = canonical.CANONICAL_LAYOUT
    base.assert_identity()

    state = json.loads(base.MUTATION_STATE.read_text())
    active = state.get("active_transaction") or {}
    if state.get("state") != "IN_FLIGHT" or active.get("transaction_id") != args.transaction_id:
        raise SystemExit(f"expected active transaction {args.transaction_id}, found {state.get('state')} {active.get('transaction_id')}")
    before = json.loads((REPO / active["snapshot_path"]).read_text())

    blocks = [key for key, value in layout["domains"].items() if int(value["container"]) == args.container]
    blocks.sort(key=lambda key: int(layout["domains"][key]["sequence"]))
    component_map = {c["ref"]: c for c in plan["components"]}
    refs = [ref for block in blocks for ref in next(b for b in plan["blocks"] if b["id"] == block)["component_refs"]]
    suffix = canonical.SUFFIX_BY_CONTAINER[args.container]
    designators = {ref: f"{ref}-{suffix}" for ref in refs}
    pids = json.loads((canonical.JOBS / f"container-{args.container}-pids.json").read_text())
    unit_specs = [unit for block in blocks for unit in (layout["domains"][block].get("additional_units") or [])]
    pin_tags = refs + [unit["tag"] for unit in unit_specs]

    pin_results = base.run_batch([
        {"tool": "list_schematic_component_pins", "tag": tag,
         "args": {"componentPrimitiveId": pids[tag], "expectedDocumentUuid": canonical.PAGE}}
        for tag in pin_tags
    ], f"container-{args.container}-pins-resume")
    live = base.parse_live_pins(pin_results)
    unit_tags = {ref: [ref] for ref in refs}
    for unit in unit_specs:
        unit_tags[unit["ref"]].append(unit["tag"])
    connections = {tag: [] for tags in unit_tags.values() for tag in tags}
    seen = set()

    for block in blocks:
        block_refs = set(next(b for b in plan["blocks"] if b["id"] == block)["component_refs"])
        for net in plan["nets"]:
            for ep in net["endpoints"]:
                if ep["ref"] not in block_refs:
                    continue
                ref = ep["ref"]
                wanted = ep.get("pin_name") or ep.get("pin")
                skip_key = (ref, str(ep.get("pin") or wanted))
                if skip_key in base.SKIP_PINS.get(block, set()):
                    continue
                remap = base.PIN_REMAP.get(block, {}).get((ref, str(ep.get("pin") or wanted)))
                chosen_tag = None
                number = None
                for tag in unit_tags[ref]:
                    number = base.map_pin(live.get(tag) or [], remap or wanted)
                    if not number and not remap and ep.get("pin") and str(ep.get("pin")) != str(wanted):
                        number = base.map_pin(live.get(tag) or [], str(ep.get("pin")))
                    if number:
                        chosen_tag = tag
                        break
                if not chosen_tag or not number:
                    names = [p.get("pinName") or p.get("name") for tag in unit_tags[ref] for p in (live.get(tag) or [])]
                    raise SystemExit(f"cannot map {block} {ref}.{wanted}; live names={names}")
                key = (chosen_tag, str(number), net["name"])
                if key not in seen:
                    seen.add(key)
                    connections[chosen_tag].append({"pinNumber": str(number), "net": net["name"]})
        for ref, extras in base.BLOCK_EXTRAS.get(block, {}).items():
            for number, net_name in extras:
                chosen_tag = next((tag for tag in unit_tags[ref] if base.map_pin(live.get(tag) or [], str(number))), None)
                if not chosen_tag:
                    raise SystemExit(f"cannot map required extra {block} {ref}.{number}")
                key = (chosen_tag, str(number), net_name)
                if key not in seen:
                    seen.add(key)
                    connections[chosen_tag].append({"pinNumber": str(number), "net": net_name})

    wired = [tag for tag in pin_tags if connections[tag]]
    base.run_batch([
        {"tool": "connect_schematic_pins_to_nets", "tag": tag,
         "args": {"componentPrimitiveId": pids[tag], "connections": connections[tag],
                  "saveAfter": index == len(wired) - 1, "expectedDocumentUuid": canonical.PAGE}}
        for index, tag in enumerate(wired)
    ], f"container-{args.container}-wire-resume")
    saved = base.mcp_call("save_active_document", {"expectedDocumentUuid": canonical.PAGE}).get("saved") is True
    if not saved:
        raise SystemExit("explicit canonical save was not confirmed")
    after = base.source_snapshot()
    missing = [designators[ref] for ref in refs if designators[ref] not in after["census"]["designators"]]
    if missing:
        raise SystemExit(f"designators missing after resume: {missing}")

    semantic_path = canonical.JOBS / f"{args.transaction_id}-semantic.json"
    semantic = {
        "schema_version": 1, "transaction_id": args.transaction_id,
        "project_uuid": canonical.PROJECT, "document_uuid": canonical.PAGE,
        "scope": f"CONTAINER_{args.container}", "stage": "place",
        "intended_delta": active["intended_delta"],
        "pre_source_hash": before["source_hash"], "post_source_hash": after["source_hash"],
        "saved": True, "affected": [designators[ref] for ref in refs],
        "census": after["census"], "blocks": blocks,
    }
    semantic_path.write_text(json.dumps(semantic, indent=2, sort_keys=True) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic_path)
    print(f"CONTAINER={args.container}")
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"SEMANTIC={semantic_path}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
