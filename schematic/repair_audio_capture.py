#!/usr/bin/env python3
"""Complete the source-derived ADC6120 and microphone-flex support network.

The stages are intentionally small so the canonical EasyEDA mutation contract
can capture and inspect each visually atomic delta before the next write.
"""
from __future__ import annotations

import argparse
import json
import sys
import time

from complete_rt_boot_clock import remove_records_and_endpoint_wires
from execute_canonical_container import JOBS, PAGE, PROJECT, SNAPSHOTS, load_fixture_executor
from inspect_live_components import endpoint_net_map
from repair_power_buck import component_records
from wire_led_efuse_support import endpoint, points_for, source_rows


TX = "canonical-audio-capture-electrical-repair-2026-08-28"
PIDS_PATH = JOBS / f"{TX}-pids.json"
STAGE_PATH = JOBS / f"{TX}-stages.json"
PREPARED_SNAPSHOT = SNAPSHOTS / f"{TX}-prepared.json"
INTENDED = (
    "Ground every TLV320ADC6120 VSS and exposed-pad endpoint; install the required "
    "AREG/DREG 10 uF plus 100 nF pairs and the required 1 uF VREF capacitor; mark "
    "the MCLK shunt capacitor DNP; remap the microphone flex with ground between PDM "
    "clock and data; and add BCLK/FSYNC test access without changing flexible RT pinmux"
)


DEVICES = {
    "C51": {
        "deviceUuid": "d7cfbc3b990d4f4892dd720a635a2d32",
        "designator": "C51-AUD", "name": "1uF", "mpn": "GRM155R61A105KE15D",
        "supplierId": "C76999", "x": 70, "y": 3300,
    },
    "C90": {
        "deviceUuid": "64ae6bee56d84f5992761781da437e68",
        "designator": "C90-AUD", "name": "10uF", "mpn": "GRM155R60J106ME44D",
        "supplierId": "", "x": 250, "y": 3300,
    },
    "C91": {
        "deviceUuid": "64ae6bee56d84f5992761781da437e68",
        "designator": "C91-AUD", "name": "10uF", "mpn": "GRM155R60J106ME44D",
        "supplierId": "", "x": 790, "y": 3400,
    },
    "TP7": {
        "deviceUuid": "42b09b6db2ab43cb994fad497f236935",
        "designator": "TP7-AUD", "name": "BCLK TP", "mpn": "5001",
        "supplierId": "", "x": 610, "y": 2795,
    },
    "TP8": {
        "deviceUuid": "42b09b6db2ab43cb994fad497f236935",
        "designator": "TP8-AUD", "name": "FSYNC TP", "mpn": "5001",
        "supplierId": "", "x": 790, "y": 2795,
    },
}


CONNECTIONS = {
    "U11-AUD": {
        "5": "GND", "10": "GND", "15": "GND", "20": "GND", "21": "GND",
    },
    "C51-AUD": {"1": "ADC_VREF", "2": "GND"},
    "C90-AUD": {"1": "ADC_AREG", "2": "GND"},
    "C91-AUD": {"1": "ADC_DREG", "2": "GND"},
    "J9-AUD": {
        "1": "3V3_MIC_FLEX", "2": "GND", "3": "PDM_CLK",
        "4": "GND", "5": "PDM_DAT", "6": "GND",
    },
    "TP7-AUD": {"1": "AUDIO_BCLK"},
    "TP8-AUD": {"1": "AUDIO_FSYNC"},
}


NOTES = [
    (520, 3470, "RT CLOCK MASTER | REMOVE R31-R33 BEFORE EXTERNAL J8 DRIVE"),
    (45, 2435, "J9: 1 PWR | 2 GND | 3 CLK | 4 GND | 5 DATA | 6 GND | 7-10 NC"),
    (520, 2435, "PDM DEFAULT R38/R39 | DIRECT RT R40/R41 = DNP EXPERIMENT"),
]


def active(base) -> None:
    state = json.loads(base.MUTATION_STATE.read_text())
    if state.get("state") != "IN_FLIGHT" or state.get("active_transaction", {}).get("transaction_id") != TX:
        raise SystemExit(f"{TX} is not the active transaction")


def save_stage(name: str, snapshot: dict) -> None:
    stages = json.loads(STAGE_PATH.read_text()) if STAGE_PATH.exists() else {}
    stages[name] = {"source_hash": snapshot["source_hash"], "census": snapshot["census"]}
    STAGE_PATH.write_text(json.dumps(stages, indent=2, sort_keys=True) + "\n")


def save_pre_write(name: str, snapshot: dict) -> None:
    path = SNAPSHOTS / f"{TX}-before-{name}.json"
    path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")


