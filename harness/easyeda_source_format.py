#!/usr/bin/env python3
"""Read EasyEDA document source in BOTH serialisations, or refuse.

Why this exists
---------------
The EasyEDA Pro host was upgraded 2.2.40.8 -> 3.2.149 on 2026-08-28. The document
source format changed WHOLESALE at that boundary:

    V2 (2.2.40.8)   newline-delimited *tagged arrays*, parsed positionally:
                    ["COMPONENT", ticket, id, x, y, ...]      (arity 9)
                    ["WIRE", ticket, [segments], ...]         (arity 5)
                    ["ATTR", ticket, parent, key, value, ...] (arity 12)

    V3 (3.2.149)    newline-delimited *typed record pairs*, header || payload |:
                    {"type":"COMPONENT","ticket":2,"id":"e1"}||{"partId":...,"x":0,"y":0,...}|

Measured on the same page (1435cb46f39e48c8a8aadbb84ca81603): 6737 V2 lines, all
parseable as tagged arrays -> 7397 V3 lines, ZERO parseable as tagged arrays. Every
record type (COMPONENT, WIRE, ATTR, RECT, TEXT, DOCTYPE, ...) disappeared from the
positional grammar. Character count went 497569 -> 2154721 for identical content.

Without this module every positional parser in harness/ reports "parsed zero source
records", which reads as "the document is empty" — a badly wrong diagnosis that
invites an agent to conclude data loss. It is not empty; it is a format it cannot read.

TWO ENTRY POINTS, AND WHICH TO USE
----------------------------------
`parse_records_any_format(source, tool=...)`
    Reads EITHER grammar and returns ONE internal representation — the V2-shaped
    positional rows. Use this in any READ-ONLY analysis so the analysis itself
    never forks per host version.

`require_v2(source, tool=...)`
    Fails closed unless the snapshot is the V2 positional grammar. Kept for the
    tools that REWRITE live board source (`easyeda_remove_source_records.py`,
    `easyeda_repair_source_swap.py`). Reading V3 is a solved problem; writing it
    is not, and a write path that half-understands the grammar is how a board
    gets damaged. Those tools stay refusing until they are separately proven.
"""
from __future__ import annotations

import json
import os

V2_TAGGED_ARRAY = "V2_TAGGED_ARRAY"
V3_TYPED_RECORD = "V3_TYPED_RECORD"
UNKNOWN = "UNKNOWN"
EMPTY = "EMPTY"

# Host builds these formats belong to, for error messages.
_FORMAT_HOST = {
    V2_TAGGED_ARRAY: "EasyEDA Pro 2.2.x (archived client)",
    V3_TYPED_RECORD: "EasyEDA Pro 3.2.x (current client)",
}


class SourceFormatError(RuntimeError):
    """Raised when a snapshot is not in the serialisation the caller can parse."""


class V3RecordError(SourceFormatError):
    """A V3 record was structurally malformed, or its payload changed shape.

    Subclasses SourceFormatError so every existing fail-closed caller keeps
    failing closed without having to learn a second exception type.
    """


def _sample(lines: list[str], limit: int = 400) -> list[str]:
    """Head + tail sample, so a shared prefix cannot dominate the verdict."""
    if len(lines) <= limit:
        return lines
    half = limit // 2
    return lines[:half] + lines[-half:]


def detect_format(source: str) -> str:
    """Classify a document-source string. Never raises."""
    if not source or not source.strip():
        return EMPTY
    lines = [ln for ln in source.splitlines() if ln.strip()]
    if not lines:
        return EMPTY

    sample = _sample(lines)
    v2 = v3 = 0
    for line in sample:
        stripped = line.lstrip()
        # V3: a JSON object header, then '||', then a payload object, then a trailing '|'
        if stripped.startswith("{") and "}||" in stripped:
            v3 += 1
            continue
        if stripped.startswith("["):
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if isinstance(rec, list) and rec and isinstance(rec[0], str):
                v2 += 1

    total = len(sample)
    # A clear majority decides; anything ambiguous is UNKNOWN rather than guessed.
    if v3 and v3 >= total * 0.8:
        return V3_TYPED_RECORD
    if v2 and v2 >= total * 0.8:
        return V2_TAGGED_ARRAY
    return UNKNOWN


