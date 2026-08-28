#!/usr/bin/env python3
"""Fail-closed validation for the canonical K1 single-sheet EasyEDA read-back."""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
DEFAULT_READBACK = (
    REPO
    / "evidence/VAL-G2-2026-08-28/canonical-core-val-r0/jobs/final-readback-results.json"
)
PLAN = REPO / "schematic/single-sheet-qualification/FIXTURE-PLAN.json"
LAYOUT = REPO / "schematic/single-sheet-qualification/LAYOUT-PLAN.json"

PROJECT_UUID = "64325d0e55e0435abd018defb0089a9b"
SCHEMATIC_UUID = "cffcdb562c1b48d1a5214cfc263b6c90"
PAGE_UUID = "1435cb46f39e48c8a8aadbb84ca81603"
FORBIDDEN_PROJECT_UUID = "09e9c541fd3d404082d4b92e55ae5336"

SUFFIX_BY_CONTAINER = {
    1: "PWR1",
    2: "PWR2",
    3: "RTC",
    4: "RTDBG",
    5: "ESP",
    6: "AUD",
    7: "NFC",
    8: "MOT",
    9: "LED",
    10: "VAL",
}
BOXES = {
    1: (0, 3605, 910, 4720),
    2: (955, 3605, 1915, 4725),
    3: (1965, 3605, 2925, 4725),
    4: (2975, 3605, 3935, 4725),
    5: (3990, 3605, 4950, 4725),
    6: (0, 2425, 910, 3535),
    7: (950, 2420, 1910, 3540),
    8: (1960, 2410, 2920, 3530),
    9: (2975, 2410, 3935, 3530),
    10: (3990, 2405, 4950, 3525),
}
EXPECTED_TITLES = {
    "1. POWER ENTRY + PROTECTION",
    "2. POWER CONVERSION + DISTRIBUTION",
    "3. RT1062 COMPUTE + CORE POWER",
    "4. RT1062 BOOT + CLOCK + DEBUG",
    "5. ESP32-S3 RADIO + SERVICE + K1BR",
    "6. AUDIO CAPTURE + CLOCK + MIC FLEX",
    "7. NFC FRONT END + ANTENNA",
    "8. MOTION / ACCELEROMETER",
    "9. LED DATA + TEMPERATURE",
    "10. DEBUG / RECOVERY + VALIDATION OPTIONS",
}
FORBIDDEN_NAME = re.compile(r"QUAL|PADDING|DUMMY|STRESS", re.IGNORECASE)


class CheckError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckError(message)


def load_tagged_results(path: Path) -> dict[str, dict]:
    require(path.is_file(), f"read-back file missing: {path}")
    raw = json.loads(path.read_text())
    require(isinstance(raw, list) and raw, "zero MCP read-back records parsed")
    tagged = {str(item.get("tag")): item for item in raw if isinstance(item, dict)}
    for tag in ("context", "project_objects", "source"):
        require(tag in tagged, f"missing required read-back record: {tag}")
        require(tagged[tag].get("ok") is True, f"required read-back failed: {tag}")
        require(isinstance(tagged[tag].get("result"), dict), f"invalid result object: {tag}")
    return tagged


def expected_designators() -> set[str]:
    plan = json.loads(PLAN.read_text())
    layout = json.loads(LAYOUT.read_text())
    components = {
        item["ref"]: item
        for item in plan.get("components", [])
        if item.get("fixture_only") is False
    }
    require(components, "zero source-derived plan components parsed")
    block_container = {
        key: int(value["container"])
        for key, value in layout.get("domains", {}).items()
    }
    expected: set[str] = set()
    for block in plan.get("blocks", []):
        block_id = block.get("id")
        require(block_id in block_container, f"plan block has no domain container: {block_id}")
        suffix = SUFFIX_BY_CONTAINER[block_container[block_id]]
        for ref in block.get("component_refs", []):
            if ref in components:
                expected.add(f"{ref}-{suffix}")
    require(expected, "zero expected canonical designators derived")
    return expected


