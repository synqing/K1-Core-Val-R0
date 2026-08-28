#!/usr/bin/env python3
"""Complete the fixed RT1062 power, DCDC and decoupling implementation.

The script is deliberately staged so every visually atomic EasyEDA write can be
screenshotted and inspected before the next write:

  prune -> add -> designate -> connect -> record
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from complete_rt_boot_clock import remove_records_and_endpoint_wires
from execute_canonical_container import JOBS, PAGE, PROJECT, SNAPSHOTS, load_fixture_executor
from inspect_live_components import endpoint_net_map
from repair_power_buck import component_records
from wire_led_efuse_support import endpoint, points_for, source_rows


TX = "canonical-rt-fixed-power-completion-2026-08-28"
PIDS_PATH = JOBS / f"{TX}-pids.json"
STAGE_PATH = JOBS / f"{TX}-stages.json"
INTENDED = (
    "Replace the placeholder RT decoupling bank with the NXP-required fixed-rail network; "
    "correct every RT1062 fixed supply, DCDC, internal-LDO and unused-RTC endpoint; add the "
    "4.7 uH DCDC inductor and 10 ms PSWITCH RC; leave all flexible GPIO assignments unchanged"
)

CAP_DEVICES = {
    "100nF": ("5ad32f6891c644b1a27268ae1b8659ab", "GRM155R71C104KA88D", ""),
    "220nF": ("1ea9e714435349b9a3e3d17faeb3ceb6", "GRM155R61A224KE19D", "C77001"),
    "1uF": ("d7cfbc3b990d4f4892dd720a635a2d32", "GRM155R61A105KE15D", "C76999"),
    "4.7uF": ("a84d6511c0ea457182ddb38644c3647b", "GRM155R60J475ME47D", "C82453"),
    "10uF": ("64ae6bee56d84f5992761781da437e68", "GRM155R60J106ME44D", ""),
    "22uF": ("525db8f03551462fbf8ca1dc43887999", "GRM188R60J226MEA0D", "C77042"),
}


def group(group_id: str, rail: str, values: list[str]) -> list[dict[str, str]]:
    return [{"group": group_id, "rail": rail, "value": value} for value in values]


CAPS = (
    group("VDD_SOC", "1V15_CORE", ["220nF"] * 5 + ["4.7uF", "22uF"])
    + group("DCDC_IN", "3V3", ["220nF"] * 3 + ["4.7uF", "22uF"])
    + group("HIGH_IN", "3V3", ["220nF", "4.7uF"])
    + group("HIGH_CAP", "VDD_HIGH_CAP", ["220nF", "4.7uF"])
    + group("SNVS_IN", "3V3", ["220nF"])
    + group("SNVS_CAP", "VDD_SNVS_CAP", ["220nF", "4.7uF"])
    + group("PLL", "NVCC_PLL_1V1", ["220nF", "4.7uF"])
    + group("USB_CAP", "VDD_USB_CAP", ["100nF", "10uF"])
    + group("ADC", "3V3", ["220nF", "1uF"])
    + group("SD0", "3V3", ["100nF", "4.7uF"])
    + group("SD1", "3V3", ["100nF", "4.7uF"])
    + group("EMC", "3V3", ["100nF", "100nF", "4.7uF"])
    + group("GPIO", "3V3", ["100nF", "100nF", "100nF", "4.7uF"])
)
assert len(CAPS) == 36

CAP_REFS = [f"C{n}" for n in range(19, 35)] + [f"C{n}" for n in range(69, 89)]
assert len(CAP_REFS) == len(CAPS)

# Three seven-part columns beside U6, then fifteen parts along the lower bank.
RIGHT_POSITIONS = [
    (x, y)
    for x in (2635, 2765, 2885)
    for y in (3890, 3970, 4050, 4130, 4210, 4290, 4370)
]
LOWER_POSITIONS = (
    [(2015 + 110 * i, 3805) for i in range(8)]
    + [(2015 + 120 * i, 3720) for i in range(7)]
)
POSITIONS = RIGHT_POSITIONS + LOWER_POSITIONS
assert len(POSITIONS) == len(CAPS)

SUPPORT = {
    "L4": {
        "deviceUuid": "ca7a22cd09a54c7ead9751b1485ca635",
        "designator": "L4-RTC", "name": "4.7uH", "mpn": "XGL4030-472MEC",
        "supplierId": "C7159276", "x": 2635, "y": 4470,
    },
    "R70": {
        "deviceUuid": "0cc9cee0c09e4a1c8b41e9d1feefa5b2",
        "designator": "R70-RTC", "name": "100k", "mpn": "RC0402FR-07100KL",
        "supplierId": "C60491", "x": 2765, "y": 4470,
    },
    "C89": {
        "deviceUuid": "5ad32f6891c644b1a27268ae1b8659ab",
        "designator": "C89-RTC", "name": "100nF", "mpn": "GRM155R71C104KA88D",
        "supplierId": "", "x": 2885, "y": 4470,
    },
}

TEXTS = [
    (2535, 4535, "RT1062 DCDC: 3V3 IN/Q -> SW -> L4 4.7uH -> 1V15_CORE"),
    (2700, 4415, "PSWITCH RC = 100k / 100nF (10ms)"),
    (2070, 3850, "NXP RAIL DECOUPLING: USB CAP | ADC | SD0/1 | EMC | GPIO"),
]

# Exact fixed balls from MIMXRT1062DVJ6B. Flexible GPIO is intentionally absent.
U6_BALL_NETS = {
    **{ball: "1V15_CORE" for ball in ("F6", "F7", "F8", "F9", "G6", "G9", "H6", "H9", "J9")},
    **{ball: "GND" for ball in (
        "A1", "A14", "B5", "B10", "E2", "E13", "G7", "G8", "H7", "H8",
        "J7", "J8", "K2", "K13", "L9", "N5", "N8", "P1", "P14",
    )},
    "L1": "3V3", "L2": "3V3", "K4": "3V3",
    "N1": "GND", "N2": "GND",
    "M1": "DCDC_SW", "M2": "DCDC_SW", "J5": "1V15_CORE",
    "K3": "DCDC_PSWITCH",
    "P12": "3V3", "P8": "VDD_HIGH_CAP",
    "M9": "3V3", "M10": "VDD_SNVS_CAP",
    "K8": "VDD_USB_CAP", "P10": "NVCC_PLL_1V1",
    "N14": "3V3", "J6": "3V3", "K5": "3V3",
    "F5": "3V3", "E6": "3V3", "E9": "3V3", "F10": "3V3", "J10": "3V3",
    "N9": "GND",  # RTC_XTALI grounded when the 32.768 kHz crystal is omitted.
    "K9": "GND",  # NGND_KEL0 default ground connection.
}

SUPPORT_CONNECTIONS = {
    "L4-RTC": {"1": "DCDC_SW", "2": "1V15_CORE"},
    "R70-RTC": {"1": "3V3", "2": "DCDC_PSWITCH"},
    "C89-RTC": {"1": "DCDC_PSWITCH", "2": "GND"},
}


def all_components(source: str) -> dict[str, list[dict]]:
    rows = source_rows(source)
    components = {
        str(row[1]): {
            "primitive_id": str(row[1]), "library_name": str(row[2]),
            "x": float(row[3]), "y": float(row[4]), "rotation": float(row[5]),
        }
        for row in rows if row[0] == "COMPONENT" and len(row) >= 6
    }
    output: dict[str, list[dict]] = {}
    for row in rows:
        if row[0] == "ATTR" and len(row) >= 5 and row[3] == "Designator":
            pid = str(row[2])
            if pid in components:
                output.setdefault(str(row[4]), []).append(components[pid])
    return output


def assert_active(base) -> dict:
    state = json.loads(base.MUTATION_STATE.read_text())
    if state.get("state") != "IN_FLIGHT" or state.get("active_transaction", {}).get("transaction_id") != TX:
        raise SystemExit(f"{TX} is not the active IN_FLIGHT transaction: {state.get('state')}")
    return state


def save_stage(name: str, snapshot: dict) -> None:
    stages = json.loads(STAGE_PATH.read_text()) if STAGE_PATH.exists() else {}
    stages[name] = {"source_hash": snapshot["source_hash"], "census": snapshot["census"]}
    STAGE_PATH.write_text(json.dumps(stages, indent=2, sort_keys=True) + "\n")


def live_pin_maps(base, refs: dict[str, dict], stem: str) -> dict[str, dict[str, dict]]:
    results = base.run_batch([
        {"tool": "list_schematic_component_pins", "tag": tag, "args": {
            "componentPrimitiveId": record["primitive_id"], "expectedDocumentUuid": PAGE}}
        for tag, record in refs.items()
    ], stem)
    parsed = base.parse_live_pins(results)
    return {tag: {str(pin["pinNumber"]): pin for pin in pins} for tag, pins in parsed.items()}


def set_source_and_confirm(base, rows: list[list], expected_hash: str, stem: str) -> dict:
    head = next(row for row in rows if row[0] == "HEAD")
    source = "\n".join(json.dumps(row, separators=(",", ":")) for row in rows)
    try:
        result = base.mcp_call("set_document_source", {
            "source": source, "expectedSourceHash": expected_hash,
            "skipConfirmation": True, "expectedDocumentUuid": PAGE,
        }, timeout=240)
    except SystemExit as exc:
        result = {"bridge_message": str(exc), "payload_max_id": head[1].get("maxId")}
    (JOBS / f"{TX}-{stem}-set-source-result.json").write_text(json.dumps(result, indent=2) + "\n")
    if base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE}).get("saved") is not True:
        raise SystemExit(f"explicit save after {stem} was not confirmed")
    return base.source_snapshot()


def prune() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    base.validate_repository_state(base.MUTATION_STATE, base.MUTATION_LEDGER)
    before = base.source_snapshot()
    live = component_records(before["source"])
    old_refs = [f"C{n}-RTC" for n in range(19, 35)]
    missing = sorted(set(old_refs) - set(live))
    if missing:
        raise SystemExit(f"placeholder RT caps missing before replacement: {missing}")
    pins = live_pin_maps(base, {ref: live[ref] for ref in old_refs}, f"{TX}-old-cap-pins")
    snapshot_path = SNAPSHOTS / f"{TX}-before.json"
    snapshot_path.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")
    base.begin_transaction(
        base.MUTATION_STATE, base.MUTATION_LEDGER, transaction_id=TX,
        project_uuid=PROJECT, document_uuid=PAGE, scope="RT_FIXED_POWER", stage="repair",
        kind="normal", intended_delta=INTENDED, snapshot_path=snapshot_path,
        expected_checks=[
            "all fixed RT1062 supply and ground balls use the correct rail",
            "DCDC SW, 4.7 uH output inductor, SENSE and 10 ms PSWITCH RC are complete",
            "36 source-derived rail capacitors are grouped legibly inside box 3",
            "VDD_USB_CAP, NVCC_PLL, HIGH_CAP and SNVS_CAP are isolated internal-LDO outputs",
            "no flexible GPIO, box, PCB or unrelated component is changed",
        ],
    )
    points = {endpoint(pin) for cap in pins.values() for pin in cap.values()}
    rows = remove_records_and_endpoint_wires(
        source_rows(before["source"]),
        {live[ref]["primitive_id"] for ref in old_refs}, points,
    )
    after = set_source_and_confirm(base, rows, before["source_hash"], "prune")
    if after["census"]["components"] != before["census"]["components"] - 16:
        raise SystemExit("placeholder-cap removal changed the wrong number of components")
    save_stage("prune", after)
    print(f"STAGE=prune SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def add() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    assert_active(base)
    before = base.source_snapshot()
    specs = {}
    for ref, cap, (x, y) in zip(CAP_REFS, CAPS, POSITIONS):
        device, mpn, supplier_id = CAP_DEVICES[cap["value"]]
        specs[ref] = {
            **cap, "deviceUuid": device, "mpn": mpn, "supplierId": supplier_id,
            "designator": f"{ref}-RTC", "x": x, "y": y,
        }
    specs.update(SUPPORT)
    jobs = [
        {"tool": "add_schematic_component", "tag": ref, "args": {
            "deviceUuid": spec["deviceUuid"], "x": spec["x"], "y": spec["y"],
            "rotation": 0, "addIntoBom": True, "addIntoPcb": True,
            "saveAfter": index == len(specs) - 1, "expectedDocumentUuid": PAGE,
        }}
        for index, (ref, spec) in enumerate(specs.items())
    ]
    pids = base.extract_pids(base.run_batch(jobs, f"{TX}-add"))
    if set(pids) != set(specs):
        raise SystemExit(f"RT power component placement incomplete: {sorted(set(specs) - set(pids))}")
    PIDS_PATH.write_text(json.dumps({"pids": pids, "specs": specs}, indent=2, sort_keys=True) + "\n")
    after = base.source_snapshot()
    if after["census"]["components"] != before["census"]["components"] + len(specs):
        raise SystemExit("RT power placement changed the wrong number of components")
    save_stage("add", after)
    print(f"STAGE=add SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def designate() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    assert_active(base)
    data = json.loads(PIDS_PATH.read_text())
    pids, specs = data["pids"], data["specs"]
    jobs = []
    for ref, spec in specs.items():
        mpn = spec["mpn"]
        jobs.append({"tool": "modify_schematic_component", "tag": ref, "args": {
            "primitiveId": pids[ref], "designator": spec["designator"],
            "name": spec.get("value") or spec["name"], "manufacturer": "Murata" if ref.startswith("C") else "",
            "manufacturerId": mpn, "supplier": "LCSC", "supplierId": spec.get("supplierId") or "",
            "addIntoBom": True, "addIntoPcb": True, "saveAfter": False,
            "expectedDocumentUuid": PAGE,
        }})
    for index, (x, y, content) in enumerate(TEXTS):
        jobs.append({"tool": "add_schematic_text", "tag": f"note-{index}", "args": {
            "x": x, "y": y, "content": content, "fontSize": 8, "bold": True,
            "textColor": "#1F5AA6", "saveAfter": index == len(TEXTS) - 1,
            "expectedDocumentUuid": PAGE,
        }})
    base.run_batch(jobs, f"{TX}-designate")
    after = base.source_snapshot()
    live = all_components(after["source"])
    missing = [spec["designator"] for spec in specs.values() if len(live.get(spec["designator"], [])) != 1]
    if missing:
        raise SystemExit(f"RT power designators missing or duplicated: {missing}")
    save_stage("designate", after)
    print(f"STAGE=designate SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def relayout() -> int:
    """Repair the provisional add-stage coordinates before designation or wiring."""
    base = load_fixture_executor()
    base.assert_identity()
    assert_active(base)
    data = json.loads(PIDS_PATH.read_text())
    pids = data["pids"]
    positions = {ref: xy for ref, xy in zip(CAP_REFS, POSITIONS)}
    positions.update({ref: (spec["x"], spec["y"]) for ref, spec in SUPPORT.items()})
    jobs = [
        {"tool": "modify_schematic_component", "tag": ref, "args": {
            "primitiveId": pids[ref], "x": xy[0], "y": xy[1],
            "saveAfter": index == len(positions) - 1, "expectedDocumentUuid": PAGE,
        }}
        for index, (ref, xy) in enumerate(positions.items())
    ]
    base.run_batch(jobs, f"{TX}-relayout")
    after = base.source_snapshot()
    rows = {str(row[1]): row for row in source_rows(after["source"]) if row[0] == "COMPONENT"}
    wrong = []
    for ref, (x, y) in positions.items():
        row = rows[pids[ref]]
        if [int(row[3]), int(row[4])] != [x, y]:
            wrong.append((ref, row[3], row[4], x, y))
    if wrong:
        raise SystemExit(f"RT power relayout position mismatch: {wrong}")
    save_stage("relayout", after)
    print(f"STAGE=relayout SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def spacing_repair() -> int:
    """Widen the seven-part lower row after designation exposed text crowding."""
    base = load_fixture_executor()
    base.assert_identity()
    assert_active(base)
    pids = json.loads(PIDS_PATH.read_text())["pids"]
    refs = CAP_REFS[-7:]
    positions = {ref: (2030 + 135 * index, 3720) for index, ref in enumerate(refs)}
    jobs = [
        {"tool": "modify_schematic_component", "tag": ref, "args": {
            "primitiveId": pids[ref], "x": xy[0], "y": xy[1],
            "saveAfter": index == len(refs) - 1, "expectedDocumentUuid": PAGE,
        }}
        for index, (ref, xy) in enumerate(positions.items())
    ]
    base.run_batch(jobs, f"{TX}-spacing-repair")
    after = base.source_snapshot()
    rows = {str(row[1]): row for row in source_rows(after["source"]) if row[0] == "COMPONENT"}
    wrong = [ref for ref, (x, y) in positions.items()
             if [int(rows[pids[ref]][3]), int(rows[pids[ref]][4])] != [x, y]]
    if wrong:
        raise SystemExit(f"lower-row spacing repair failed for {wrong}")
    save_stage("spacing_repair", after)
    print(f"STAGE=spacing_repair SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def label_repair() -> int:
    """Move and shorten captions that crossed U6 or the left box edge."""
    base = load_fixture_executor()
    base.assert_identity()
    assert_active(base)
    before = base.source_snapshot()
    replacements = {
        "RT1062 DCDC: 3V3 IN/Q -> SW -> L4 4.7uH -> 1V15_CORE":
            (2630, 4535, "DCDC: 3V3 -> SW -> L4 -> 1V15_CORE"),
        "PSWITCH RC = 100k / 100nF (10ms)":
            (2650, 4415, "PSWITCH: 100k / 100nF = 10ms"),
        "NXP RAIL DECOUPLING: USB CAP | ADC | SD0/1 | EMC | GPIO":
            (2190, 3850, "NXP DECOUPLING: USB CAP | ADC | SD0/1 | EMC | GPIO"),
    }
    rows = source_rows(before["source"])
    found = set()
    for row in rows:
        if row[0] == "TEXT" and len(row) > 5 and row[5] in replacements:
            old = row[5]
            row[2], row[3], row[5] = replacements[old]
            found.add(old)
    if found != set(replacements):
        raise SystemExit(f"caption repair could not find {sorted(set(replacements) - found)}")
    after = set_source_and_confirm(base, rows, before["source_hash"], "label-repair")
    for _, _, content in replacements.values():
        if sum(row[0] == "TEXT" and len(row) > 5 and row[5] == content
               for row in source_rows(after["source"])) != 1:
            raise SystemExit(f"repaired caption missing or duplicated: {content}")
    save_stage("label_repair", after)
    print(f"STAGE=label_repair SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def declutter() -> int:
    """Hide redundant bank endpoint labels while preserving every named net."""
    base = load_fixture_executor()
    base.assert_identity()
    assert_active(base)
    before = base.source_snapshot()
    live = all_components(before["source"])
    refs = [f"{ref}-RTC" for ref in CAP_REFS] + [spec["designator"] for spec in SUPPORT.values()]
    targets = {}
    for ref in refs:
        if len(live.get(ref, [])) != 1:
            raise SystemExit(f"declutter target {ref} missing or duplicated")
        targets[ref] = live[ref][0]
    pins = live_pin_maps(base, targets, f"{TX}-declutter-pins")
    points = {endpoint(pin) for pinset in pins.values() for pin in pinset.values()}
    rows = source_rows(before["source"])
    wire_ids = set()
    for row in rows:
        if row[0] != "WIRE":
            continue
        if any((int(x1), int(y1)) in points or (int(x2), int(y2)) in points
               for x1, y1, x2, y2 in row[2]):
            wire_ids.add(str(row[1]))
    hidden = 0
    for row in rows:
        if (row[0] == "ATTR" and len(row) > 6 and str(row[2]) in wire_ids
                and row[3] == "NET"):
            row[6] = 0
            hidden += 1
    if hidden != 78:
        raise SystemExit(f"expected to hide 78 cap/support endpoint labels, found {hidden}")
    head = next(row for row in rows if row[0] == "HEAD")
    max_id = int(head[1].get("maxId") or 0) + 1
    head[1]["maxId"] = max_id
    caption = "CORE/LDO CAPS: SOC | DCDC_IN | HIGH | SNVS | PLL"
    rows.append(["TEXT", f"e{max_id}", 2545, 3845, 0, caption, "st16", 0])
    after = set_source_and_confirm(base, rows, before["source_hash"], "declutter")
    if sum(row[0] == "TEXT" and len(row) > 5 and row[5] == caption
           for row in source_rows(after["source"])) != 1:
        raise SystemExit("core/LDO bank caption missing or duplicated")
    final_nets = endpoint_net_map(after["source"])
    for ref, cap in zip(CAP_REFS, CAPS):
        designator = f"{ref}-RTC"
        for pin_number, expected in (("1", cap["rail"]), ("2", "GND")):
            actual = final_nets.get(endpoint(pins[designator][pin_number]), [])
            if actual != [expected]:
                raise SystemExit(f"declutter changed {designator}.{pin_number}: {actual}")
    for ref, connections in SUPPORT_CONNECTIONS.items():
        for pin_number, expected in connections.items():
            actual = final_nets.get(endpoint(pins[ref][pin_number]), [])
            if actual != [expected]:
                raise SystemExit(f"declutter changed {ref}.{pin_number}: {actual}")
    save_stage("declutter", after)
    print(f"STAGE=declutter SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def connect() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    assert_active(base)
    before = base.source_snapshot()
    live = all_components(before["source"])
    u6 = live.get("U6-RTC", [])
    if len(u6) != 2:
        raise SystemExit(f"expected two U6 symbol units, found {len(u6)}")
    u6.sort(key=lambda record: record["library_name"])
    targets = {f"U6.{index + 1}": record for index, record in enumerate(u6)}
    for ref in [f"{ref}-RTC" for ref in CAP_REFS] + [spec["designator"] for spec in SUPPORT.values()]:
        records = live.get(ref, [])
        if len(records) != 1:
            raise SystemExit(f"{ref} missing or duplicated before wiring")
        targets[ref] = records[0]
    pins = live_pin_maps(base, targets, f"{TX}-final-pins")
    ball_pins = {}
    for unit in ("U6.1", "U6.2"):
        for ball, pin in pins[unit].items():
            if ball in ball_pins:
                raise SystemExit(f"duplicate U6 ball {ball}")
            ball_pins[ball] = pin
    missing_balls = sorted(set(U6_BALL_NETS) - set(ball_pins))
    if missing_balls:
        raise SystemExit(f"U6 fixed balls missing: {missing_balls}")

    rows = source_rows(before["source"])
    affected_points = {endpoint(ball_pins[ball]) for ball in U6_BALL_NETS}
    for ref in [f"{ref}-RTC" for ref in CAP_REFS] + [spec["designator"] for spec in SUPPORT.values()]:
        affected_points.update(endpoint(pin) for pin in pins[ref].values())
    rows = remove_records_and_endpoint_wires(rows, set(), affected_points)
    head = next(row for row in rows if row[0] == "HEAD")
    max_id = int(head[1].get("maxId") or 0)
    topology = {}

    def append_wire(pin: dict, net: str, visible: int) -> None:
        nonlocal max_id
        geometry = points_for(pin)
        max_id += 1
        wire_id = f"e{max_id}"
        rows.append(["WIRE", wire_id, geometry, "st11", 0])
        max_id += 1
        x1, y1, x2, y2 = geometry[0]
        rows.append(["ATTR", f"e{max_id}", wire_id, "NET", net, 0, visible,
                     (x1 + x2) / 2, (y1 + y2) / 2, 0, "st4", 0])
        topology[f"{endpoint(pin)[0]},{endpoint(pin)[1]}"] = net

    shown_u6_nets = set()
    for ball, net in U6_BALL_NETS.items():
        visible = 0 if net in shown_u6_nets else 1
        append_wire(ball_pins[ball], net, visible)
        shown_u6_nets.add(net)

    group_seen = set()
    for ref, cap in zip(CAP_REFS, CAPS):
        designator = f"{ref}-RTC"
        visible = 0 if cap["group"] in group_seen else 1
        append_wire(pins[designator]["1"], cap["rail"], visible)
        append_wire(pins[designator]["2"], "GND", visible)
        group_seen.add(cap["group"])
    for ref, connections in SUPPORT_CONNECTIONS.items():
        for pin_number, net in connections.items():
            append_wire(pins[ref][pin_number], net, 1)
    head[1]["maxId"] = max_id

    after = set_source_and_confirm(base, rows, before["source_hash"], "connect")
    if after["census"]["components"] != 215:
        raise SystemExit(f"RT power completion expected 215 components, found {after['census']['components']}")
    final_live = all_components(after["source"])
    for ref in [f"{ref}-RTC" for ref in CAP_REFS] + [spec["designator"] for spec in SUPPORT.values()]:
        if len(final_live.get(ref, [])) != 1:
            raise SystemExit(f"final {ref} missing or duplicated")
    if "VDD_USB_CAP\",\"3V3" in after["source"] or "NVCC_PLL\",\"3V3" in after["source"]:
        raise SystemExit("internal LDO output remains tied to 3V3")
    final_nets = endpoint_net_map(after["source"])
    for ball, expected in U6_BALL_NETS.items():
        actual = final_nets.get(endpoint(ball_pins[ball]), [])
        if actual != [expected]:
            raise SystemExit(f"U6 ball {ball} endpoint nets {actual} != {[expected]}")
    for ref, cap in zip(CAP_REFS, CAPS):
        designator = f"{ref}-RTC"
        for pin_number, expected in (("1", cap["rail"]), ("2", "GND")):
            actual = final_nets.get(endpoint(pins[designator][pin_number]), [])
            if actual != [expected]:
                raise SystemExit(f"{designator}.{pin_number} nets {actual} != {[expected]}")
    for ref, connections in SUPPORT_CONNECTIONS.items():
        for pin_number, expected in connections.items():
            actual = final_nets.get(endpoint(pins[ref][pin_number]), [])
            if actual != [expected]:
                raise SystemExit(f"{ref}.{pin_number} nets {actual} != {[expected]}")
    deliberately_open_names = {
        "GPANAIO", "RTC_XTALO", "CCM_CLK1_P", "CCM_CLK1_N", "TEST_MODE",
        "USB_OTG1_VBUS", "USB_OTG2_VBUS",
    }
    for ball, pin in ball_pins.items():
        if pin.get("pinName") in deliberately_open_names:
            actual = final_nets.get(endpoint(pin), [])
            if actual:
                raise SystemExit(f"deliberately open U6 pin {pin.get('pinName')} {ball} has nets {actual}")
    save_stage("connect", after)
    (JOBS / f"{TX}-topology.json").write_text(json.dumps(topology, indent=2, sort_keys=True) + "\n")
    print(f"STAGE=connect SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def record() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    assert_active(base)
    original = json.loads((SNAPSHOTS / f"{TX}-before.json").read_text())
    after = base.source_snapshot()
    stages = json.loads(STAGE_PATH.read_text())
    if stages.get("declutter", {}).get("source_hash") != after["source_hash"]:
        raise SystemExit("live source changed after the inspected declutter stage")
    live = all_components(after["source"])
    if len(live.get("U6-RTC", [])) != 2 or after["census"]["components"] != 215:
        raise SystemExit("final RT power census changed before recording")
    semantic = JOBS / f"{TX}-semantic.json"
    semantic.write_text(json.dumps({
        "schema_version": 1, "transaction_id": TX, "project_uuid": PROJECT,
        "document_uuid": PAGE, "scope": "RT_FIXED_POWER", "stage": "repair",
        "intended_delta": INTENDED, "pre_source_hash": original["source_hash"],
        "post_source_hash": after["source_hash"], "saved": True,
        "affected": ["U6-RTC", *[f"{ref}-RTC" for ref in CAP_REFS],
                     *[spec["designator"] for spec in SUPPORT.values()]],
        "fixed_ball_nets": U6_BALL_NETS, "decoupling_groups": CAPS,
        "topology": json.loads((JOBS / f"{TX}-topology.json").read_text()),
        "intermediate_stages": stages, "component_count": after["census"]["components"],
        "census": after["census"],
        "deliberately_open_fixed_pins": [
            "GPANAIO N10", "RTC_XTALO P9", "CCM_CLK1_P", "CCM_CLK1_N", "TEST_MODE K6",
            "USB_OTG1_VBUS N6 pending optional USB implementation",
            "USB_OTG2_VBUS P6 pending optional USB implementation",
        ],
        "source_basis": [
            "NXP MIMXRT105060HDUG Rev 3 power, DCDC, clock and decoupling guidance",
            "NXP IMXRT1060CEC current datasheet fixed ball map",
            "NXP MIMXRT1060-EVK SPF-31357 A3 reference schematic",
            "NXP VDD_USB_CAP support ruling",
        ],
    }, indent=2, sort_keys=True) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic)
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"SEMANTIC={semantic}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=(
        "prune", "add", "relayout", "designate", "spacing_repair", "label_repair",
        "connect", "declutter", "record"
    ))
    args = parser.parse_args()
    return globals()[args.stage]()


if __name__ == "__main__":
    sys.exit(main())