def describe(source: str) -> str:
    """Human-readable one-liner for logs and receipts."""
    fmt = detect_format(source)
    lines = len([ln for ln in source.splitlines() if ln.strip()]) if source else 0
    host = _FORMAT_HOST.get(fmt, "unrecognised")
    return f"{fmt} ({host}) — {lines} records, {len(source or '')} chars"


def require_v2(source: str, *, tool: str) -> None:
    """Fail closed unless `source` is the V2 positional grammar.

    For WRITE paths and for any tool not yet proven against V3. Read paths should
    use `parse_records_any_format` instead.
    """
    fmt = detect_format(source)
    if fmt == V2_TAGGED_ARRAY:
        return
    if fmt == V3_TYPED_RECORD:
        raise SourceFormatError(
            f"{tool}: refusing to parse — this snapshot is {V3_TYPED_RECORD} "
            f"(EasyEDA Pro 3.2.x, records look like "
            f'\'{{"type":"COMPONENT",...}}||{{"x":0,"y":0,...}}|\'), but this tool only '
            f"understands the V2 positional grammar (['COMPONENT', ticket, id, x, y, ...]).\n"
            f"  This is NOT an empty or damaged document. The host was upgraded on "
            f"2026-08-28 and re-serialised every page.\n"
            f"  Fix the parser for the V3 named-field grammar; do not 'repair' the board."
        )
    if fmt == EMPTY:
        raise SourceFormatError(f"{tool}: snapshot source is empty — refusing to emit a verdict")
    raise SourceFormatError(
        f"{tool}: snapshot source is in an unrecognised serialisation "
        f"(neither V2 tagged arrays nor V3 typed records) — refusing to emit a verdict"
    )


# ==========================================================================
# V3 RECORD PARSER  (3.2.149)
# ==========================================================================
# GRAMMAR, measured on schematic-P1-source-POST-V3.json (7397 records, 0 that
# fail this parse):
#
#     <header JSON object> || <payload JSON object> |
#
# The header carries {"type", "ticket", "id"}; the payload carries the NAMED
# fields V2 held POSITIONALLY. Record types on the real page:
#     ATTR 5768 · LINE 688 · WIRE 676 · COMPONENT 231 · TEXT 22 · RECT 10
#     DOCHEAD 1 · CANVAS 1
#
# TWO STRUCTURAL CHANGES THAT MATTER TO ANY CONNECTIVITY PARSER
# -------------------------------------------------------------
# 1. WIRE GEOMETRY MOVED OUT OF THE WIRE RECORD. In V2 a wire carried its own
#    segment list: ["WIRE","e968",[[80,4420,100,4420]],"st11",0]. In V3 the WIRE
#    payload is ONLY {"zIndex":236,"locked":false} — the geometry lives in
#    separate LINE records that point back with `lineGroup`:
#        {"type":"LINE",...}||{"startX":80,"startY":-4420,"endX":100,
#                              "endY":-4420,"lineGroup":"e968"}|
#    A parser that looks for coordinates in the V3 WIRE payload finds NONE and
#    concludes the sheet has no wiring. It has 676 wires and 688 segments.
#
# 2. THE Y AXIS IS NEGATED relative to V2. V2 `[80,4420,100,4420]` is V3
#    `startY:-4420`. Verified across the WHOLE page, not sampled: all 676 wire
#    ids match, all 676 segment lists match after negation (0 mismatches), and
#    231 of 231 COMPONENT anchors match after negation (only e1, at the origin,
#    matches without it).
#
#    This is the step that decides whether the oracle is right or catastrophically
#    wrong, because pin read-backs are mapped into the V2 source frame by
#    check_schematic_connectivity's own (x, y) -> (x, -y). Leave V3 coordinates
#    un-negated and every pin lands 2y away from its wire: the pin landing rate
#    collapses to ~0% and the oracle reports an entire sheet of floating pins,
#    confidently and falsely. So V3 is normalised INTO the V2 frame here, once,
#    at the parse boundary — and the `--self-test` differential below re-derives
#    that equality from the two real snapshots on every run.
V3_Y_SIGN = -1
V3_SEPARATOR = "||"

