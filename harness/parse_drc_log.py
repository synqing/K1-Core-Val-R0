#!/usr/bin/env python3
"""Structured parser for EasyEDA Pro schematic DRC logs.

WHY THIS EXISTS

Four separate scripts in this repository hand-transcribed this log into Python
dict literals. A hand-transcription is a second, undocumented parser with no
denominator: nobody could tell whether a finding had been dropped, mistyped, or
quietly waived by omission. This ends that.

WHAT IT MEASURES

Line format: `YYYY-MM-DD HH:MM:SS[Level] :  message`, levels Info / Warn /
Fatal Error. EasyEDA batches long lists at roughly 30 tokens per line, so one
logical finding (e.g. "these 200 pins are floating") arrives as seven Warn
lines; the parser re-aggregates them. It also uses the ideographic comma `、`
as an intra-field separator alongside the ASCII comma, so both are honoured.

Findings are classified into named kinds. Anything that does NOT match a known
shape is reported as `unclassified` and, by default, makes the run RED —
silently dropping a message shape you have not taught the parser about is the
exact mechanism that lets a defect leave a log without leaving a record.

THE DENOMINATOR IS EXTERNAL

The log ends with its own census — `Fatal Error: N, Error: N, Warning: N,
Info: N`. That line is the authority this parse is measured against, not the
parse's own output. If the observed level counts do not reconcile with the
declared ones, the parse FAILS CLOSED rather than reporting a tidy subset.

WAIVERS

A waiver register records known-intentional findings as waived-WITH-REASON.
Waivers never delete a finding — they move it to a `waived` bucket that is
printed and counted. A waiver that matches nothing is itself an error (a stale
waiver silently stops protecting anything), so the register is checked in both
directions.

FAULT BATTERY — `--self-test`. Includes cases expected to be RED and cases
expected to FAIL CLOSED, and asserts both actually happen (canon K1E-054,
K1E-055).

EXIT CODES
  0  GREEN        — parsed, reconciled, no unwaived Warn/Fatal, no unclassified
  1  RED          — parsed and reconciled, but findings remain
  2  FAIL-CLOSED  — could not parse or could not reconcile; no verdict possible
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from collections import Counter, defaultdict

SCHEMA_VERSION = 1

LINE_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\[(?P<level>[^\]]+)\]\s*:\s*(?P<msg>.*)$"
)

# EasyEDA mixes the ideographic comma with the ASCII one inside a single field.
SEPARATORS = re.compile(r"[,、]")

# EasyEDA emits NON-BREAKING and other exotic spaces inside message text — the real
# 2026-08-28 log contains "components Pins floating". These are invisible in a
# terminal and are exactly what a hand-transcription silently normalises away, which
# is how a mis-transcribed finding stops matching without anyone noticing. Normalise
# them for matching, keep the raw message, and COUNT how many lines needed it.
EXOTIC_SPACE = re.compile(r"[   　 - ]")

LEVELS = {"Info", "Warn", "Error", "Fatal Error"}


class FailClosed(RuntimeError):
    """Raised when the parse cannot honestly reach any verdict."""


# --------------------------------------------------------------------------
# message classification
# --------------------------------------------------------------------------

def _split(text: str) -> list[str]:
    return [tok.strip() for tok in SEPARATORS.split(text) if tok.strip()]


CLASSIFIERS: list[tuple[str, re.Pattern, str]] = [
    ("start", re.compile(r"^Start Design Rule Checking\.?$"), "DRC run began"),
    (
        "summary",
        re.compile(
            r"^Finish Design Rule Checking\.\s*"
            r"Fatal Error:\s*(?P<fatal>\d+),\s*Error:\s*(?P<error>\d+),\s*"
            r"Warning:\s*(?P<warning>\d+),\s*Info:\s*(?P<info>\d+)\.?$"
        ),
        "DRC run census — the external denominator for this parse",
    ),
    (
        "single_pin_net",
        re.compile(
            r"^The wire (?P<net>\S+) (?P<wires>[\$\w、,]+) is a single network "
            r"connected to only one component pin\.?$"
        ),
        "a named net EasyEDA resolved to exactly one component pin",
    ),
    (
        "designator_style",
        re.compile(
            r'^The property "Designator" of Component (?P<component>\S+) '
            r"doesn't match the suggestion rule\..*$"
        ),
        "designator does not match EasyEDA's suggested letter+number form",
    ),
    (
        "empty_value",
        re.compile(r'^Component (?P<component>\S+) has empty value of property "Value"\.?$'),
        "component carries no Value property",
    ),
    (
        "net_name_not_displayed",
        re.compile(
            r"^Wires and buses are not connected to netflag or netport, "
            r"name not displayed in the canvas:\s*(?P<names>.+)$"
        ),
        "named wires with no netflag/netport — the name is not shown on the canvas",
    ),
    (
        "multipart_property_mismatch",
        re.compile(
            r"^Component (?P<device>.+?) is a multi-part component, the properties of each "
            r"part should be the same\.\s*(?P<parts>[\$\w、,]+) have different property "
            r"(?P<properties>.+?)\.?$"
        ),
        "parts of one multi-part component disagree on a property",
    ),
    (
        "supplier_standardisation",
        re.compile(
            r"^Component attributes does not match the Supplier Part, It is recommended to "
            r"use Device Standardization:\s*:?\s*(?P<items>.+)$"
        ),
        "component attributes diverge from the supplier part record",
    ),
    (
        "floating_pins",
        re.compile(
            r"^Found some components Pins floating, suggest placing No Connect Flag on "
            r"the Pins\s*:\s*(?P<pins>.+)$"
        ),
        "pins with neither a wire nor a No-Connect flag",
    ),
    (
        "pad_without_pin",
        re.compile(
            r"^The pin of the component (?P<device>.+?) does not correspond to the pad "
            r"\(Pad has no corresponding pin:\s*(?P<pads>[^)]+)\):\s*(?P<components>.+)$"
        ),
        "footprint pads with no matching symbol pin",
    ),
]

KIND_DESCRIPTIONS = {kind: desc for kind, _re, desc in CLASSIFIERS}
KIND_DESCRIPTIONS["unclassified"] = "message shape this parser has not been taught"

ITEM_REF = re.compile(r"^(?P<ref>.+?)\((?P<component>\$\w+)\)$")


def classify(level: str, message: str) -> dict:
    for kind, pattern, _desc in CLASSIFIERS:
        match = pattern.match(message)
        if not match:
            continue
        finding = {"kind": kind, "level": level, "message": message}
        groups = match.groupdict()
        if kind == "summary":
            finding["declared"] = {
                "Fatal Error": int(groups["fatal"]),
                "Error": int(groups["error"]),
                "Warn": int(groups["warning"]),
                "Info": int(groups["info"]),
            }
        elif kind == "single_pin_net":
            finding["net"] = groups["net"]
            finding["wire_ids"] = _split(groups["wires"])
            finding["items"] = [groups["net"]]
        elif kind in ("designator_style", "empty_value"):
            finding["component"] = groups["component"]
            finding["items"] = [groups["component"]]
        elif kind == "net_name_not_displayed":
            finding["items"] = _split(groups["names"])
        elif kind == "multipart_property_mismatch":
            finding["device"] = groups["device"]
            finding["parts"] = _split(groups["parts"])
            finding["properties"] = _split(groups["properties"])
            finding["items"] = _split(groups["parts"])
        elif kind == "supplier_standardisation":
            refs = []
            for token in _split(groups["items"]):
                m = ITEM_REF.match(token)
                refs.append(m.group("ref") if m else token)
            finding["items"] = refs
        elif kind == "floating_pins":
            finding["items"] = _split(groups["pins"])
        elif kind == "pad_without_pin":
            finding["device"] = groups["device"]
            finding["pads"] = _split(groups["pads"])
            finding["items"] = _split(groups["components"])
        else:
            finding["items"] = []
        return finding
    return {"kind": "unclassified", "level": level, "message": message, "items": []}


# --------------------------------------------------------------------------
# waiver register
# --------------------------------------------------------------------------

def load_waivers(path: pathlib.Path | None) -> list[dict]:
    if path is None:
        return []
    payload = json.loads(path.read_text())
    waivers = payload.get("waivers")
    if not isinstance(waivers, list):
        raise FailClosed(f"waiver register has no 'waivers' list: {path}")
    for index, waiver in enumerate(waivers):
        for key in ("kind", "match", "reason", "authority"):
            if not waiver.get(key):
                raise FailClosed(f"waiver[{index}] in {path} is missing required field {key!r}")
    return waivers


def apply_waivers(findings: list[dict], waivers: list[dict]) -> dict:
    """Move waived ITEMS into a waived bucket. Nothing is ever deleted."""
    hits = Counter()
    waived: list[dict] = []
    for finding in findings:
        remaining = []
        for item in finding.get("items", []):
            matched = None
            for index, waiver in enumerate(waivers):
                if waiver["kind"] != finding["kind"]:
                    continue
                if waiver["match"] == item or re.fullmatch(waiver["match"], item or ""):
                    matched = index
                    break
            if matched is None:
                remaining.append(item)
            else:
                hits[matched] += 1
                waived.append(
                    {
                        "kind": finding["kind"],
                        "item": item,
                        "reason": waivers[matched]["reason"],
                        "authority": waivers[matched]["authority"],
                    }
                )
        finding["items"] = remaining
        finding["fully_waived"] = bool(waivers) and not remaining and finding["kind"] not in (
            "start",
            "summary",
        )
    stale = [
        {"index": i, "kind": w["kind"], "match": w["match"], "reason": w["reason"]}
        for i, w in enumerate(waivers)
        if hits[i] == 0
    ]
    return {"waived": waived, "stale_waivers": stale, "waiver_hits": dict(hits)}


# --------------------------------------------------------------------------
# parse + reconcile
# --------------------------------------------------------------------------

def parse(text: str, waivers: list[dict]) -> dict:
    lines = text.splitlines()
    findings: list[dict] = []
    unparseable: list[str] = []
    normalised_lines = 0
    for line in lines:
        if not line.strip():
            continue
        match = LINE_RE.match(line)
        if not match:
            unparseable.append(line)
            continue
        level = match.group("level").strip()
        raw = match.group("msg").strip()
        message = EXOTIC_SPACE.sub(" ", raw)
        if message != raw:
            normalised_lines += 1
        finding = classify(level, message)
        if message != raw:
            finding["raw_message"] = raw
        findings.append(finding)

    if not findings:
        raise FailClosed(
            f"parsed zero DRC findings from {len(lines)} line(s) — refusing to report a DRC verdict"
        )

    summaries = [f for f in findings if f["kind"] == "summary"]
    if not summaries:
        raise FailClosed(
            "no 'Finish Design Rule Checking' summary line — the log has no external "
            "denominator, so this parse cannot be shown to be complete"
        )
    declared = summaries[-1]["declared"]

    observed = Counter()
    for finding in findings:
        if finding["kind"] in ("start", "summary"):
            continue
        observed[finding["level"]] += 1

    reconciliation = {
        level: {"declared": declared.get(level, 0), "observed": observed.get(level, 0)}
        for level in sorted(set(declared) | set(observed))
    }
    mismatched = {
        level: values for level, values in reconciliation.items()
        if values["declared"] != values["observed"]
    }
    if mismatched:
        raise FailClosed(
            "DRC level counts do not reconcile with the log's own summary line "
            f"(declared vs observed): {mismatched}"
        )

    waiver_result = apply_waivers(findings, waivers)

    by_kind: dict[str, list[dict]] = defaultdict(list)
    for finding in findings:
        by_kind[finding["kind"]].append(finding)

    items_by_kind = {
        kind: sorted({item for f in group for item in f.get("items", [])})
        for kind, group in by_kind.items()
    }

    unclassified = by_kind.get("unclassified", [])
    open_findings = [
        f for f in findings
        if f["kind"] not in ("start", "summary")
        and f["level"] in ("Warn", "Error", "Fatal Error")
        and not f.get("fully_waived")
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "counts": {
            "log_lines": len(lines),
            "lines_parsed": len(findings),
            "lines_unparseable": len(unparseable),
            "lines_needing_space_normalisation": normalised_lines,
            "findings_by_kind": dict(sorted(Counter(f["kind"] for f in findings).items())),
            "findings_by_level": dict(sorted(Counter(f["level"] for f in findings).items())),
            "distinct_items_by_kind": {k: len(v) for k, v in sorted(items_by_kind.items())},
            "waived_items": len(waiver_result["waived"]),
            "stale_waivers": len(waiver_result["stale_waivers"]),
            "unclassified_lines": len(unclassified),
            "open_warn_or_worse": len(open_findings),
        },
        "declared_summary": declared,
        "reconciliation": reconciliation,
        "kind_descriptions": {k: KIND_DESCRIPTIONS.get(k, "") for k in sorted(by_kind)},
        "items_by_kind": items_by_kind,
        "waived": waiver_result["waived"],
        "stale_waivers": waiver_result["stale_waivers"],
        "unparseable_lines": unparseable[:20],
        "unclassified_messages": [f["message"] for f in unclassified][:20],
        "findings": findings,
        "verdict": "RED" if (open_findings or unclassified or waiver_result["stale_waivers"]) else "GREEN",
    }


# --------------------------------------------------------------------------
# fault battery
# --------------------------------------------------------------------------

FIXTURE_DIR = pathlib.Path(__file__).resolve().parent / "fixtures" / "drc"

# (fixture stem, expected verdict, description, required fail-closed reason, required counts)
#
# `required counts` is the positive control: a case can reach the right VERDICT for
# entirely the wrong reason. The nbsp case is RED either way — what proves the
# non-breaking-space handling is that it is red with unclassified_lines == 0.
BATTERY = [
    ("clean", "GREEN", "start + summary declaring zero findings", None, None),
    ("waived-warn", "GREEN", "one Warn fully covered by a waiver register", None, None),
    ("unwaived-warn", "RED", "one Warn with no waiver", None, None),
    ("stale-waiver", "RED", "waiver register entry that matches nothing", None, None),
    ("unclassified", "RED", "well-formed line with a message shape the parser does not know", None,
     {"unclassified_lines": 1}),
    ("nbsp-floating-pins", "RED",
     "floating-pin Warn containing a non-breaking space, as the real EasyEDA log does", None,
     {"unclassified_lines": 0, "lines_needing_space_normalisation": 1, "open_warn_or_worse": 1}),
    ("empty", "FAIL-CLOSED", "zero parseable lines", "parsed zero DRC findings", None),
    ("garbage", "FAIL-CLOSED", "text with no DRC line format at all", "parsed zero DRC findings", None),
    ("no-summary", "FAIL-CLOSED", "findings but no census line to measure them against",
     "no external denominator", None),
    ("count-mismatch", "FAIL-CLOSED", "summary declares more findings than the log contains",
     "do not reconcile", None),
]


def run_self_test(verbose: bool = True) -> int:
    if not FIXTURE_DIR.is_dir():
        print(f"SELF_TEST=FAIL-CLOSED fixture directory missing: {FIXTURE_DIR}", file=sys.stderr)
        return 2
    results = []
    for stem, expected, description, want_reason, want_counts in BATTERY:
        log = FIXTURE_DIR / f"{stem}.txt"
        register = FIXTURE_DIR / f"{stem}.waivers.json"
        if not log.is_file():
            results.append([stem, expected, "MISSING-FIXTURE", description, None, False])
            continue
        matched_reason = True
        try:
            waivers = load_waivers(register if register.is_file() else None)
            report = parse(log.read_text(), waivers)
            observed, detail = report["verdict"], report["counts"]
            if want_counts:
                wrong = {
                    key: {"want": value, "got": detail.get(key)}
                    for key, value in want_counts.items()
                    if detail.get(key) != value
                }
                if wrong:
                    matched_reason = False
                    detail = dict(detail)
                    detail["POSITIVE_CONTROL_FAILED"] = wrong
        except FailClosed as exc:
            observed, detail = "FAIL-CLOSED", str(exc)
            if want_reason is not None:
                matched_reason = want_reason in detail
        results.append([stem, expected, observed, description, detail, matched_reason])

    failures = [r for r in results if r[1] != r[2] or not r[5]]
    if verbose:
        print("DRC_PARSE_SELF_TEST")
        print(f"  fixture dir = {FIXTURE_DIR}")
        for stem, expected, observed, description, detail, matched_reason in results:
            mark = "ok " if (expected == observed and matched_reason) else "BAD"
            print(f"  [{mark}] {stem:16} expected={expected:12} observed={observed:12} {description}")
            if observed == "RED" and isinstance(detail, dict):
                print(
                    f"          open_warn_or_worse={detail['open_warn_or_worse']} "
                    f"unclassified={detail['unclassified_lines']} "
                    f"stale_waivers={detail['stale_waivers']} "
                    f"nbsp_normalised={detail['lines_needing_space_normalisation']}"
                )
            if isinstance(detail, dict) and "POSITIVE_CONTROL_FAILED" in detail:
                print(f"          POSITIVE CONTROL FAILED: {detail['POSITIVE_CONTROL_FAILED']}")
                print("          right verdict, wrong reason — the case proves nothing as it stands")
            if observed == "FAIL-CLOSED":
                print(f"          reason: {detail}")
                if not matched_reason:
                    print("          WRONG GUARD FIRED — the intended guard is not the one that caught this")
    red_seen = sum(1 for r in results if r[2] == "RED")
    closed_seen = sum(1 for r in results if r[2] == "FAIL-CLOSED")
    if verbose:
        print(f"  cases={len(results)} red_observed={red_seen} fail_closed_observed={closed_seen}")
    if not results:
        print("SELF_TEST=FAIL-CLOSED zero battery cases ran", file=sys.stderr)
        return 2
    if red_seen == 0 or closed_seen == 0:
        print("SELF_TEST=FAIL-CLOSED battery produced no RED or no FAIL-CLOSED case", file=sys.stderr)
        return 2
    if failures:
        print(f"SELF_TEST=FAIL {len(failures)} case(s) did not match expectation", file=sys.stderr)
        return 1
    print("SELF_TEST=OK every battery case matched its expectation, including the RED ones")
    return 0


# --------------------------------------------------------------------------
# cli
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", type=pathlib.Path, help="EasyEDA schematic DRC log")
    ap.add_argument("--waivers", type=pathlib.Path, help="waiver register JSON")
    ap.add_argument("--json-out", type=pathlib.Path)
    ap.add_argument("--max-list", type=int, default=12)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.log:
        print("DRC_PARSE=FAIL-CLOSED --log is required (or use --self-test)", file=sys.stderr)
        return 2
    if not args.log.is_file():
        print(f"DRC_PARSE=FAIL-CLOSED log not found: {args.log}", file=sys.stderr)
        return 2

    try:
        waivers = load_waivers(args.waivers)
        report = parse(args.log.read_text(), waivers)
    except FailClosed as exc:
        print(f"DRC_PARSE=FAIL-CLOSED {exc}", file=sys.stderr)
        return 2
    except (OSError, json.JSONDecodeError, re.error) as exc:
        print(f"DRC_PARSE=FAIL-CLOSED {exc}", file=sys.stderr)
        return 2

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    counts = report["counts"]
    print(f"DRC_PARSE={report['verdict']}")
    print(f"  log_lines          = {counts['log_lines']}")
    print(f"  lines_parsed       = {counts['lines_parsed']}")
    print(f"  lines_unparseable  = {counts['lines_unparseable']}")
    print(f"  nbsp_normalised    = {counts['lines_needing_space_normalisation']}")
    print(f"  unclassified_lines = {counts['unclassified_lines']}")
    print(f"  waived_items       = {counts['waived_items']}")
    print(f"  stale_waivers      = {counts['stale_waivers']}")
    print(f"  open_warn_or_worse = {counts['open_warn_or_worse']}")
    print("reconciliation against the log's own summary line")
    for level, values in report["reconciliation"].items():
        flag = "ok" if values["declared"] == values["observed"] else "MISMATCH"
        print(f"  {level:12} declared={values['declared']:5} observed={values['observed']:5} {flag}")
    print("findings by kind (lines / distinct items)")
    for kind, lines in report["counts"]["findings_by_kind"].items():
        items = report["counts"]["distinct_items_by_kind"].get(kind, 0)
        print(f"  {kind:28} lines={lines:4} items={items:5}  {report['kind_descriptions'].get(kind,'')}")
    for kind in ("single_pin_net", "floating_pins", "pad_without_pin"):
        items = report["items_by_kind"].get(kind)
        if items:
            print(f"{kind} ({len(items)}): {items[: args.max_list]}"
                  + (" ..." if len(items) > args.max_list else ""))
    if report["waived"]:
        print(f"waived ({len(report['waived'])}):")
        for entry in report["waived"][: args.max_list]:
            print(f"  {entry['kind']}/{entry['item']} — {entry['reason']} [{entry['authority']}]")
    if report["stale_waivers"]:
        print(f"STALE WAIVERS ({len(report['stale_waivers'])}) — these protect nothing:")
        for entry in report["stale_waivers"]:
            print(f"  {entry['kind']}/{entry['match']} — {entry['reason']}")
    if report["unclassified_messages"]:
        print("UNCLASSIFIED MESSAGES:")
        for message in report["unclassified_messages"]:
            print(f"  {message}")
    if args.json_out:
        print(f"report written to {args.json_out}")
    return 1 if report["verdict"] == "RED" else 0


if __name__ == "__main__":
    sys.exit(main())