def pin_maps(base, targets: dict[str, dict], stem: str) -> dict[str, dict[str, dict]]:
    results = base.run_batch([
        {"tool": "list_schematic_component_pins", "tag": ref, "args": {
            "componentPrimitiveId": record["primitive_id"], "expectedDocumentUuid": PAGE}}
        for ref, record in targets.items()
    ], stem)
    parsed = base.parse_live_pins(results)
    return {ref: {str(pin["pinNumber"]): pin for pin in pins} for ref, pins in parsed.items()}


def set_source(base, rows: list[list], expected_hash: str, stem: str) -> dict:
    source = "\n".join(json.dumps(row, separators=(",", ":")) for row in rows)
    try:
        result = base.mcp_call("set_document_source", {
            "source": source, "expectedSourceHash": expected_hash, "skipConfirmation": True,
            "expectedDocumentUuid": PAGE,
        }, timeout=240)
    except SystemExit as exc:
        result = {"bridge_message": str(exc)}
    (JOBS / f"{TX}-{stem}-set-source-result.json").write_text(json.dumps(result, indent=2) + "\n")
    if result.get("bridge_message") or result.get("error"):
        raise SystemExit(f"{stem} source write was refused; save deliberately skipped: {result}")
    if base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE}).get("saved") is not True:
        raise SystemExit(f"save after {stem} was not confirmed")
    return base.source_snapshot()