# The record-shape contract. A payload of a known type MUST carry these fields.
# A renamed field (x -> posX), a removed field, or a truncated payload violates
# it, and a violation is FAIL-CLOSED — never a silently emptier document.
V3_REQUIRED_PAYLOAD_FIELDS = {
    "COMPONENT": ("x", "y", "rotation"),
    "LINE": ("startX", "startY", "endX", "endY", "lineGroup"),
    "ATTR": ("parentId", "key", "value"),
    "TEXT": ("x", "y", "value"),
}
# Fields that must additionally BE NUMBERS. A null coordinate is drift, not a
# value. `value` on ATTR/TEXT is deliberately absent here: null there is legal.
V3_NUMERIC_PAYLOAD_FIELDS = {
    "COMPONENT": ("x", "y"),
    "LINE": ("startX", "startY", "endX", "endY"),
    "TEXT": ("x", "y"),
}


class V3Record:
    """One parsed `header || payload |` line, with named-field access."""

    __slots__ = ("type", "ticket", "id", "payload", "line_no")

    def __init__(self, type_: str, ticket, id_, payload: dict, line_no=None) -> None:
        self.type = type_
        self.ticket = ticket
        self.id = id_
        self.payload = payload
        self.line_no = line_no

    def get(self, field, default=None):
        return self.payload.get(field, default)

    def __repr__(self) -> str:  # pragma: no cover - debug aid only
        return f"V3Record(type={self.type!r}, id={self.id!r}, line={self.line_no!r})"


def _raw_decode_one(text: str, idx: int):
    """Decode exactly one JSON value starting at idx.

    `raw_decode` is used rather than `json.loads` on a split string because it
    reports the END OFFSET, which is what lets the separator be verified in
    place. It raises ValueError on truncation — which is the point.
    """
    return json.JSONDecoder().raw_decode(text, idx)


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _check_payload_shape(rec: V3Record) -> None:
    """RECORD-SHAPE DRIFT gate. Raises if a known type lost or renamed a field."""
    where = f" (line {rec.line_no})" if rec.line_no is not None else ""
    required = V3_REQUIRED_PAYLOAD_FIELDS.get(rec.type)
    if required:
        missing = [f for f in required if f not in rec.payload]
        if missing:
            raise V3RecordError(
                f"V3 {rec.type} record {rec.id!r}{where} is missing required payload field(s) "
                f"{missing} — RECORD-SHAPE DRIFT. Present fields: {sorted(rec.payload)}.\n"
                f"  A field was renamed or removed by a host change. Refusing to parse: a "
                f"parser that shrugs at this reports a SMALLER sheet, not a broken one, and "
                f"every verdict computed on it is wrong in the reassuring direction."
            )
    for field in V3_NUMERIC_PAYLOAD_FIELDS.get(rec.type, ()):
        if not _is_number(rec.payload.get(field)):
            raise V3RecordError(
                f"V3 {rec.type}.{field} on record {rec.id!r}{where} is "
                f"{rec.payload.get(field)!r}, not a number — RECORD-SHAPE DRIFT"
            )


def parse_v3_line(line: str, *, line_no: int | None = None) -> V3Record:
    """Parse one V3 `header||payload|` record line.

    Raises V3RecordError on any structural break (missing '||' separator, a
    header or payload that is not valid JSON, a non-object payload, a header
    without 'type', a payload whose shape drifted). A corrupt line is a fault to
    surface, never a line to skip.
    """
    where = f" (line {line_no})" if line_no is not None else ""
    stripped = line.strip()
    if not stripped.startswith("{"):
        raise V3RecordError(
            f"V3 record does not start with a header object{where}: {stripped[:80]!r}"
        )
    try:
        header, end = _raw_decode_one(stripped, 0)
    except ValueError as exc:
        raise V3RecordError(f"V3 header is not valid JSON{where}: {exc}") from exc
    if not isinstance(header, dict) or "type" not in header:
        raise V3RecordError(f"V3 header missing required 'type' field{where}: {header!r}")
    if stripped[end : end + len(V3_SEPARATOR)] != V3_SEPARATOR:
        raise V3RecordError(
            f"V3 record missing '{V3_SEPARATOR}' separator after header{where} — "
            f"TRUNCATED OR CORRUPT LINE"
        )
    try:
        payload, _end2 = _raw_decode_one(stripped, end + len(V3_SEPARATOR))
    except ValueError as exc:
        raise V3RecordError(
            f"V3 payload is not valid JSON{where} — TRUNCATED RECORD: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise V3RecordError(
            f"V3 payload is not a JSON object{where}: {type(payload).__name__}"
        )
    rtype = header["type"]
    if not isinstance(rtype, str) or not rtype:
        raise V3RecordError(f"V3 header 'type' is not a non-empty string{where}: {rtype!r}")
    rec = V3Record(rtype, header.get("ticket"), header.get("id"), payload, line_no)
    _check_payload_shape(rec)
    return rec


