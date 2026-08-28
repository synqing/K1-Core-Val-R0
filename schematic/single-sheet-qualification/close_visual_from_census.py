#!/usr/bin/env python3
"""Assemble an EasyEDA visual-evidence record from an INSPECTION THAT ACTUALLY HAPPENED.

=============================================================================
WHY THIS FILE WAS REWRITTEN — 2026-08-28
=============================================================================
This file is preserved rather than deleted because the mechanism it used to
implement is the single clearest false-green in this repository, and the shape
of it is worth keeping on the record.

The previous version built the visual record itself. It hardcoded four checks,
every one of them `"result": "OK"`, and `"verdict": "ACCEPTED"`, filling the
mandatory `detail` strings from the semantic census — which is derived from
`get_document_source`, not from anybody looking at the canvas. Verbatim, the
third check it emitted was:

    {
      "name": "changed labels pins and geometry readable",
      "result": "OK",
      "detail": "Pin glyphs are not readable at whole-sheet zoom. "
                "Named-net ATTR census in the semantic read-back is the "
                "electrical proof."
    }

The detail string states plainly that the thing the check is named after could
not be seen. The result says OK anyway. Running the script therefore satisfied
`harness/easyeda_mutation_gate.py close` — which requires four granular checks,
each with a non-empty detail, all OK for an ACCEPTED verdict — and moved the
gate to READY, with nobody having read the canvas at any point.

That is the entire failure class: the gate was measuring the SHAPE of the
evidence record, and this script manufactured a correctly shaped record. Canon
K1E-059 says agents capture and inspect the screenshots; a script that writes
"OK" on their behalf is how that rule gets bypassed without anyone lying.

It also read the mutation state from `evidence/VAL-G2-2026-08-28/
EASYEDA-MUTATION-STATE.json` — the RETIRED lane — while the canonical lane is
`canonical-core-val-r0/`. So it could report the wrong gate phase too.

=============================================================================
WHAT IT DOES NOW
=============================================================================
It cannot produce an OK. Every check result and detail must be supplied on the
command line by whoever inspected the screenshot, along with an attestation of
who did the inspecting. This script only:

  * resolves the live lane and confirms the gate is AWAITING_EVIDENCE
  * checks the supplied check NAMES against the `expected_checks` the
    transaction declared at `begin` — you may not answer a different question
    from the one the transaction asked
  * attaches the semantic census as CONTEXT, clearly labelled as such and never
    as the basis of any result
  * refuses outright when the record would repeat the historical lie: a check
    about readability of pins, labels or geometry may not be OK at
    `whole_sheet` scale, because pin glyphs are not readable at that zoom on
    this host — that is a measured property of the host, not an opinion
  * refuses auto-generated or placeholder detail text
  * hands the finished record to the gate

If you want an ACCEPTED verdict you must look at the screenshot, at a scale
that shows the delta, and say so in your own words.

Run `--self-test` for the fault battery, which includes the auto-accept attempt
this file used to perform and asserts that it is refused.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GATE = REPO / "harness/easyeda_mutation_gate.py"

VISUAL_SCALES = {"block", "whole_sheet", "both"}
VISUAL_RESULTS = {"OK", "DEFECT"}
VERDICTS = {"ACCEPTED", "REJECTED"}

# A check whose name is about seeing detail cannot be answered from a whole-sheet
# capture on this host. This is the exact claim the old version made.
READABILITY_TERMS = re.compile(r"\b(readab|legib|glyph|pin|label|designator|text)", re.IGNORECASE)

# Detail text that is not an observation. Refusing these keeps the record from
# drifting back into census-derived boilerplate.
BANNED_DETAIL = re.compile(
    r"(not readable at whole-sheet zoom"
    r"|is the electrical proof"
    r"|semantic read-back can substitute"
    r"|^n/?a$|^ok$|^none$|^see census$|^auto)",
    re.IGNORECASE,
)
MIN_DETAIL_CHARS = 40


class Refused(RuntimeError):
    """Raised when the record would assert something nobody observed."""


def validate_check(check: dict) -> dict:
    """Every path into the record runs this — CLI parsing and direct calls alike.

    It lived only in the CLI parser at first, and the fault battery caught that:
    a direct call to build_visual_record sailed past the boilerplate rule. A guard
    that only sits on one route is not a guard.
    """
    if not isinstance(check, dict):
        raise Refused(f"check must be an object, got {type(check).__name__}")
    name = str(check.get("name") or "").strip()
    result = str(check.get("result") or "").strip()
    detail = str(check.get("detail") or "").strip()
    if not name:
        raise Refused("check name is empty")
    if result not in VISUAL_RESULTS:
        raise Refused(f"check {name!r} result must be one of {sorted(VISUAL_RESULTS)}, got {result!r}")
    if len(detail) < MIN_DETAIL_CHARS:
        raise Refused(
            f"check {name!r} detail is {len(detail)} chars; at least {MIN_DETAIL_CHARS} are required. "
            "Describe what you saw in the screenshot."
        )
    if BANNED_DETAIL.search(detail):
        raise Refused(
            f"check {name!r} detail matches known non-observation boilerplate: {detail!r}. "
            "This is the phrasing the auto-accepting version of this script emitted."
        )
    return {"name": name, "result": result, "detail": detail}


def parse_check(raw: str) -> dict:
    """--check 'NAME|RESULT|detail written by the person who looked'"""
    parts = raw.split("|", 2)
    if len(parts) != 3:
        raise Refused(
            f"--check must be 'NAME|RESULT|detail', got: {raw!r}. "
            "The detail is your observation, not a template."
        )
    name, result, detail = (part.strip() for part in parts)
    return validate_check({"name": name, "result": result, "detail": detail})


def build_visual_record(
    *,
    transaction_id: str,
    project_uuid: str,
    document_uuid: str,
    intended_delta: str,
    expected_checks: list[str],
    observed_delta: str,
    screenshot_path: str,
    scale: str,
    checks: list[dict],
    verdict: str,
    inspected_by: str,
    unexpected_changes: list[str],
    census: dict | None,
) -> dict:
    if scale not in VISUAL_SCALES:
        raise Refused(f"--scale must be one of {sorted(VISUAL_SCALES)}")
    if verdict not in VERDICTS:
        raise Refused(f"--verdict must be one of {sorted(VERDICTS)}")
    if not inspected_by.strip():
        raise Refused("--inspected-by is required: name the agent or person who read the screenshot")
    if len(observed_delta.strip()) < MIN_DETAIL_CHARS:
        raise Refused(
            f"--observed is {len(observed_delta.strip())} chars; at least {MIN_DETAIL_CHARS} required. "
            "Say what the canvas actually shows, not what was intended."
        )
    if not checks:
        raise Refused("no --check supplied; this script will not invent any")
    checks = [validate_check(check) for check in checks]

    names = [check["name"] for check in checks]
    if len(set(names)) != len(names):
        raise Refused(f"duplicate check names: {names}")
    missing = [name for name in expected_checks if name not in names]
    if missing:
        raise Refused(
            f"the transaction declared these checks at begin and they were not answered: {missing}. "
            "Answer the question the transaction asked."
        )
    extra = [name for name in names if name not in expected_checks]
    if extra:
        raise Refused(
            f"these checks were not declared by the transaction: {extra}. "
            f"Declared: {expected_checks}"
        )

    # The historical lie, made structurally impossible.
    if scale == "whole_sheet":
        offenders = [
            check["name"] for check in checks
            if check["result"] == "OK" and READABILITY_TERMS.search(check["name"])
        ]
        if offenders:
            raise Refused(
                f"checks {offenders} are about reading fine detail and are marked OK at "
                "scale=whole_sheet. Pin glyphs are not readable at whole-sheet zoom on this "
                "host — that is exactly the claim the auto-accepting version of this script "
                "made. Re-capture the affected block at scale=block or scale=both and inspect "
                "it, or mark the check DEFECT."
            )

    if verdict == "ACCEPTED":
        defects = [check["name"] for check in checks if check["result"] != "OK"]
        if defects:
            raise Refused(f"verdict ACCEPTED but these checks are DEFECT: {defects}")
        if unexpected_changes:
            raise Refused("verdict ACCEPTED but unexpected_changes is non-empty")
    else:
        if not unexpected_changes and all(check["result"] == "OK" for check in checks):
            raise Refused(
                "verdict REJECTED but every check is OK and no unexpected change is named — "
                "the gate requires a rejected record to identify a defect"
            )

    record = {
        "schema_version": 1,
        "transaction_id": transaction_id,
        "project_uuid": project_uuid,
        "document_uuid": document_uuid,
        "intended_delta": intended_delta,
        "observed_delta": observed_delta,
        "screenshot_path": screenshot_path,
        "captured_after_settle": True,
        "scale": scale,
        "unexpected_changes": unexpected_changes,
        "verdict": verdict,
        "checks": checks,
        "inspected_by": inspected_by,
        "evidence_provenance": (
            "Every check result and detail above was supplied by the named inspector from the "
            "screenshot. The semantic census below is CONTEXT ONLY and is not the basis of any "
            "result — see the header of close_visual_from_census.py."
        ),
    }
    if census is not None:
        record["semantic_census_context"] = census
    return record


# --------------------------------------------------------------------------
# lane / state
# --------------------------------------------------------------------------

def resolve_state_path() -> Path:
    """Ask the gate which lane is live rather than hardcoding one (see header)."""
    proc = subprocess.run(
        [sys.executable, str(GATE), "lanes"],
        cwd=str(REPO), capture_output=True, text=True, timeout=30,
    )
    if proc.returncode != 0:
        raise Refused(f"gate could not enumerate lanes:\n{proc.stdout}{proc.stderr}")
    live = [
        line.split("]", 1)[1].strip()
        for line in proc.stdout.splitlines()
        if line.strip().startswith("[LIVE")
    ]
    if len(live) != 1:
        raise Refused(f"expected exactly one live mutation lane, found {len(live)}: {live}")
    directory = REPO / live[0]
    for name in ("MUTATION-STATE.json", "EASYEDA-MUTATION-STATE.json"):
        if (directory / name).is_file():
            return directory / name
    raise Refused(f"live lane {directory} has no mutation state file")


# --------------------------------------------------------------------------
# fault battery
# --------------------------------------------------------------------------

def _base_kwargs(**overrides):
    kwargs = {
        "transaction_id": "battery-tx",
        "project_uuid": "64325d0e55e0435abd018defb0089a9b",
        "document_uuid": "1435cb46f39e48c8a8aadbb84ca81603",
        "intended_delta": "battery fixture",
        "expected_checks": ["block visible", "no debris", "changed pins readable", "no unrelated movement"],
        "observed_delta": "The settled capture shows the four new decoupling caps beside U12 with their designators.",
        "screenshot_path": "evidence/battery.png",
        "scale": "block",
        "checks": [
            {"name": "block visible", "result": "OK",
             "detail": "Box 7 fills the frame; all ten new parts are inside the rectangle and legible."},
            {"name": "no debris", "result": "OK",
             "detail": "No question-mark designators and no leftover placeholder symbols anywhere in box 7."},
            {"name": "changed pins readable", "result": "OK",
             "detail": "Pin 1 and pin 2 numerals on C92 through C97 are individually readable at this zoom."},
            {"name": "no unrelated movement", "result": "OK",
             "detail": "Boxes 1 through 6 and 8 through 10 are pixel-identical to the pre-mutation capture."},
        ],
        "verdict": "ACCEPTED",
        "inspected_by": "agent:battery",
        "unexpected_changes": [],
        "census": {"components": 230, "wires": 675},
    }
    kwargs.update(overrides)
    return kwargs


def run_self_test() -> int:
    cases: list[tuple[str, str, str, dict]] = []

    cases.append(("well-formed block inspection", "ACCEPTED", "a real block-scale inspection is allowed through", _base_kwargs()))

    # THE HISTORICAL AUTO-ACCEPT, reconstructed exactly as the old script emitted it.
    auto = _base_kwargs(
        scale="whole_sheet",
        checks=[
            {"name": "block visible", "result": "OK",
             "detail": "Settled screenshot of the qualification sheet. Census: 230 components, 675 wires."},
            {"name": "no debris", "result": "OK",
             "detail": "Affected 10. Undesignated tokens now: none. Census derived from get_document_source."},
            {"name": "changed pins readable", "result": "OK",
             "detail": "Pin glyphs are not readable at whole-sheet zoom. Named-net ATTR census in the "
                       "semantic read-back is the electrical proof."},
            {"name": "no unrelated movement", "result": "OK",
             "detail": "Saved=True. Single Option-C sheet. Scope canonical stage wire, per the census."},
        ],
    )
    cases.append(("historical auto-accept", "REFUSED", "the exact record the old script wrote must be refused", auto))

    cases.append(("readability OK at whole_sheet", "REFUSED", "fine-detail check marked OK at whole-sheet zoom",
                  _base_kwargs(scale="whole_sheet")))
    cases.append(("boilerplate detail", "REFUSED", "detail is census boilerplate, not an observation",
                  _base_kwargs(checks=[
                      dict(_base_kwargs()["checks"][0]),
                      dict(_base_kwargs()["checks"][1]),
                      {"name": "changed pins readable", "result": "OK",
                       "detail": "Named-net ATTR census in the semantic read-back is the electrical proof."},
                      dict(_base_kwargs()["checks"][3]),
                  ])))
    cases.append(("no checks supplied", "REFUSED", "script must not invent checks", _base_kwargs(checks=[])))
    cases.append(("unanswered declared check", "REFUSED", "a check declared at begin was skipped",
                  _base_kwargs(checks=_base_kwargs()["checks"][:3])))
    cases.append(("undeclared extra check", "REFUSED", "answering a question the transaction never asked",
                  _base_kwargs(checks=_base_kwargs()["checks"] + [
                      {"name": "invented check", "result": "OK",
                       "detail": "This check was never declared by the transaction at begin time."}])))
    cases.append(("accepted with a defect", "REFUSED", "ACCEPTED verdict over a DEFECT check",
                  _base_kwargs(checks=[
                      dict(_base_kwargs()["checks"][0]),
                      dict(_base_kwargs()["checks"][1]),
                      {"name": "changed pins readable", "result": "DEFECT",
                       "detail": "C95 designator is overlapped by the wire label and cannot be read."},
                      dict(_base_kwargs()["checks"][3]),
                  ])))
    cases.append(("no inspector named", "REFUSED", "attestation of who looked is mandatory",
                  _base_kwargs(inspected_by="   ")))
    cases.append(("observed delta too thin", "REFUSED", "one-word observation is not an observation",
                  _base_kwargs(observed_delta="ok")))
    cases.append(("rejected without a defect", "REFUSED", "REJECTED must name what is wrong",
                  _base_kwargs(verdict="REJECTED")))

    print("CLOSE_VISUAL_SELF_TEST")
    failures = 0
    refused_seen = 0
    for name, expected, description, kwargs in cases:
        try:
            build_visual_record(**kwargs)
            observed, reason = "ACCEPTED", ""
        except Refused as exc:
            observed, reason = "REFUSED", str(exc)
            refused_seen += 1
        ok = observed == expected
        failures += 0 if ok else 1
        print(f"  [{'ok ' if ok else 'BAD'}] {name:30} expected={expected:9} observed={observed:9} {description}")
        if observed == "REFUSED":
            print(f"          refused: {reason.splitlines()[0][:140]}")
    print(f"  cases={len(cases)} refused_observed={refused_seen}")
    if refused_seen == 0:
        print("SELF_TEST=FAIL-CLOSED battery produced no REFUSED case — it is testing nothing", file=sys.stderr)
        return 2
    if failures:
        print(f"SELF_TEST=FAIL {failures} case(s) did not match expectation", file=sys.stderr)
        return 1
    print("SELF_TEST=OK auto-accept is structurally refused, including the exact historical record")
    return 0


# --------------------------------------------------------------------------
# cli
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--screenshot", type=Path)
    ap.add_argument("--observed", help="what the screenshot actually shows, in your own words")
    ap.add_argument("--scale", choices=sorted(VISUAL_SCALES))
    ap.add_argument("--inspected-by", help="agent id or person who read the screenshot")
    ap.add_argument("--check", action="append", dest="checks", default=[],
                    help="'NAME|OK or DEFECT|what you saw' — repeat once per declared check")
    ap.add_argument("--unexpected", action="append", dest="unexpected", default=[])
    ap.add_argument("--verdict", choices=sorted(VERDICTS))
    ap.add_argument("--dry-run", action="store_true", help="write the record but do not call the gate")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return run_self_test()

    required = {
        "--screenshot": args.screenshot, "--observed": args.observed, "--scale": args.scale,
        "--inspected-by": args.inspected_by, "--verdict": args.verdict,
    }
    absent = [flag for flag, value in required.items() if not value]
    if absent:
        print(f"CLOSE_VISUAL=REFUSED missing required arguments: {absent}", file=sys.stderr)
        print("This script no longer supplies any of these on your behalf.", file=sys.stderr)
        return 2

    try:
        screenshot = args.screenshot.expanduser()
        if not screenshot.is_absolute():
            screenshot = (REPO / screenshot).resolve()
        if not screenshot.is_file():
            raise Refused(f"missing screenshot {screenshot}")

        state_path = resolve_state_path()
        state = json.loads(state_path.read_text())
        active = state.get("active_transaction") or {}
        transaction_id = active.get("transaction_id")
        if state.get("state") != "AWAITING_EVIDENCE" or not transaction_id:
            raise Refused(f"gate is {state.get('state')}; need AWAITING_EVIDENCE")

        jobs = state_path.parent / "jobs"
        semantic_path = jobs / f"{transaction_id}-semantic.json"
        census = None
        if semantic_path.is_file():
            census = json.loads(semantic_path.read_text()).get("census")

        record = build_visual_record(
            transaction_id=transaction_id,
            project_uuid=state["project_uuid"],
            document_uuid=state["document_uuid"],
            intended_delta=active["intended_delta"],
            expected_checks=list(active.get("expected_checks") or []),
            observed_delta=args.observed,
            screenshot_path=str(screenshot),
            scale=args.scale,
            checks=[parse_check(raw) for raw in args.checks],
            verdict=args.verdict,
            inspected_by=args.inspected_by,
            unexpected_changes=list(args.unexpected),
            census=census,
        )
    except Refused as exc:
        print(f"CLOSE_VISUAL=REFUSED {exc}", file=sys.stderr)
        return 2
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"CLOSE_VISUAL=REFUSED {exc}", file=sys.stderr)
        return 2

    visual_path = jobs / f"{transaction_id}-visual.json"
    visual_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(f"CLOSE_VISUAL=RECORD_WRITTEN {visual_path}")
    if args.dry_run:
        print("CLOSE_VISUAL=DRY_RUN gate not called")
        return 0

    proc = subprocess.run(
        [sys.executable, str(GATE), "--state", str(state_path),
         "--ledger", str(state_path.parent / state_path.name.replace("STATE.json", "LEDGER.jsonl")),
         "close", "--visual", str(visual_path)],
        cwd=str(REPO), capture_output=True, text=True, timeout=30,
    )
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