def prune() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    base.validate_repository_state(base.MUTATION_STATE, base.MUTATION_LEDGER)
    if not PREPARED_SNAPSHOT.exists():
        raise SystemExit(f"run {sys.argv[0]} prepare before prune")
    before = json.loads(PREPARED_SNAPSHOT.read_text())
    state = json.loads(base.MUTATION_STATE.read_text())
    if state.get("current_source_hash") != before.get("source_hash"):
        raise SystemExit(
            f"prepared source {before.get('source_hash')} does not match gate "
            f"{state.get('current_source_hash')}"
        )
    live = component_records(before["source"])
    old = live.get("C51-AUD")
    pins = pin_maps(base, {"C51-AUD": old}, f"{TX}-old-c51-pins") if old else {}
    snapshot = SNAPSHOTS / f"{TX}-before.json"
    snapshot.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")
    base.begin_transaction(
        base.MUTATION_STATE, base.MUTATION_LEDGER, transaction_id=TX,
        project_uuid=PROJECT, document_uuid=PAGE, scope="AUDIO_CAPTURE", stage="repair",
        kind="normal", intended_delta=INTENDED, snapshot_path=snapshot,
        expected_checks=[
            "ADC6120 pins 5 10 15 20 and exposed pad 21 are all grounded",
            "AREG and DREG each have 10 uF plus 100 nF and VREF has 1 uF",
            "J9 inserts ground between PDM clock and data and leaves 7-10 unconnected",
            "BCLK and FSYNC have explicit test points",
            "no flexible RT pinmux, PCB, box or unrelated domain changes",
        ],
    )
    if old:
        points = {endpoint(pin) for pin in pins["C51-AUD"].values()}
        rows = remove_records_and_endpoint_wires(
            source_rows(before["source"]), {old["primitive_id"]}, points,
        )
        after = set_source(base, rows, before["source_hash"], "prune")
        if after["census"]["components"] != before["census"]["components"] - 1:
            raise SystemExit("C51 replacement prune changed the wrong component count")
    else:
        # The guarded write from the earlier interrupted attempt removed C51 and
        # persisted it before its contradictory bridge read-back. Adopt that
        # source state; the replacement is still covered by this transaction.
        after = before
        if after["census"]["components"] != 217:
            raise SystemExit(f"adopted C51 removal expected 217 components, found {after['census']['components']}")
    save_stage("prune", after)
    print(f"STAGE=prune SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def prepare() -> int:
    """Require three settled, byte-identical reads before binding the write snapshot."""
    base = load_fixture_executor()
    base.assert_identity()
    previous_hash = None
    stable_reads = 0
    for attempt in range(1, 13):
        current = base.source_snapshot()
        if current["source_hash"] == previous_hash:
            stable_reads += 1
        else:
            stable_reads = 1
            previous_hash = current["source_hash"]
        if stable_reads >= 3:
            PREPARED_SNAPSHOT.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
            print(f"SOURCE_SETTLED={current['source_hash']} ATTEMPTS={attempt} IDENTICAL_READS={stable_reads}")
            print(f"PREPARED_SNAPSHOT={PREPARED_SNAPSHOT}")
            return 0
        time.sleep(1.0)
    raise SystemExit("live EasyEDA source did not settle to three byte-identical reads")


def add() -> int:
    base = load_fixture_executor()
    base.assert_identity(); active(base)
    before = base.source_snapshot(); save_pre_write("add", before)
    jobs = [
        {"tool": "add_schematic_component", "tag": ref, "args": {
            "deviceUuid": spec["deviceUuid"], "x": spec["x"], "y": spec["y"],
            "rotation": 0, "addIntoBom": True, "addIntoPcb": True,
            "saveAfter": index == len(DEVICES) - 1, "expectedDocumentUuid": PAGE,
        }}
        for index, (ref, spec) in enumerate(DEVICES.items())
    ]
    pids = base.extract_pids(base.run_batch(jobs, f"{TX}-add"))
    if set(pids) != set(DEVICES):
        raise SystemExit(f"audio add missing {sorted(set(DEVICES) - set(pids))}")
    PIDS_PATH.write_text(json.dumps(pids, indent=2, sort_keys=True) + "\n")
    after = base.source_snapshot()
    if after["census"]["components"] != 222:
        raise SystemExit(f"audio add expected 222 components, found {after['census']['components']}")
    save_stage("add", after)
    print(f"STAGE=add SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def designate() -> int:
    base = load_fixture_executor()
    base.assert_identity(); active(base)
    before = base.source_snapshot(); save_pre_write("designate", before)
    pids = json.loads(PIDS_PATH.read_text())
    live = component_records(before["source"])
    jobs = []
    for ref, spec in DEVICES.items():
        jobs.append({"tool": "modify_schematic_component", "tag": ref, "args": {
            "primitiveId": pids[ref], "designator": spec["designator"], "name": spec["name"],
            "manufacturerId": spec["mpn"], "supplier": "LCSC", "supplierId": spec["supplierId"],
            "addIntoBom": True, "addIntoPcb": True, "saveAfter": False,
            "expectedDocumentUuid": PAGE,
        }})
    jobs.append({"tool": "modify_schematic_component", "tag": "C52-AUD", "args": {
        "primitiveId": live["C52-AUD"]["primitive_id"], "name": "DNP / 100pF MCLK TUNE",
        "addIntoBom": False, "addIntoPcb": True, "saveAfter": False,
        "expectedDocumentUuid": PAGE,
    }})
    for index, (x, y, content) in enumerate(NOTES):
        jobs.append({"tool": "add_schematic_text", "tag": f"note-{index}", "args": {
            "x": x, "y": y, "content": content, "fontSize": 8, "bold": True,
            "textColor": "#1F5AA6", "saveAfter": index == len(NOTES) - 1,
            "expectedDocumentUuid": PAGE,
        }})
    base.run_batch(jobs, f"{TX}-designate")
    after = base.source_snapshot(); final = component_records(after["source"])
    for spec in DEVICES.values():
        if spec["designator"] not in final or after["source"].count(f'"Designator","{spec["designator"]}"') != 1:
            raise SystemExit(f"missing or duplicate {spec['designator']}")
    save_stage("designate", after)
    print(f"STAGE=designate SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def connect() -> int:
    base = load_fixture_executor()
    base.assert_identity(); active(base)
    before = base.source_snapshot(); save_pre_write("connect", before)
    live = component_records(before["source"])
    targets = {ref: live[ref] for ref in CONNECTIONS}
    pins = pin_maps(base, targets, f"{TX}-connect-pins")
    for ref, mapping in CONNECTIONS.items():
        missing = sorted(set(mapping) - set(pins[ref]))
        if missing:
            raise SystemExit(f"{ref} missing pins {missing}")
    points = {endpoint(pins[ref][pin]) for ref, mapping in CONNECTIONS.items() for pin in mapping}
    rows = remove_records_and_endpoint_wires(source_rows(before["source"]), set(), points)
    head = next(row for row in rows if row[0] == "HEAD")
    max_id = int(head[1].get("maxId") or 0)
    topology = {}
    for ref, mapping in CONNECTIONS.items():
        for pin_number, net in mapping.items():
            geometry = points_for(pins[ref][pin_number])
            max_id += 1; wire_id = f"e{max_id}"
            rows.append(["WIRE", wire_id, geometry, "st11", 0])
            max_id += 1
            x1, y1, x2, y2 = geometry[0]
            visible = 1
            if (ref == "U11-AUD" and pin_number in ("10", "15")) or (ref == "J9-AUD" and pin_number in ("4", "6")):
                visible = 0
            rows.append(["ATTR", f"e{max_id}", wire_id, "NET", net, 0, visible,
                         (x1 + x2) / 2, (y1 + y2) / 2, 0, "st4", 0])
            topology[f"{ref}.{pin_number}"] = net
    head[1]["maxId"] = max_id
    after = set_source(base, rows, before["source_hash"], "connect")
    if after["census"]["components"] != 222:
        raise SystemExit("audio connection changed the component count")
    nets = endpoint_net_map(after["source"])
    for ref, mapping in CONNECTIONS.items():
        for pin_number, expected in mapping.items():
            actual = nets.get(endpoint(pins[ref][pin_number]), [])
            if actual != [expected]:
                raise SystemExit(f"{ref}.{pin_number} nets {actual} != {[expected]}")
    for pin_number in ("7", "8", "9", "10", "11", "12"):
        if nets.get(endpoint(pins["J9-AUD"][pin_number]), []):
            raise SystemExit(f"J9 pin {pin_number} must remain open")
    for pin_number in ("1", "2", "4"):
        if nets.get(endpoint(pins["U11-AUD"][pin_number]), []):
            raise SystemExit(f"U11 analogue input pin {pin_number} must remain open for digital-PDM use")
    save_stage("connect", after)
    (JOBS / f"{TX}-topology.json").write_text(json.dumps(topology, indent=2, sort_keys=True) + "\n")
    print(f"STAGE=connect SOURCE_HASH={after['source_hash']} COMPONENTS={after['census']['components']}")
    return 0


def record() -> int:
    base = load_fixture_executor()
    base.assert_identity(); active(base)
    before = json.loads((SNAPSHOTS / f"{TX}-before.json").read_text())
    after = base.source_snapshot()
    if after["census"]["components"] != 222:
        raise SystemExit(f"final audio component count changed: {after['census']['components']}")
    live = component_records(after["source"])
    pins = pin_maps(base, {ref: live[ref] for ref in CONNECTIONS}, f"{TX}-record-pins")
    nets = endpoint_net_map(after["source"])
    for ref, mapping in CONNECTIONS.items():
        for pin_number, expected in mapping.items():
            actual = nets.get(endpoint(pins[ref][pin_number]), [])
            if actual != [expected]:
                raise SystemExit(f"final {ref}.{pin_number} nets {actual} != {[expected]}")
    for pin_number in ("7", "8", "9", "10", "11", "12"):
        if nets.get(endpoint(pins["J9-AUD"][pin_number]), []):
            raise SystemExit(f"final J9 pin {pin_number} is not open")
    for pin_number in ("1", "2", "4"):
        if nets.get(endpoint(pins["U11-AUD"][pin_number]), []):
            raise SystemExit(f"final U11 pin {pin_number} is not open")
    semantic = JOBS / f"{TX}-semantic.json"
    topology_path = JOBS / f"{TX}-topology.json"
    if topology_path.exists():
        topology = json.loads(topology_path.read_text())
    else:
        # The connect source write can land while its asynchronous bridge
        # acknowledgement is stale.  Reconstruct the expected topology from
        # the independently verified live pin/net read-back rather than
        # losing the transaction record or issuing another mutation.
        topology = {
            f"{ref}.{pin_number}": expected
            for ref, mapping in CONNECTIONS.items()
            for pin_number, expected in mapping.items()
        }
        topology_path.write_text(json.dumps(topology, indent=2, sort_keys=True) + "\n")
    semantic.write_text(json.dumps({
        "schema_version": 1, "transaction_id": TX, "project_uuid": PROJECT,
        "document_uuid": PAGE, "scope": "AUDIO_CAPTURE", "stage": "repair",
        "intended_delta": INTENDED, "pre_source_hash": before["source_hash"],
        "post_source_hash": after["source_hash"], "saved": True,
        "affected": sorted(CONNECTIONS),
        "topology": topology,
        "component_count": after["census"]["components"], "census": after["census"],
        "deliberately_open": [
            "U11 pins 1 IN1P, 2 IN1M and 4 IN2M for digital-PDM operation",
            "J9 pins 7-10 reserved and pins 11-12 mechanical tabs",
        ],
        "source_basis": [
            "Texas Instruments TLV320ADC6120 datasheet SBAS885D: pin table and sections 8.3.4 and 8.3.9",
            "K1 contracts/audio-interface.md",
            "K1 contracts/microphone-interface.md",
            "K1 IM69D130 board-wiring extraction dated 2026-08-05",
        ],
    }, indent=2, sort_keys=True) + "\n")
    base.record_mutation(base.MUTATION_STATE, base.MUTATION_LEDGER, semantic)
    print(f"POST_SOURCE_HASH={after['source_hash']}")
    print(f"SEMANTIC={semantic}")
    print("WRITE_LOCK=AWAITING_EVIDENCE")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("prepare", "prune", "add", "designate", "connect", "record"))
    args = parser.parse_args()
    return globals()[args.stage]()


if __name__ == "__main__":
    sys.exit(main())