def parse_v3_records(source: str) -> list[V3Record]:
    """Parse every non-blank line of a V3 document source, in file order.

    Raises on the FIRST malformed line rather than skipping it. A partial parse
    of a document source is the worst outcome available to a connectivity
    oracle: it yields a smaller, still-plausible sheet and a confident verdict
    about a document that was never read.
    """
    records: list[V3Record] = []
    for line_no, line in enumerate(source.split("\n"), start=1):
        if not line.strip():
            continue
        records.append(parse_v3_line(line, line_no=line_no))
    return records


def assemble_v3_wire_segments(records: list[V3Record]) -> dict:
    """Reassemble WIRE geometry from LINE records via `lineGroup`.

    Coordinates are normalised into the V2 frame (y -> -y) here, at the parse
    boundary, so nothing downstream has to know which host wrote the file.
    """
    wire_ids = {r.id for r in records if r.type == "WIRE" and r.id is not None}
    segments: dict = {}
    orphan_groups: set = set()
    for r in records:
        if r.type != "LINE":
            continue
        group = r.get("lineGroup")
        if group not in wire_ids:
            orphan_groups.add(group)
            continue
        segments.setdefault(group, []).append(
            [
                int(r.get("startX")),
                V3_Y_SIGN * int(r.get("startY")),
                int(r.get("endX")),
                V3_Y_SIGN * int(r.get("endY")),
            ]
        )
    # A rename of the WIRE<->LINE join key presents as "this sheet has no
    # wiring" — the exact shape of failure this module exists to stop.
    if wire_ids and not segments:
        raise V3RecordError(
            f"{len(wire_ids)} WIRE record(s) declared but NOT ONE received any LINE geometry "
            f"— the LINE.lineGroup join key no longer resolves to WIRE ids (orphan groups "
            f"seen: {sorted(g for g in orphan_groups if g)[:5]}). RECORD-SHAPE DRIFT: "
            f"refusing rather than reporting an unwired sheet."
        )
    return segments


def to_v2_shaped_rows(records: list[V3Record]) -> list:
    """Convert parsed V3 records into the V2 positional row shape.

    ONE internal representation, so downstream analysis never forks per host
    version. Arities match V2 exactly (COMPONENT 9, WIRE 5, ATTR 12) so any
    existing positional consumer indexes them unchanged.
    """
    wire_segments = assemble_v3_wire_segments(records)
    rows: list = []
    for r in records:
        if r.type == "COMPONENT":
            rows.append(
                [
                    "COMPONENT",
                    r.id,
                    r.get("partId") or "",
                    int(r.get("x")),
                    V3_Y_SIGN * int(r.get("y")),
                    r.get("rotation") or 0,
                    1 if r.get("isMirror") else 0,
                    r.get("attrs") if isinstance(r.get("attrs"), dict) else {},
                    1 if r.get("locked") else 0,
                ]
            )
        elif r.type == "WIRE":
            rows.append(["WIRE", r.id, wire_segments.get(r.id, []), None, 0])
        elif r.type == "ATTR":
            rows.append(
                [
                    "ATTR",
                    r.id,
                    r.get("parentId"),
                    r.get("key"),
                    r.get("value"),
                    None, None, None, None, None, None, 0,
                ]
            )
        elif r.type == "TEXT":
            rows.append(
                ["TEXT", r.id, int(r.get("x")), V3_Y_SIGN * int(r.get("y")), r.get("value")]
            )
        elif r.type == "LINE":
            continue  # folded into its owning WIRE above
        else:
            rows.append([r.type, r.id])
    return rows


def parse_records_any_format(source: str, *, tool: str) -> list:
    """Format-agnostic READ entry point: detect V2/V3, always return V2-shaped rows.

    Replaces the `require_v2(...)` + positional-loop pattern in read-only tools.
    V2 sources are parsed exactly as before; V3 sources go through
    parse_v3_records + to_v2_shaped_rows, so no downstream logic forks.
    """
    fmt = detect_format(source)
    if fmt == V2_TAGGED_ARRAY:
        rows: list = []
        for line in source.split("\n"):
            line = line.strip()
            if not line.startswith("["):
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, list) and row:
                rows.append(row)
        return rows
    if fmt == V3_TYPED_RECORD:
        return to_v2_shaped_rows(parse_v3_records(source))
    if fmt == EMPTY:
        raise SourceFormatError(f"{tool}: snapshot source is empty — refusing to emit a verdict")
    raise SourceFormatError(
        f"{tool}: snapshot source is in an unrecognised serialisation "
        f"(neither V2 tagged arrays nor V3 typed records) — refusing to emit a verdict"
    )


