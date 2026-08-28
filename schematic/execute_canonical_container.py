#!/usr/bin/env python3
"""Populate one Captain-authored canonical domain box as one visual transaction."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


REPO = Path("/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0")
FIXTURE_EXECUTOR = REPO / "schematic/single-sheet-qualification/execute_fixture_block.py"
FIXTURE_PLAN = REPO / "schematic/single-sheet-qualification/FIXTURE-PLAN.json"
FIXTURE_LAYOUT = REPO / "schematic/single-sheet-qualification/LAYOUT-PLAN.json"
EVIDENCE = REPO / "evidence/VAL-G2-2026-08-28/canonical-core-val-r0"
JOBS = EVIDENCE / "jobs"
SNAPSHOTS = EVIDENCE / "snapshots"
CANONICAL_PLAN = EVIDENCE / "canonical-plan.json"
CANONICAL_LAYOUT = EVIDENCE / "canonical-layout.json"
PROJECT = "64325d0e55e0435abd018defb0089a9b"
PAGE = "1435cb46f39e48c8a8aadbb84ca81603"
FORBIDDEN_QUALIFICATION_PROJECT = "09e9c541fd3d404082d4b92e55ae5336"
OFFSET_X = 65
OFFSET_Y = 3440
SUFFIX_BY_CONTAINER = {
    1: "PWR1", 2: "PWR2", 3: "RTC", 4: "RTDBG", 5: "ESP",
    6: "AUD", 7: "NFC", 8: "MOT", 9: "LED", 10: "VAL",
}


def load_fixture_executor():
    spec = importlib.util.spec_from_file_location("fixture_executor", FIXTURE_EXECUTOR)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load fixture executor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.PROJECT = PROJECT
    module.PAGE = PAGE
    module.ABANDONED = FORBIDDEN_QUALIFICATION_PROJECT
    module.JOBS = JOBS
    module.SNAPSHOTS = SNAPSHOTS
    module.MUTATION_STATE = EVIDENCE / "MUTATION-STATE.json"
    module.MUTATION_LEDGER = EVIDENCE / "MUTATION-LEDGER.jsonl"
    return module


def build_canonical_inputs() -> tuple[dict, dict]:
    plan = json.loads(FIXTURE_PLAN.read_text())
    keep = {c["ref"] for c in plan["components"] if c.get("fixture_only") is False}
    plan["components"] = [c for c in plan["components"] if c["ref"] in keep]
    for block in plan["blocks"]:
        block["component_refs"] = [ref for ref in block["component_refs"] if ref in keep]
    for net in plan["nets"]:
        net["endpoints"] = [ep for ep in net["endpoints"] if ep["ref"] in keep]
    plan["nets"] = [net for net in plan["nets"] if net["endpoints"]]
    plan["planned_symbols"] = len(keep)
    plan["canonical_source"] = "FIXTURE-PLAN source-derived components with fixture_only parts removed"

    layout = json.loads(FIXTURE_LAYOUT.read_text())
    for key, domain in layout["domains"].items():
        container = int(domain["container"])
        domain["suffix"] = SUFFIX_BY_CONTAINER[container]
        domain["parts"] = {
            ref: [xy[0] + OFFSET_X, xy[1] + OFFSET_Y]
            for ref, xy in domain["parts"].items() if ref in keep
        }
        for unit in domain.get("additional_units") or []:
            unit["x"] += OFFSET_X
            unit["y"] += OFFSET_Y
        if domain.get("title"):
            domain["title"][0] += OFFSET_X
            domain["title"][1] += OFFSET_Y
        for axis in ("x1", "x2"):
            domain["box"][axis] += OFFSET_X
        for axis in ("y1", "y2"):
            domain["box"][axis] += OFFSET_Y
    for key, container in layout["containers"].items():
        number = int(key)
        container["suffix"] = SUFFIX_BY_CONTAINER[number]
        container["x1"] += OFFSET_X
        container["x2"] += OFFSET_X
        container["y1"] += OFFSET_Y
        container["y2"] += OFFSET_Y

    JOBS.mkdir(parents=True, exist_ok=True)
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    CANONICAL_PLAN.write_text(json.dumps(plan, indent=2) + "\n")
    CANONICAL_LAYOUT.write_text(json.dumps(layout, indent=2) + "\n")
    return plan, layout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("container", type=int, choices=range(2, 11))
    ap.add_argument("--transaction-id", required=True)
    args = ap.parse_args()

    base = load_fixture_executor()
    plan, layout = build_canonical_inputs()
    base.PLAN = CANONICAL_PLAN
    base.LAYOUT = CANONICAL_LAYOUT
    base.assert_identity()
    # This is canonical capture, not the rejected disposable qualification
    # fixture.  The qualification-only 120-net count floor must never force
    # fictional nets back into the production schematic.  Canonical input is
    # instead constrained below by the source-derived, fixture_only=False set.
    if not plan["components"] or any(c.get("fixture_only") is not False for c in plan["components"]):
        raise SystemExit("canonical input must contain a non-empty source-derived component set only")

    blocks = [key for key, value in layout["domains"].items() if int(value["container"]) == args.container]
    blocks.sort(key=lambda key: int(layout["domains"][key]["sequence"]))
    component_map = {c["ref"]: c for c in plan["components"]}
    refs = [ref for block in blocks for ref in next(b for b in plan["blocks"] if b["id"] == block)["component_refs"]]
    if len(refs) != len(set(refs)):
        raise SystemExit(f"duplicate component refs in container {args.container}")
    suffix = SUFFIX_BY_CONTAINER[args.container]
    designators = {ref: f"{ref}-{suffix}" for ref in refs}
    title_domain = next((layout["domains"][block] for block in blocks if layout["domains"][block].get("title")), None)
    intended = f"Populate canonical domain box {args.container} ({', '.join(blocks)}) with source-derived components, domain suffix -{suffix}, functional net endpoints and one readable title"

    base.validate_repository_state(base.MUTATION_STATE, base.MUTATION_LEDGER)
    before = base.source_snapshot()
    snapshot_path = SNAPSHOTS / f"{args.transaction_id}-before.json"
    snapshot_path.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")
    base.begin_transaction(
        base.MUTATION_STATE,
        base.MUTATION_LEDGER,
        transaction_id=args.transaction_id,
        project_uuid=PROJECT,
        document_uuid=PAGE,
        scope=f"CONTAINER_{args.container}",
        stage="place",
        kind="normal",
        intended_delta=intended,
        snapshot_path=snapshot_path,
        expected_checks=[
            "domain title is visible and correct",
            "all source-derived components fit inside the declared box",
            "all component designators carry the declared suffix",
            "no duplicates overlaps fixture padding or unrelated movement",
        ],
    )

    place_jobs = []
    unit_specs = []
    for block in blocks:
        coords = layout["domains"][block]
        for ref in next(b for b in plan["blocks"] if b["id"] == block)["component_refs"]:
            component = component_map[ref]
            binding = json.loads(base.BIND.read_text())["binds"].get(component["manufacturer_part_number"])
            if not binding:
                raise SystemExit(f"unbound MPN {component['manufacturer_part_number']} for {ref}")
            x, y = coords["parts"][ref]
            place_jobs.append({
                "tool": "add_schematic_component", "tag": ref,
                "args": {
                    "deviceUuid": binding["deviceUuid"], "x": x, "y": y, "rotation": 0,
                    "addIntoBom": True, "addIntoPcb": True, "saveAfter": False,
                    "expectedDocumentUuid": PAGE,
                },
            })
        for unit in coords.get("additional_units") or []:
            ref = unit["ref"]
            component = component_map[ref]
            binding = json.loads(base.BIND.read_text())["binds"].get(component["manufacturer_part_number"])
            if not binding:
                raise SystemExit(f"unbound MPN {component['manufacturer_part_number']} for {unit['tag']}")
            unit_specs.append(unit)
            place_jobs.append({
                "tool": "add_schematic_component", "tag": unit["tag"],
                "args": {
                    "deviceUuid": binding["deviceUuid"], "subPartName": unit["sub_part_name"],
                    "x": unit["x"], "y": unit["y"], "rotation": 0,
                    "addIntoBom": False, "addIntoPcb": True, "saveAfter": False,
                    "expectedDocumentUuid": PAGE,
                },
            })
    if title_domain:
        title = title_domain["title"]
        place_jobs.append({
            "tool": "add_schematic_text", "tag": f"title-container-{args.container}",
            "args": {
                "x": title[0], "y": title[1], "content": title[2], "fontSize": 18,
                "bold": True, "textColor": "#B00020", "saveAfter": True,
                "expectedDocumentUuid": PAGE,
            },
        })
    else:
        place_jobs[-1]["args"]["saveAfter"] = True
    pids = base.extract_pids(base.run_batch(place_jobs, f"container-{args.container}-place"))
    missing = [tag for tag in refs + [unit["tag"] for unit in unit_specs] if tag not in pids]
    if missing:
        raise SystemExit(f"placement missing primitive IDs: {missing}")
    (JOBS / f"container-{args.container}-pids.json").write_text(json.dumps(pids, indent=2) + "\n")

    designate_jobs = []
    for ref in refs:
        component = component_map[ref]
        designate_jobs.append({
            "tool": "modify_schematic_component", "tag": ref,
            "args": {
                "primitiveId": pids[ref], "designator": designators[ref],
                "name": component.get("value") or component["manufacturer_part_number"],
                "manufacturerId": component["manufacturer_part_number"], "addIntoPcb": True,
                "saveAfter": False, "expectedDocumentUuid": PAGE,
            },
        })
    for unit in unit_specs:
        ref = unit["ref"]
        component = component_map[ref]
        designate_jobs.append({
            "tool": "modify_schematic_component", "tag": unit["tag"],
            "args": {
                "primitiveId": pids[unit["tag"]], "designator": designators[ref],
                "name": component.get("value") or component["manufacturer_part_number"],
                "manufacturerId": component["manufacturer_part_number"], "addIntoBom": False,
                "addIntoPcb": True, "saveAfter": False, "expectedDocumentUuid": PAGE,
            },
        })
    designate_jobs[-1]["args"]["saveAfter"] = True
    base.run_batch(designate_jobs, f"container-{args.container}-designate")

    pin_tags = refs + [unit["tag"] for unit in unit_specs]
    pin_results = base.run_batch([
        {"tool": "list_schematic_component_pins", "tag": tag,
         "args": {"componentPrimitiveId": pids[tag], "expectedDocumentUuid": PAGE}}
        for tag in pin_tags
    ], f"container-{args.container}-pins")
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
                    raise SystemExit(f"cannot map {block} {ref}.{wanted} to a live pin")
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
    wire_jobs = [
        {"tool": "connect_schematic_pins_to_nets", "tag": tag,
         "args": {"componentPrimitiveId": pids[tag], "connections": connections[tag],
                  "saveAfter": index == len(wired) - 1, "expectedDocumentUuid": PAGE}}
        for index, tag in enumerate(wired)
    ]
    if wire_jobs:
        base.run_batch(wire_jobs, f"container-{args.container}-wire")
    saved = base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE}).get("saved") is True
    if not saved:
        raise SystemExit("explicit canonical save was not confirmed")

    after = base.source_snapshot()
    missing_designators = [designators[ref] for ref in refs if designators[ref] not in after["census"]["designators"]]
    if missing_designators:
        raise SystemExit(f"designators missing from source read-back: {missing_designators}")
    semantic_path = JOBS / f"{args.transaction_id}-semantic.json"
    semantic = {
        "schema_version": 1, "transaction_id": args.transaction_id,
        "project_uuid": PROJECT, "document_uuid": PAGE,
        "scope": f"CONTAINER_{args.container}", "stage": "place",
        "intended_delta": intended, "pre_source_hash": before["source_hash"],
        "post_source_hash": after["source_hash"], "saved": True,
        "affected": [designators[ref] for ref in refs], "census": after["census"],
        "blocks": blocks,
    }
    semantic_path.write_text(json.dumps(semantic, indent=2, sort_keys=True) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic_path)
    print(f"CONTAINER={args.container}")
    print(f"BLOCKS={','.join(blocks)}")
    print(f"COMPONENTS={len(refs)}")
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"SEMANTIC={semantic_path}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
