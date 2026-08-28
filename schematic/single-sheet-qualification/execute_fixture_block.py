#!/usr/bin/env python3
"""Place one Option-C fixture block from FIXTURE-PLAN.json onto the live EasyEDA sheet.

One visually atomic block per invocation. Never invent QUAL/CIRCUIT_PATH nets.
Plan device_uuid values are md5 keys — use library-bind-map.json live UUIDs.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0")
sys.path.insert(0, str(REPO / "harness"))

from easyeda_mutation_gate import (  # noqa: E402 - repo path is established above
    GateError,
    begin_transaction,
    record_mutation,
    validate_repository_state,
)

PLAN = REPO / "schematic/single-sheet-qualification/FIXTURE-PLAN.json"
LAYOUT = REPO / "schematic/single-sheet-qualification/LAYOUT-PLAN.json"
BIND = REPO / "evidence/VAL-G2-2026-08-28/jobs/library-bind-map.json"
JOBS = REPO / "evidence/VAL-G2-2026-08-28/jobs"
SNAPSHOTS = REPO / "evidence/VAL-G2-2026-08-28/snapshots"
MUTATION_STATE = REPO / "evidence/VAL-G2-2026-08-28/EASYEDA-MUTATION-STATE.json"
MUTATION_LEDGER = REPO / "evidence/VAL-G2-2026-08-28/EASYEDA-MUTATION-LEDGER.jsonl"
MCP = Path("/Users/spectrasynq/SpectraSynq-EDA/EasyEDA-MCP")
BATCH = MCP / "tools/mcp_batch.mjs"
CALL = MCP / "tools/mcp_http_call.mjs"

PROJECT = "09e9c541fd3d404082d4b92e55ae5336"
PAGE = "1991698f35bf4c09b8de4bcf78bd2b7b"
ABANDONED = "64325d0e55e0435abd018defb0089a9b"
MUTATING_STAGES = {"place", "designate", "wire"}
EXPECTED_VISUAL_CHECKS = [
    "declared block visible at useful scale",
    "no duplicates placeholders or undesignated debris",
    "changed labels pins and geometry readable",
    "no unrelated movement additions or deletions",
]

PIN_ALIASES = {
    "ILIM": ["ILIM", "ILM"],
    "ILM": ["ILIM", "ILM"],
    "EN": ["EN", "EN/SYNC", "EN_SYNC", "EN/UVLO", "EN_UVLO", "ENABLE"],
    "EN/UVLO": ["EN", "EN/UVLO", "EN_UVLO"],
    "SS": ["SS", "NR/SS", "NR_SS", "SOFTSTART", "SOFT_START"],
    "IN": ["IN", "VIN", "IN+"],
    "OUT": ["OUT", "VOUT", "VO", "OUT+"],
    "GND": ["GND", "PGND", "AGND", "VSS", "GND1"],
    "VSS": ["VSS", "GND"],
    "CS": ["CS", "CS#"],
    "CS#": ["CS", "CS#"],
    "SI": ["SI", "SI(IO0)", "IO0"],
    "SO": ["SO", "SO(IO1)", "IO1"],
    "WP": ["WP", "WP#", "WP#(IO2)"],
    "WP#": ["WP", "WP#", "WP#(IO2)"],
    "SCK": ["SCK", "CLK"],
    "SCL": ["SCL", "SCLK/SCL", "SCL/SPC"],
    "SDA": ["SDA", "MISO/SDA", "SDA/SDI/SDO"],
    "VSP_A": ["VSP_A", "VDD_TX"],
    "VTref": ["VTREF", "VTref", "VCC", "3V3", "1"],
    "SWCLK": ["SWCLK", "SWDCLK", "TCK", "4"],
    "SWDIO": ["SWDIO", "TMS", "2"],
    "nRESET": ["NRESET", "RESET", "NRST", "RESET#", "10"],
    "TX": ["TX", "TXD", "TXD0"],
    "RX": ["RX", "RXD", "RXD0"],
    "USB_D+": ["USB_D+", "USBDP", "DP", "IO20"],
    "USB_D-": ["USB_D-", "USBDM", "DM", "IO19"],
    "USB_D_P": ["USB_D+", "USBDP", "IO20"],
    "USB_D_N": ["USB_D-", "USBDM", "IO19"],
    "DP": ["DP", "DP1", "D+"],
    "DM": ["DM", "DN1", "D-", "DN"],
    "S": ["S", "SOURCE", "1"],
    "D": ["D", "DRAIN", "3"],
    "G": ["G", "GATE", "2"],
}

# Datasheet-mandatory extras that the 2-terminal plan abstracted. Never QUAL nets.
BLOCK_EXTRAS = {
    "NFC": {
        "U12": [
            ("1", "3V3"), ("6", "GND"), ("10", "NFC_5V"),
            ("12", "GND"), ("16", "GND"), ("21", "GND"),
            ("26", "GND"), ("33", "GND"),
            ("3", "NFC_VDD_D"), ("7", "NFC_VDD_A"),
            ("9", "NFC_VDD_RF"), ("11", "NFC_VDD_AM"),
            ("14", "NFC_VDD_DR"), ("24", "NFC_AGDC"),
        ],
    },
    "POWER_LED": {
        "U4": [("1", "5V_SYS")],  # EN/UVLO always-on from VIN rail
    },
    "POWER_BRANCH": {
        "U5": [("3", "5V_SYS")],  # LDO EN always-on
    },
    "RT_CLOCK_MEM": {
        "Y1": [("2", "GND"), ("4", "GND")],  # 4-pad crystal: 2/4 are GND, 1/3 are the crystal
        "U8": [("7", "3V3")],  # HOLD#/RESET# pulled up
    },
    "ESP_CORE": {
        "U9": [("40", "GND"), ("41", "GND")],  # extra module GND balls
    },
    "ESP_USB": {
        "U10": [("5", "S3_VBUS")],  # USBLC6 Vcc
        "J7": [
            ("A12", "GND"),
            ("B1", "GND"),
            ("B12", "GND"),
            ("A9", "S3_VBUS"),
            ("B4", "S3_VBUS"),
            ("B9", "S3_VBUS"),
            ("B6", "USB_DP"),
            ("B7", "USB_DM"),
        ],
    },
}

# Library symbols that omit a plan pin. Never invent QUAL nets; leave the pin unwired.
SKIP_PINS = {
    "ESP_CORE": {("U9", "VBUS")},  # WROOM schematic symbol has no VBUS ball
    "K1BR": {("TP1", "2"), ("TP2", "2")},  # library test points are 1-pin
}

# Plan pin numbers that are wrong against the live library symbol.
PIN_REMAP = {
    "RT_CLOCK_MEM": {
        ("Y1", "2"): "3",  # plan XTALO on pin 2; live pin 2 is GND, pin 3 is XTALO
    },
    "ESP_USB": {
        ("U10", "GND"): "2",
        ("U10", "I_1"): "1",
        ("U10", "I_2"): "3",
        ("U10", "O_1"): "6",
        ("U10", "O_2"): "4",
    },
}


def run_batch(jobs: list, stem: str) -> list:
    job_path = JOBS / f"{stem}.json"
    res_path = JOBS / f"{stem}.results.json"
    job_path.write_text(json.dumps(jobs, indent=2) + "\n")
    proc = subprocess.run(
        ["node", str(BATCH), str(job_path), str(res_path)],
        cwd=str(MCP),
        capture_output=True,
        text=True,
        timeout=240,
    )
    if proc.returncode != 0:
        print(proc.stdout[-2000:])
        print(proc.stderr[-2000:])
        raise SystemExit(f"mcp_batch failed {stem} rc={proc.returncode}")
    results = json.loads(res_path.read_text())
    bad = [r for r in results if not r.get("ok")]
    if bad:
        print(json.dumps(bad, indent=2)[:3000])
        raise SystemExit(f"{stem}: {len(bad)} jobs failed")
    return results


def mcp_call(tool: str, args: dict, timeout: int = 40) -> dict:
    proc = subprocess.run(
        ["node", str(CALL), tool, json.dumps(args)],
        cwd=str(MCP),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    text = (proc.stdout + proc.stderr).strip()
    i = text.find("{")
    if i < 0:
        raise SystemExit(f"{tool} no json: {text[:400]}")
    return json.loads(text[i:])


def assert_identity() -> None:
    ctx = mcp_call("get_current_context", {})
    p = ctx.get("currentProject") or {}
    d = ctx.get("currentDocument") or {}
    print(
        "IDENTITY",
        p.get("uuid"),
        p.get("friendlyName"),
        d.get("uuid"),
        d.get("documentType"),
    )
    if p.get("uuid") == ABANDONED:
        raise SystemExit("HARD STOP: abandoned project is active")
    if p.get("uuid") != PROJECT or d.get("uuid") != PAGE or d.get("documentType") != 1:
        raise SystemExit(
            f"HARD STOP: identity mismatch project={p.get('uuid')} doc={d.get('uuid')} type={d.get('documentType')}"
        )


def source_snapshot() -> dict:
    srcd = mcp_call("get_document_source", {})
    src = srcd.get("source") or ""
    placed = sorted(set(re.findall(r'\["ATTR","[^"]+","[^"]+","Designator","([^"]+)"', src)))
    nets = re.findall(r'\["ATTR","[^"]+","[^"]+","NET","([^"]+)"', src)
    from collections import Counter

    return {
        "schema_version": 1,
        "project_uuid": PROJECT,
        "document_uuid": srcd.get("documentUuid") or PAGE,
        "source_hash": srcd.get("sourceHash"),
        "source": src,
        "census": {
            "components": src.count('["COMPONENT"'),
            "wires": src.count('["WIRE"'),
            "texts": src.count('["TEXT"'),
            "rectangles": src.count('["RECT"'),
            "designators": placed,
            "net_counts": dict(Counter(nets)),
        },
    }


def extract_pids(results: list) -> dict[str, str]:
    out = {}
    for r in results:
        tag = r.get("tag")
        prim = (r.get("result") or {}).get("primitive") or {}
        pid = prim.get("primitiveId")
        if tag and pid and not str(tag).startswith("title"):
            out[tag] = pid
    return out


def norm(name: str) -> str:
    # Preserve electrical polarity before punctuation stripping. The old normaliser
    # collapsed VIN+ and VIN- (and D+ and D-) to the same token, so first-match
    # library ordering could silently wire a positive endpoint onto the negative pin.
    value = (name or "").upper().replace("+", "PLUS").replace("-", "MINUS")
    return re.sub(r"[^A-Z0-9]+", "", value)


def map_pin(live_pins: list, wanted: str) -> str | None:
    aliases = PIN_ALIASES.get(wanted, [wanted])
    wanted_n = {norm(a) for a in aliases + [wanted]}
    for p in live_pins:
        n = p.get("pinName") or p.get("name") or ""
        num = str(p.get("pinNumber") or p.get("number") or "")
        live_norm = norm(n)
        # NXP documentation often abbreviates mux pads as SD_B1_07/AD_B0_00,
        # while the EasyEDA DVJ6B symbol carries the full GPIO_SD_B1_07 form.
        # Match only the exact GPIO-prefixed spelling; do not select a different
        # legal mux candidate from a peripheral function name.
        if live_norm in wanted_n or (live_norm.startswith("GPIO") and live_norm[4:] in wanted_n) or num == wanted:
            return num
    # 2-pin passives often expose only numbers
    if wanted in {"1", "2"}:
        return wanted
    return None


def parse_live_pins(pin_results: list) -> dict[str, list]:
    out = {}
    for r in pin_results:
        tag = r.get("tag")
        res = r.get("result") or {}
        pins = res.get("pins") or res.get("data") or res.get("items") or []
        if isinstance(res, dict) and not pins:
            for key in ("result", "payload"):
                inner = res.get(key)
                if isinstance(inner, dict):
                    pins = inner.get("pins") or []
                elif isinstance(inner, list):
                    pins = inner
        out[tag] = pins if isinstance(pins, list) else []
    return out


def assert_fixture_plan() -> None:
    checker = REPO / "harness/check_single_sheet_qualification_plan.py"
    proc = subprocess.run(
        [sys.executable, str(checker)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        print(proc.stdout[-4000:])
        print(proc.stderr[-2000:])
        raise SystemExit("HARD STOP: fixture plan checker rejected the plan")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("block")
    ap.add_argument("--stage", choices=["place", "designate", "pins", "wire"], required=True)
    ap.add_argument("--transaction-id")
    ap.add_argument("--kind", choices=["normal", "repair"], default="normal")
    ap.add_argument("--repairs-transaction-id")
    ap.add_argument("--intent")
    args = ap.parse_args()

    plan = json.loads(PLAN.read_text())
    binds = json.loads(BIND.read_text())["binds"]
    block = next(b for b in plan["blocks"] if b["id"] == args.block)
    refs = list(block["component_refs"])
    comps = {c["ref"]: c for c in plan["components"] if c["ref"] in refs}

    assert_identity()
    assert_fixture_plan()

    if not LAYOUT.is_file():
        raise SystemExit(f"missing canonical layout plan {LAYOUT}")
    layout = json.loads(LAYOUT.read_text())
    if layout.get("coordinate_unit") != "0.01_inch":
        raise SystemExit(f"unexpected layout coordinate unit: {layout.get('coordinate_unit')}")
    block_coords = (layout.get("domains") or {}).get(args.block)
    if not block_coords:
        raise SystemExit(f"no canonical layout for {args.block} in {LAYOUT}")
    domain_suffix = str(block_coords.get("suffix") or "")
    if not re.fullmatch(r"[A-Z0-9]{3,5}", domain_suffix):
        raise SystemExit(
            f"invalid or missing 3-5 character domain suffix for {args.block}: {domain_suffix!r}"
        )
    live_designators = {ref: f"{ref}-{domain_suffix}" for ref in refs}

    slug = args.block.lower().replace("_", "-")

    pre_snapshot = None
    intended_delta = args.intent or (
        f"{args.stage.capitalize()} the complete {args.block} circuit block from FIXTURE-PLAN.json"
    )
    if args.stage in MUTATING_STAGES:
        if not args.transaction_id:
            raise SystemExit("HARD STOP: mutating stages require --transaction-id")
        try:
            validate_repository_state(MUTATION_STATE, MUTATION_LEDGER)
        except GateError as exc:
            raise SystemExit(
                f"HARD STOP: EasyEDA mutation state/ledger validation failed: {exc}"
            ) from exc
        JOBS.mkdir(parents=True, exist_ok=True)
        SNAPSHOTS.mkdir(parents=True, exist_ok=True)
        pre_snapshot = source_snapshot()
        snapshot_path = SNAPSHOTS / f"{args.transaction_id}-before.json"
        snapshot_path.write_text(json.dumps(pre_snapshot, indent=2, sort_keys=True) + "\n")
        try:
            begin_transaction(
                MUTATION_STATE,
                MUTATION_LEDGER,
                transaction_id=args.transaction_id,
                project_uuid=PROJECT,
                document_uuid=PAGE,
                scope=args.block,
                stage=args.stage,
                kind=args.kind,
                intended_delta=intended_delta,
                snapshot_path=snapshot_path,
                expected_checks=EXPECTED_VISUAL_CHECKS,
                repairs_transaction_id=args.repairs_transaction_id,
            )
        except GateError as exc:
            raise SystemExit(f"HARD STOP: EasyEDA mutation gate refused begin: {exc}") from exc

    if args.stage == "place":
        jobs = []
        for ref in refs:
            c = comps[ref]
            mpn = c.get("manufacturer_part_number")
            bind = binds.get(mpn)
            if not bind:
                raise SystemExit(f"unbound MPN {mpn} for {ref}")
            xy = block_coords["parts"][ref]
            jobs.append(
                {
                    "tool": "add_schematic_component",
                    "tag": ref,
                    "args": {
                        "deviceUuid": bind["deviceUuid"],
                        "x": xy[0],
                        "y": xy[1],
                        "rotation": 0,
                        "addIntoBom": True,
                        "addIntoPcb": True,
                        "saveAfter": False,
                        "expectedDocumentUuid": PAGE,
                    },
                }
            )
        for unit in block_coords.get("additional_units") or []:
            ref = unit["ref"]
            c = comps[ref]
            mpn = c.get("manufacturer_part_number")
            bind = binds.get(mpn)
            if not bind:
                raise SystemExit(f"unbound MPN {mpn} for {unit['tag']}")
            jobs.append(
                {
                    "tool": "add_schematic_component",
                    "tag": unit["tag"],
                    "args": {
                        "deviceUuid": bind["deviceUuid"],
                        "subPartName": unit["sub_part_name"],
                        "x": unit["x"],
                        "y": unit["y"],
                        "rotation": 0,
                        "addIntoBom": False,
                        "addIntoPcb": True,
                        "saveAfter": False,
                        "expectedDocumentUuid": PAGE,
                    },
                }
            )
        # Captain supplied the ten canonical domain boxes directly in EasyEDA.
        # Never create, resize or duplicate rectangles from this executor.
        title = block_coords.get("title")
        if title:
            jobs.append(
                {
                    "tool": "add_schematic_text",
                    "tag": f"title-{slug}",
                    "args": {
                        "x": title[0],
                        "y": title[1],
                        "content": title[2],
                        "fontSize": 18,
                        "bold": True,
                        "textColor": "#B00020",
                        "saveAfter": True,
                        "expectedDocumentUuid": PAGE,
                    },
                }
            )
        elif jobs:
            jobs[-1]["args"]["saveAfter"] = True
        results = run_batch(jobs, f"place-{slug}")
        pids = extract_pids(results)
        print("PLACED", pids)
        missing = [r for r in refs if r not in pids]
        missing.extend(
            unit["tag"]
            for unit in block_coords.get("additional_units") or []
            if unit["tag"] not in pids
        )
        if missing:
            raise SystemExit(f"place missing primitiveIds: {missing}")
        (JOBS / f"pids-{slug}.json").write_text(json.dumps(pids, indent=2) + "\n")

    pids = json.loads((JOBS / f"pids-{slug}.json").read_text())

    if args.stage == "designate":
        jobs = []
        for i, ref in enumerate(refs):
            c = comps[ref]
            jobs.append(
                {
                    "tool": "modify_schematic_component",
                    "tag": ref,
                    "args": {
                        "primitiveId": pids[ref],
                        "designator": live_designators[ref],
                        "name": c.get("value") or c.get("manufacturer_part_number"),
                        "manufacturerId": c.get("manufacturer_part_number"),
                        "addIntoPcb": True,
                        "saveAfter": i == len(refs) - 1,
                        "expectedDocumentUuid": PAGE,
                    },
                }
            )
        for unit in block_coords.get("additional_units") or []:
            ref = unit["ref"]
            c = comps[ref]
            jobs.append(
                {
                    "tool": "modify_schematic_component",
                    "tag": unit["tag"],
                    "args": {
                        "primitiveId": pids[unit["tag"]],
                        "designator": live_designators[ref],
                        "name": c.get("value") or c.get("manufacturer_part_number"),
                        "manufacturerId": c.get("manufacturer_part_number"),
                        "addIntoBom": False,
                        "addIntoPcb": True,
                        "saveAfter": False,
                        "expectedDocumentUuid": PAGE,
                    },
                }
            )
        for job in jobs:
            job["args"]["saveAfter"] = False
        jobs[-1]["args"]["saveAfter"] = True
        run_batch(jobs, f"designate-{slug}")
        print("DESIGNATED", refs)

    if args.stage == "pins":
        pin_tags = refs + [unit["tag"] for unit in block_coords.get("additional_units") or []]
        jobs = [
            {
                "tool": "list_schematic_component_pins",
                "tag": ref,
                "args": {
                    "componentPrimitiveId": pids[ref],
                    "expectedDocumentUuid": PAGE,
                },
            }
            for ref in pin_tags
        ]
        pin_results = run_batch(jobs, f"pins-{slug}")
        live = parse_live_pins(pin_results)
        print("PINS")
        for ref, pins in live.items():
            summary = [
                f"{p.get('pinNumber') or p.get('number')}:{(p.get('pinName') or p.get('name') or '')}"
                for p in pins
            ]
            print(f"  {ref}", summary)

    if args.stage == "wire":
        pin_results = json.loads((JOBS / f"pins-{slug}.results.json").read_text())
        live = parse_live_pins(pin_results)
        unit_tags: dict[str, list[str]] = {ref: [ref] for ref in refs}
        for unit in block_coords.get("additional_units") or []:
            unit_tags[unit["ref"]].append(unit["tag"])
        connections: dict[str, list[dict]] = {
            tag: [] for tags in unit_tags.values() for tag in tags
        }
        seen: set[tuple[str, str, str]] = set()
        for net in plan["nets"]:
            for ep in net["endpoints"]:
                if ep["ref"] not in refs:
                    continue
                ref = ep["ref"]
                wanted = ep.get("pin_name") or ep.get("pin")
                skip_key = (ref, str(ep.get("pin") or wanted))
                if skip_key in SKIP_PINS.get(args.block, set()):
                    print(f"SKIP {ref} {wanted} — not on live symbol")
                    continue
                chosen_tag = None
                num = None
                remap = PIN_REMAP.get(args.block, {}).get((ref, str(ep.get("pin") or wanted)))
                for tag in unit_tags[ref]:
                    if remap:
                        candidate = map_pin(live.get(tag) or [], remap)
                    else:
                        candidate = map_pin(live.get(tag) or [], wanted)
                        if not candidate and ep.get("pin") and str(ep.get("pin")) != str(wanted):
                            candidate = map_pin(live.get(tag) or [], str(ep.get("pin")))
                    if candidate:
                        chosen_tag = tag
                        num = candidate
                        break
                if not num or not chosen_tag:
                    print(f"UNMAPPED {ref} {wanted} units={[(tag, live.get(tag)) for tag in unit_tags[ref]]}")
                    raise SystemExit(f"cannot map {ref}.{wanted} to live pin")
                key = (chosen_tag, num, net["name"])
                if key in seen:
                    continue
                seen.add(key)
                connections[chosen_tag].append({"pinNumber": str(num), "net": net["name"]})
        for ref, extras in BLOCK_EXTRAS.get(args.block, {}).items():
            for num, net in extras:
                chosen_tag = next(
                    (tag for tag in unit_tags[ref] if map_pin(live.get(tag) or [], str(num))),
                    None,
                )
                if not chosen_tag:
                    raise SystemExit(f"cannot map required extra {ref}.{num} to a live symbol unit")
                key = (chosen_tag, str(num), net)
                if key in seen:
                    continue
                seen.add(key)
                connections[chosen_tag].append({"pinNumber": str(num), "net": net})
        jobs = []
        wired_refs = [tag for tags in unit_tags.values() for tag in tags if connections[tag]]
        for i, ref in enumerate(wired_refs):
            jobs.append(
                {
                    "tool": "connect_schematic_pins_to_nets",
                    "tag": ref,
                    "args": {
                        "componentPrimitiveId": pids[ref],
                        "connections": connections[ref],
                        "saveAfter": i == len(wired_refs) - 1,
                        "expectedDocumentUuid": PAGE,
                    },
                }
            )
        run_batch(jobs, f"wire-{slug}")
        print("WIRED")
        for ref in wired_refs:
            print(f"  {ref}", connections[ref])

    saved = True
    if args.stage in MUTATING_STAGES:
        save_result = mcp_call("save_active_document", {"expectedDocumentUuid": PAGE})
        saved = save_result.get("saved") is True
        if not saved:
            raise SystemExit(
                "HARD STOP: explicit save was not confirmed; mutation remains IN_FLIGHT for recovery"
            )

    post_snapshot = source_snapshot()
    census = post_snapshot["census"]
    print(
        "CENSUS",
        json.dumps(
            {
                "sourceHash": post_snapshot["source_hash"],
                "components": census["components"],
                "wires": census["wires"],
            },
            indent=2,
        ),
    )
    print("DESIGNATORS", " ".join(census["designators"]))
    print("NETS", json.dumps(census["net_counts"], indent=2, sort_keys=True))
    # Place leaves EasyEDA designators as C?/R?/U?. Naming is the designate stage.
    if args.stage != "place":
        missing_refs = [
            live_designators[r] for r in refs if live_designators[r] not in census["designators"]
        ]
        if missing_refs:
            raise SystemExit(f"designators missing after block: {missing_refs}")

    if args.stage in MUTATING_STAGES:
        try:
            netlist = mcp_call("get_schematic_netlist", {"expectedDocumentUuid": PAGE})
        except SystemExit as exc:
            # Tool is historically missing on this bridge. Source NET ATTR census remains proof.
            netlist = {"available": False, "error": str(exc)[:800]}
        semantic_path = JOBS / f"{args.transaction_id}-semantic.json"
        semantic = {
            "schema_version": 1,
            "transaction_id": args.transaction_id,
            "project_uuid": PROJECT,
            "document_uuid": PAGE,
            "scope": args.block,
            "stage": args.stage,
            "intended_delta": intended_delta,
            "pre_source_hash": pre_snapshot["source_hash"],
            "post_source_hash": post_snapshot["source_hash"],
            "saved": saved,
            "affected": [live_designators[r] for r in refs],
            "census": census,
            "netlist": netlist,
        }
        semantic_path.write_text(json.dumps(semantic, indent=2, sort_keys=True) + "\n")
        try:
            record_mutation(MUTATION_STATE, MUTATION_LEDGER, semantic_path)
        except GateError as exc:
            raise SystemExit(
                f"HARD STOP: mutation exists but semantic evidence was rejected: {exc}"
            ) from exc
        print("WRITE_LOCK=AWAITING_EVIDENCE")
        print(f"TRANSACTION_ID={args.transaction_id}")
        print(f"SEMANTIC_READBACK={semantic_path}")
        print(
            "NEXT=Capture a settled useful-scale screenshot, write its structured visual evidence, "
            "then close the transaction with harness/easyeda_mutation_gate.py."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