# --------------------------------------------------------------------------
# Real snapshots — the differential pair. Same page, same board, captured
# minutes apart across the host upgrade. Overridable for portability.
# --------------------------------------------------------------------------
_ARCHIVE = "/Users/spectrasynq/SpectraSynq-EDA/_archive/easyeda-backups/2026-08-28"
REAL_V2_SNAPSHOT = os.environ.get("K1_V2_SNAPSHOT", f"{_ARCHIVE}/schematic-P1-source-1305.json")
REAL_V3_SNAPSHOT = os.environ.get(
    "K1_V3_SNAPSHOT", f"{_ARCHIVE}/schematic-P1-source-POST-V3.json"
)


def topology_digest(rows: list) -> dict:
    """Grammar-independent summary of a parsed sheet, for the differential.

    Deliberately re-derived from the ROWS, not from either parser's internals:
    if the two grammars produce the same digest, they produced the same sheet.
    """
    wires: dict = {}
    components: dict = {}
    designators: set = set()
    wire_nets: dict = {}
    for row in rows:
        if row[0] == "WIRE" and len(row) > 2 and isinstance(row[2], list) and row[2]:
            wires[row[1]] = sorted(tuple(int(v) for v in s[:4]) for s in row[2] if len(s) >= 4)
        elif row[0] == "COMPONENT" and len(row) > 4:
            components[row[1]] = (row[3], row[4])
    for row in rows:
        if row[0] != "ATTR" or len(row) < 5:
            continue
        if row[3] == "Designator" and row[4]:
            designators.add(str(row[4]))
        elif row[3] == "NET" and row[4] and row[2] in wires:
            wire_nets[row[2]] = str(row[4])
    return {
        "designators": designators,
        "components": components,
        "wires": wires,
        "wire_nets": wire_nets,
        "nets": set(wire_nets.values()),
    }


def _load_snapshot_source(path: str) -> str:
    with open(path) as fh:
        blob = json.load(fh)
    return blob["source"] if isinstance(blob, dict) and "source" in blob else blob