def parse_source(source: str) -> list[list]:
    require(source, "document source is empty")
    rows: list[list] = []
    for number, line in enumerate(source.splitlines(), 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CheckError(f"invalid source record at line {number}: {exc}") from exc
        require(isinstance(row, list) and row, f"invalid source row at line {number}")
        rows.append(row)
    require(rows and rows[0][:3] == ["DOCTYPE", "SCH", "1.1"], "source is not EasyEDA SCH 1.1")
    return rows


def check(readback: Path, expected_source_hash: str | None = None) -> dict:
    tagged = load_tagged_results(readback)
    context = tagged["context"]["result"]
    objects = tagged["project_objects"]["result"]
    source_result = tagged["source"]["result"]

    project = context.get("currentProject") or {}
    document = context.get("currentDocument") or {}
    require(project.get("uuid") != FORBIDDEN_PROJECT_UUID, "forbidden qualification project is active")
    require(project.get("uuid") == PROJECT_UUID, f"wrong project UUID: {project.get('uuid')}")
    require(project.get("friendlyName") == "K1-Core-Val-R0", "wrong canonical project name")
    require(document.get("uuid") == PAGE_UUID, f"wrong document UUID: {document.get('uuid')}")
    require(document.get("documentType") == 1, "active document is not a schematic page")

    schematics = objects.get("schematics")
    require(isinstance(schematics, list) and len(schematics) == 1, "canonical project must contain exactly one schematic")
    schematic = schematics[0]
    require(schematic.get("uuid") == SCHEMATIC_UUID, "wrong canonical schematic UUID")
    pages = schematic.get("page")
    require(isinstance(pages, list) and len(pages) == 1, "canonical schematic must contain exactly one page")
    require(pages[0].get("uuid") == PAGE_UUID, "project-tree page UUID mismatch")

    source_hash = source_result.get("sourceHash")
    require(isinstance(source_hash, str) and source_hash, "source hash missing")
    if expected_source_hash is not None:
        require(source_hash == expected_source_hash, f"stale source hash: {source_hash}")
    require(source_result.get("documentUuid") == PAGE_UUID, "source document UUID mismatch")
    rows = parse_source(source_result.get("source") or "")

    components = {row[1]: row for row in rows if row[0] == "COMPONENT"}
    designator_attrs = [
        row for row in rows
        if row[0] == "ATTR" and len(row) > 4 and row[3] == "Designator"
    ]
    require(components, "zero component records parsed")
    require(designator_attrs, "zero electrical designators parsed")
    raw_designators = [str(row[4]) for row in designator_attrs]
    actual = set(raw_designators)
    expected = expected_designators()
    require(actual == expected, f"designator inventory mismatch missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    duplicates = {key: count for key, count in collections.Counter(raw_designators).items() if count > 1}
    require(duplicates == {"U6-RTC": 2}, f"unexpected duplicate designators: {duplicates}")

    suffix_to_container = {suffix: number for number, suffix in SUFFIX_BY_CONTAINER.items()}
    anchor_violations: list[str] = []
    for attr in designator_attrs:
        designator = str(attr[4])
        match = re.search(r"-([A-Z0-9]{3,5})$", designator)
        require(match is not None and match.group(1) in suffix_to_container, f"invalid domain suffix: {designator}")
        component = components.get(attr[2])
        require(component is not None, f"designator parent component missing: {designator}")
        x, y = component[3], component[4]
        box_number = suffix_to_container[match.group(1)]
        x1, y1, x2, y2 = BOXES[box_number]
        if not (x1 <= x <= x2 and y1 <= y <= y2):
            anchor_violations.append(f"{designator}@{x},{y}->box{box_number}")
    require(not anchor_violations, f"component anchors outside assigned boxes: {anchor_violations}")

    rectangles = [row for row in rows if row[0] == "RECT"]
    texts = [row for row in rows if row[0] == "TEXT"]
    require(len(rectangles) == 10, f"expected 10 domain rectangles, found {len(rectangles)}")
    require(len(texts) == 10, f"expected 10 domain titles, found {len(texts)}")
    titles = {str(row[5]) for row in texts if len(row) > 5}
    require(titles == EXPECTED_TITLES, f"domain title inventory mismatch: {sorted(titles ^ EXPECTED_TITLES)}")
    box6 = next(row for row in texts if row[5] == "6. AUDIO CAPTURE + CLOCK + MIC FLEX")
    require(box6[2] >= 0, "Box 6 title starts outside native sheet")

    page_attrs = {
        str(row[3]): str(row[4])
        for row in rows
        if row[0] == "ATTR" and len(row) > 4 and row[2] == "e1"
    }
    require(page_attrs.get("Page Size") == "Custom", "page size is not Custom")
    require(page_attrs.get("Width") == "5000", "page width is not 5000")
    require(page_attrs.get("Height") == "4800", "page height is not 4800")

    net_attrs = [row for row in rows if row[0] == "ATTR" and len(row) > 4 and row[3] == "NET"]
    require(net_attrs, "zero named-net records parsed")
    forbidden_names = [str(row[4]) for row in net_attrs if FORBIDDEN_NAME.search(str(row[4]))]
    forbidden_names.extend(name for name in raw_designators if FORBIDDEN_NAME.search(name))
    require(not forbidden_names, f"qualification/padding names found: {sorted(set(forbidden_names))}")

    net_counts = collections.Counter(str(row[4]) for row in net_attrs)
    return {
        "project_uuid": PROJECT_UUID,
        "schematics": len(schematics),
        "pages": len(pages),
        "source_hash": source_hash,
        "source_records": len(rows),
        "components_including_frame": len(components),
        "unique_designators": len(actual),
        "designator_records": len(raw_designators),
        "rectangles": len(rectangles),
        "titles": len(texts),
        "wires": sum(row[0] == "WIRE" for row in rows),
        "unique_named_nets": len(net_counts),
        "single_occurrence_nets": sorted(name for name, count in net_counts.items() if count == 1),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--readback", type=Path, default=DEFAULT_READBACK)
    parser.add_argument("--expected-source-hash")
    args = parser.parse_args()
    try:
        summary = check(args.readback, args.expected_source_hash)
    except (CheckError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"SINGLE_SCHEMATIC_CHECK=ERROR {exc}", file=sys.stderr)
        return 1
    print("SINGLE_SCHEMATIC_CHECK=OK")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
