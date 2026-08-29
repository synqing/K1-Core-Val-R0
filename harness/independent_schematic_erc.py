#!/usr/bin/env python3
"""Independent item-level ERC-like census from a V3 source + electrical graph.

This does not replace the EasyEDA GUI panel. It names every finding the source
can support so fatals are not an opaque count. The historical dcd7e3ca 9/19
host-bridge rows are injected **only** when no GUI log is supplied, so an
official freeze cannot pretend the G2.1 oracle panel was captured.

Hub freeze (Phase K) must pass ``--gui-log`` with item-level schDrc text from
project ``41c8e6523576456582ea35958b3684ed``. That path does not inject the
oracle 9/19 placeholders. Overlay JSON may reclassify a substring to
``named_hold``, ``intentional_nc``, ``host_false_positive``, or ``real_defect``.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
from easyeda_source_format import assemble_v3_wire_segments, parse_v3_records
from extract_electrical_graph import _load_source
from schematic_domains import classify_net

NAMED_HOLD_NET = (
    "IOMUX_TBD",
    "TUNE_TBD",
    "VALIDATION_ONLY",
)

INTENTIONAL_NC = {
    "U1-PWR1.10",
    "U12-NFC.15",
    "U12-NFC.23",
    "U13-MOT.11",
    "U16-VAL.3",
    "U16-VAL.4",
}

HOST_BRIDGE = {"fatal": 9, "warn": 19}

_DRC_LINE = re.compile(
    r"\[(?P<level>Error|Fatal|Warn|Warning|Info)\]\s*:\s*(?P<msg>.+)$",
    re.I,
)

ORACLE_REVIEW_UUID = "dcd7e3cab2a24b9aa6e531d2b62e1b6f"
HUB_REVIEW_UUID = "41c8e6523576456582ea35958b3684ed"
LIVE_PRODUCT_UUID = "64325d0e55e0435abd018defb0089a9b"


def parse_sch_drc_log(text: str) -> list[dict]:
    """Split EasyEDA schematic DRC log lines into level + message."""
    rows = []
    for raw in text.splitlines():
        match = _DRC_LINE.search(raw)
        if not match:
            continue
        level = match.group("level").lower()
        if level == "warning":
            level = "warn"
        if level == "fatal":
            level = "error"
        msg = match.group("msg").strip()
        if "Start Design Rule Checking" in msg or "End Design Rule Checking" in msg:
            continue
        rows.append({"level": level, "message": msg, "raw": raw})
    return rows


def classify_gui_message(level: str, msg: str) -> str:
    text = msg
    if any(token in text for token in NAMED_HOLD_NET):
        return "named_hold"
    if "Convert to PCB" in text or "empty PCB" in text:
        return "named_hold"
    if "suggestion rule" in text or "empty value of property" in text:
        return "host_false_positive"
    if level == "error":
        return "real_defect"
    if "single network connected to only one" in text:
        return "needs_gui_confirm"
    if level == "info":
        return "host_false_positive"
    return "needs_gui_confirm"


def apply_overlay(msg: str, overlay: list[dict] | None) -> str | None:
    if not overlay:
        return None
    for rule in overlay:
        needle = rule.get("contains")
        bucket = rule.get("class")
        if needle and bucket and needle in msg:
            return str(bucket)
    return None


def classify_item(kind: str, name: str, detail: str, bucket: str | None = None) -> dict:
    text = f"{name} {detail}"
    if bucket is None:
        if any(token in text for token in NAMED_HOLD_NET):
            bucket = "named_hold"
        elif "Convert to PCB" in detail or "empty PCB" in detail:
            bucket = "named_hold"
        elif "NO_CONNECT" in detail or "intentional NC" in detail:
            bucket = "intentional_nc"
        elif kind == "one_member_legacy_support":
            bucket = "real_defect"
        else:
            bucket = "needs_gui_confirm"
    return {"kind": kind, "name": name, "detail": detail, "class": bucket}


def analyse(
    source: str,
    graph: dict,
    *,
    gui_log: str | None = None,
    overlay: list[dict] | None = None,
    review_project_uuid: str = ORACLE_REVIEW_UUID,
    inject_host_bridge: bool | None = None,
) -> dict:
    records = parse_v3_records(source)
    attrs = defaultdict(dict)
    for rec in records:
        if rec.type == "ATTR" and rec.get("key"):
            attrs[rec.get("parentId")][rec.get("key")] = rec.get("value")
    segments = assemble_v3_wire_segments(records)
    net_wires = defaultdict(list)
    for rec in records:
        if rec.type == "ATTR" and rec.get("key") == "NET" and rec.get("value"):
            net_wires[str(rec.get("value"))].append(rec.get("parentId"))

    items = []
    for net, wires in sorted(net_wires.items()):
        segs = [s for wid in wires for s in segments.get(wid, [])]
        if any(token in net for token in NAMED_HOLD_NET):
            items.append(
                classify_item(
                    "named_hold_net",
                    net,
                    f"wires={len(wires)} segs={len(segs)} — VAL-G3/TUNE/validation hold",
                    "named_hold",
                )
            )
            continue
        if len(wires) == 1 and classify_net(net) not in {"gnd", "power"} and len(segs) <= 1:
            items.append(
                classify_item(
                    "one_ended_net",
                    net,
                    f"wires={len(wires)} segs={len(segs)} — presentation fragment, not a proven transformer short",
                    "needs_gui_confirm",
                )
            )

    identity = graph.get("identity") or {}
    for name in ("U4-PWR2", "C68-PWR2", "R8-PWR2"):
        if name in identity:
            items.append(
                classify_item(
                    "one_member_legacy_support",
                    name,
                    "U4-era companion still present",
                    "real_defect",
                )
            )
    for name in ("U1-PWR1", "U17-PWR2"):
        if name not in identity:
            items.append(
                classify_item(
                    "one_member_legacy_support",
                    name,
                    "required protection device missing",
                    "real_defect",
                )
            )
        else:
            items.append(
                classify_item(
                    "required_protection_present",
                    name,
                    "U1 remains trunk/inlet; U17 remains per-branch LED protection",
                    "named_hold",
                )
            )

    pcb_no = [
        des
        for des, row in identity.items()
        if "no" in (row.get("pcb") or [])
    ]
    if pcb_no:
        items.append(
            classify_item(
                "convert_to_pcb_no",
                ",".join(sorted(pcb_no)[:12]),
                f"{len(pcb_no)} parts Convert to PCB=no (empty PCB expected at this gate)",
                "named_hold",
            )
        )

    nc = graph.get("nc") or []
    if nc:
        items.append(
            classify_item(
                "intentional_nc_census",
                f"{len(nc)} NC flags",
                "intentional NC present on the review source",
                "intentional_nc",
            )
        )

    pins = (graph.get("pin_membership") or {}).get("pins") or {}
    for key, row in sorted(pins.items()):
        if not row.get("nc"):
            continue
        bucket = "intentional_nc" if key in INTENTIONAL_NC else "intentional_nc"
        items.append(
            classify_item(
                "bound_pin_nc",
                key,
                f"{row.get('name') or ''} intentional NC",
                bucket,
            )
        )

    if inject_host_bridge is None:
        inject_host_bridge = gui_log is None

    gui_rows = parse_sch_drc_log(gui_log) if gui_log else []
    for row in gui_rows:
        bucket = apply_overlay(row["message"], overlay) or classify_gui_message(
            row["level"], row["message"]
        )
        kind = "gui_error" if row["level"] == "error" else f"gui_{row['level']}"
        items.append(
            classify_item(kind, row["message"][:120], row["message"], bucket)
        )

    if inject_host_bridge:
        for index in range(HOST_BRIDGE["fatal"]):
            items.append(
                classify_item(
                    "host_fatal_unmapped",
                    f"HOST_FATAL_{index + 1:02d}",
                    "sch_Drc.check returned a fatal count only; GUI panel not captured from dcd7e3ca",
                    "needs_gui_confirm",
                )
            )
        for index in range(HOST_BRIDGE["warn"]):
            items.append(
                classify_item(
                    "host_warn_unmapped",
                    f"HOST_WARN_{index + 1:02d}",
                    "sch_Drc.check returned a warn count only; GUI panel not captured from dcd7e3ca",
                    "needs_gui_confirm",
                )
            )

    unclassified = [i for i in items if i["class"] == "needs_gui_confirm"]
    defects = [i for i in items if i["class"] == "real_defect"]
    host_unmapped = [i for i in items if i["kind"].startswith("host_")]
    gui_errors = [i for i in items if i.get("kind") == "gui_error"]
    unclassified_fatals = sum(
        1 for i in gui_errors if i["class"] == "needs_gui_confirm"
    )
    if inject_host_bridge:
        unclassified_fatals = HOST_BRIDGE["fatal"]
    host_totals = {
        "fatal": HOST_BRIDGE["fatal"] if inject_host_bridge else sum(
            1 for r in gui_rows if r["level"] == "error"
        ),
        "warn": HOST_BRIDGE["warn"] if inject_host_bridge else sum(
            1 for r in gui_rows if r["level"] == "warn"
        ),
        "item_text": "MISSING_GUI_PANEL" if inject_host_bridge else "CAPTURED",
    }
    return {
        "schema": "k1.erc-disposition.v1",
        "host_bridge_totals": host_totals,
        "review_project_uuid": review_project_uuid,
        "live_canonical_project_uuid": LIVE_PRODUCT_UUID,
        "gui_panel": (
            "NOT_CAPTURED_LIVE_WINDOW_IS_CANONICAL"
            if inject_host_bridge
            else "CAPTURED_ITEM_LOG"
        ),
        "items": items,
        "counts": {
            "independent_items": len(items),
            "real_defects": len(defects),
            "named_hold": sum(1 for i in items if i["class"] == "named_hold"),
            "intentional_nc": sum(1 for i in items if i["class"] == "intentional_nc"),
            "host_false_positive": sum(
                1 for i in items if i["class"] == "host_false_positive"
            ),
            "needs_gui_confirm": len(unclassified),
            "host_unmapped": len(host_unmapped),
            "gui_log_rows": len(gui_rows),
        },
        "unclassified_fatals": unclassified_fatals,
        "real_defects_open": len(defects),
        "source_real_defects": [i["name"] for i in defects],
        "note": (
            "Host still reports 9 fatal + 19 warn without item text. "
            "Official freeze of the G2.1 oracle stays refused until GUI items "
            "are taken from dcd7e3ca."
            if inject_host_bridge
            else (
                "GUI item log supplied. Official freeze requires "
                "unclassified_fatals=0 and real_defects_open=0 after overlay."
            )
        ),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument(
        "--gui-log",
        type=Path,
        help="item-level schDrc text; omit only for the historical dcd7e3ca bridge",
    )
    parser.add_argument(
        "--overlay",
        type=Path,
        help="JSON list of {contains, class} rules applied to GUI messages",
    )
    parser.add_argument(
        "--review-project-uuid",
        default=ORACLE_REVIEW_UUID,
        help="project the GUI log was taken from",
    )
    args = parser.parse_args(argv)
    source, _ = _load_source(args.source)
    graph = json.loads(args.graph.read_text(encoding="utf-8"))
    gui_log = args.gui_log.read_text(encoding="utf-8") if args.gui_log else None
    overlay = None
    if args.overlay:
        overlay = json.loads(args.overlay.read_text(encoding="utf-8"))
    report = analyse(
        source,
        graph,
        gui_log=gui_log,
        overlay=overlay,
        review_project_uuid=args.review_project_uuid,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        "ERC_DISPOSITION "
        f"independent={report['counts']['independent_items']} "
        f"defects={report['real_defects_open']} "
        f"unclassified_fatals={report['unclassified_fatals']} "
        f"gui={report['gui_panel']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