def _self_test() -> int:
    """Fault battery. Must go RED on the cases it exists to catch."""
    v2 = '["DOCTYPE","SCH",1]\n["COMPONENT",2,"e1",0,0,0,0,0,0]\n["WIRE",3,[[1,2]],0,0]'
    v3 = ('{"type":"DOCHEAD"}||{"docType":"SCH_PAGE"}|\n'
          '{"type":"COMPONENT","ticket":2,"id":"e1"}||'
          '{"partId":"p","x":0,"y":0,"rotation":0}|')

    # Hand-built V3 fixtures for the shape-drift battery. None are derived from
    # the real snapshots — the real snapshots are exercised separately below.
    v3_good = (
        '{"type":"COMPONENT","ticket":1,"id":"e1"}||{"x":10,"y":-20,"rotation":0}|\n'
        '{"type":"ATTR","ticket":2,"id":"e2"}||{"key":"Designator","value":"C1","parentId":"e1"}|\n'
        '{"type":"WIRE","ticket":3,"id":"e3"}||{"zIndex":1,"locked":false}|\n'
        '{"type":"LINE","ticket":4,"id":"e4"}||'
        '{"startX":0,"startY":-20,"endX":10,"endY":-20,"lineGroup":"e3"}|'
    )
    # Same fields, reordered — must parse identically (proves we are not
    # accidentally position-dependent INSIDE the payload objects).
    v3_reordered = (
        '{"id":"e1","ticket":1,"type":"COMPONENT"}||{"rotation":0,"y":-20,"x":10}|\n'
        '{"id":"e2","type":"ATTR","ticket":2}||{"parentId":"e1","value":"C1","key":"Designator"}|\n'
        '{"type":"WIRE","id":"e3","ticket":3}||{"locked":false,"zIndex":1}|\n'
        '{"type":"LINE","id":"e4","ticket":4}||'
        '{"lineGroup":"e3","endY":-20,"endX":10,"startY":-20,"startX":0}|'
    )
    v3_renamed_attr = (  # parentId -> parent_id
        '{"type":"ATTR","ticket":2,"id":"e2"}||{"key":"Designator","value":"C1","parent_id":"e1"}|'
    )
    v3_renamed_component = (  # x -> posX
        '{"type":"COMPONENT","ticket":1,"id":"e1"}||{"posX":10,"y":-20,"rotation":0}|'
    )
    v3_missing_line_field = (  # LINE lost startX
        '{"type":"WIRE","ticket":3,"id":"e3"}||{"zIndex":1,"locked":false}|\n'
        '{"type":"LINE","ticket":4,"id":"e4"}||'
        '{"startY":0,"endX":10,"endY":0,"lineGroup":"e3"}|'
    )
    v3_null_coordinate = (  # field present but nulled
        '{"type":"COMPONENT","ticket":1,"id":"e1"}||{"x":null,"y":-20,"rotation":0}|'
    )
    v3_join_key_renamed = (  # lineGroup no longer resolves to any WIRE id
        '{"type":"WIRE","ticket":3,"id":"e3"}||{"zIndex":1,"locked":false}|\n'
        '{"type":"LINE","ticket":4,"id":"e4"}||'
        '{"startX":0,"startY":0,"endX":10,"endY":0,"lineGroup":"GROUP-e3"}|'
    )
    v3_truncated_payload = '{"type":"WIRE","ticket":1,"id":"e1"}||{"zIndex":1'
    v3_truncated_header = '{"type":"WIRE","ticket":1'
    v3_no_separator = '{"type":"WIRE","ticket":1,"id":"e1"}{"zIndex":1}|'

    expected_good_rows = [
        ["COMPONENT", "e1", "", 10, 20, 0, 0, {}, 0],
        ["ATTR", "e2", "e1", "Designator", "C1", None, None, None, None, None, None, 0],
        ["WIRE", "e3", [[0, 20, 10, 20]], None, 0],
    ]

    cases = [
        ("v2 detected",        lambda: detect_format(v2) == V2_TAGGED_ARRAY),
        ("v3 detected",        lambda: detect_format(v3) == V3_TYPED_RECORD),
        ("empty detected",     lambda: detect_format("") == EMPTY),
        ("garbage is UNKNOWN", lambda: detect_format("hello\nworld") == UNKNOWN),
        ("require_v2 passes on v2", lambda: require_v2(v2, tool="t") is None),
        # --- V3 GREEN cases ---
        ("v3 good parses to 4 records", lambda: len(parse_v3_records(v3_good)) == 4),
        ("v3 rows are V2-shaped AND y-normalised (y:-20 -> 20)",
         lambda: to_v2_shaped_rows(parse_v3_records(v3_good)) == expected_good_rows),
        ("v3 reordered payload fields parse identically (named, not positional)",
         lambda: to_v2_shaped_rows(parse_v3_records(v3_reordered))
         == to_v2_shaped_rows(parse_v3_records(v3_good))),
        ("parse_records_any_format accepts V2",
         lambda: len(parse_records_any_format(v2, tool="t")) == 3),
        ("parse_records_any_format accepts V3",
         lambda: len(parse_records_any_format(v3_good, tool="t")) == 3),
    ]
    failed = 0
    for name, fn in cases:
        try:
            ok = fn()
        except Exception as exc:  # noqa: BLE001 - self-test reports, never masks
            ok, name = False, f"{name} (raised {exc.__class__.__name__}: {exc})"
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
        failed += 0 if ok else 1

    # ---- negative controls: these MUST raise, or the guard is decorative ----
    negative_cases = [
        ("require_v2 rejects v3", lambda: require_v2(v3, tool="t"), SourceFormatError),
        ("require_v2 rejects empty", lambda: require_v2("", tool="t"), SourceFormatError),
        ("parse_records_any_format rejects garbage",
         lambda: parse_records_any_format("hello\nworld", tool="t"), SourceFormatError),
        ("DRIFT: ATTR parentId renamed -> parent_id",
         lambda: parse_records_any_format(v3_renamed_attr, tool="t"), V3RecordError),
        ("DRIFT: COMPONENT x renamed -> posX",
         lambda: parse_records_any_format(v3_renamed_component, tool="t"), V3RecordError),
        ("DRIFT: LINE lost startX",
         lambda: parse_records_any_format(v3_missing_line_field, tool="t"), V3RecordError),
        ("DRIFT: COMPONENT x present but null",
         lambda: parse_records_any_format(v3_null_coordinate, tool="t"), V3RecordError),
        ("DRIFT: lineGroup join key renamed — wires would silently lose all geometry",
         lambda: parse_records_any_format(v3_join_key_renamed, tool="t"), V3RecordError),
        ("TRUNCATED: payload cut mid-object",
         lambda: parse_v3_records(v3_truncated_payload), V3RecordError),
        ("TRUNCATED: header cut mid-object",
         lambda: parse_v3_records(v3_truncated_header), V3RecordError),
        ("TRUNCATED: '||' separator missing",
         lambda: parse_v3_records(v3_no_separator), V3RecordError),
    ]
    for name, fn, expected_exc in negative_cases:
        try:
            fn()
        except expected_exc:
            print(f"  PASS  {name}  <- went RED as required")
        except Exception as exc:  # noqa: BLE001
            print(f"  FAIL  {name} — raised {exc.__class__.__name__}, wanted "
                  f"{expected_exc.__name__}: {exc}")
            failed += 1
        else:
            print(f"  FAIL  {name} — guard did not fire")
            failed += 1

    # ---- REAL-SNAPSHOT DIFFERENTIAL --------------------------------------
    # The only check here with an EXTERNAL denominator: two independent captures
    # of the same page, one per grammar. If the V3 parse is right, the two
    # digests are identical. If it is not, no amount of synthetic fixture
    # passing means anything.
    print("  REAL-SNAPSHOT DIFFERENTIAL (V2 capture vs V3 capture of the same page):")
    have_both = os.path.isfile(REAL_V2_SNAPSHOT) and os.path.isfile(REAL_V3_SNAPSHOT)
    if not have_both:
        print(f"        V2: {REAL_V2_SNAPSHOT}")
        print(f"        V3: {REAL_V3_SNAPSHOT}")
        if os.environ.get("K1_ALLOW_MISSING_SNAPSHOTS") == "1":
            print("  NOT-RUN  snapshots absent and K1_ALLOW_MISSING_SNAPSHOTS=1 — the "
                  "differential DID NOT RUN, so this run proves only the synthetic battery")
        else:
            print("  FAIL  snapshots not on this host — refusing to report a green battery "
                  "whose only external check did not run (set K1_ALLOW_MISSING_SNAPSHOTS=1 "
                  "to downgrade to NOT-RUN, or point K1_V2_SNAPSHOT/K1_V3_SNAPSHOT at them)")
            failed += 1
    else:
        try:
            d2 = topology_digest(
                parse_records_any_format(_load_snapshot_source(REAL_V2_SNAPSHOT), tool="self-test")
            )
            d3 = topology_digest(
                parse_records_any_format(_load_snapshot_source(REAL_V3_SNAPSHOT), tool="self-test")
            )
            print(f"        V2: {len(d2['designators'])} designators, {len(d2['wires'])} wires, "
                  f"{len(d2['wire_nets'])} named wires, {len(d2['nets'])} nets")
            print(f"        V3: {len(d3['designators'])} designators, {len(d3['wires'])} wires, "
                  f"{len(d3['wire_nets'])} named wires, {len(d3['nets'])} nets")
            checks = [
                ("designator SET identical across grammars", d2["designators"] == d3["designators"]),
                ("designator count is 228", len(d3["designators"]) == 228),
                ("wire id SET identical", set(d2["wires"]) == set(d3["wires"])),
                ("wire SEGMENT GEOMETRY identical (this is the y-negation proof)",
                 d2["wires"] == d3["wires"]),
                ("COMPONENT anchors identical", d2["components"] == d3["components"]),
                ("wire -> net map identical", d2["wire_nets"] == d3["wire_nets"]),
            ]
            for name, ok in checks:
                print(f"  {'PASS' if ok else 'FAIL'}  {name}")
                failed += 0 if ok else 1
        except Exception as exc:  # noqa: BLE001 - integration failure must be visible
            print(f"  FAIL  differential raised {exc.__class__.__name__}: {exc}")
            failed += 1

    print("SELF-TEST:", "PASS" if failed == 0 else f"FAIL ({failed})")
    return 1 if failed else 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        raise SystemExit(_self_test())
    data = sys.stdin.read()
    try:
        blob = json.loads(data)
        data = blob.get("source", data) if isinstance(blob, dict) else data
    except ValueError:
        pass
    print(describe(data))
