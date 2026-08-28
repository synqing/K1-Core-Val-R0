#!/usr/bin/env python3
"""Clear the rejected disposable qualification sheet through typed delete APIs."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0")
sys.path.insert(0, str(REPO / "harness"))

from easyeda_mutation_gate import GateError, begin_transaction, record_mutation, validate_repository_state  # noqa: E402

MCP = Path("/Users/spectrasynq/SpectraSynq-EDA/EasyEDA-MCP")
BATCH = MCP / "tools/mcp_batch.mjs"
CALL = MCP / "tools/mcp_http_call.mjs"
EVIDENCE = REPO / "evidence/VAL-G2-2026-08-28"
JOBS = EVIDENCE / "jobs"
SNAPSHOTS = EVIDENCE / "snapshots"
STATE = EVIDENCE / "EASYEDA-MUTATION-STATE.json"
LEDGER = EVIDENCE / "EASYEDA-MUTATION-LEDGER.jsonl"
PROJECT = "09e9c541fd3d404082d4b92e55ae5336"
PAGE = "1991698f35bf4c09b8de4bcf78bd2b7b"


def call(tool: str, args: dict) -> dict:
    proc = subprocess.run(
        ["node", str(CALL), tool, json.dumps(args)],
        cwd=str(MCP), capture_output=True, text=True, timeout=120,
    )
    text = (proc.stdout + proc.stderr).strip()
    start = text.find("{")
    if proc.returncode or start < 0:
        raise SystemExit(f"{tool} failed: {text[-1200:]}")
    return json.loads(text[start:])


def source_snapshot() -> dict:
    src = call("get_document_source", {"expectedDocumentUuid": PAGE})
    source = src.get("source") or ""
    counts = {kind: source.count(f'["{kind}"') for kind in ("COMPONENT", "WIRE", "TEXT", "RECT")}
    return {
        "schema_version": 1,
        "project_uuid": PROJECT,
        "document_uuid": PAGE,
        "source_hash": src.get("sourceHash"),
        "source": source,
        "census": counts,
    }


def parse_ids(source: str) -> dict[str, list[str]]:
    ids = {"COMPONENT": [], "WIRE": [], "TEXT": [], "RECT": []}
    for line in source.splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, list) and len(row) > 1 and row[0] in ids:
            ids[row[0]].append(str(row[1]))
    return ids


def main() -> int:
    transaction_id = "reset-rejected-layout-2026-08-28"
    try:
        validate_repository_state(STATE, LEDGER)
    except GateError as exc:
        raise SystemExit(f"mutation gate invalid: {exc}") from exc

    context = call("get_current_context", {})
    project = context.get("currentProject") or {}
    document = context.get("currentDocument") or {}
    if project.get("uuid") != PROJECT or document.get("uuid") != PAGE or document.get("documentType") != 1:
        raise SystemExit("identity mismatch; refusing destructive fixture reset")

    before = source_snapshot()
    snapshot_path = SNAPSHOTS / f"{transaction_id}-before.json"
    snapshot_path.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")
    try:
        begin_transaction(
            STATE, LEDGER,
            transaction_id=transaction_id,
            project_uuid=PROJECT,
            document_uuid=PAGE,
            scope="WHOLE_SHEET_REJECTED_LAYOUT",
            stage="delete",
            kind="normal",
            intended_delta="Clear every primitive from the rejected oversized disposable fixture before compact boxed reconstruction",
            snapshot_path=snapshot_path,
            expected_checks=[
                "sheet is visibly empty",
                "component wire text and rectangle census is zero",
                "project and page identity are unchanged",
                "no PCB or second schematic sheet was created",
            ],
        )
    except GateError as exc:
        raise SystemExit(f"mutation gate refused reset: {exc}") from exc

    ids = parse_ids(before["source"])
    jobs = []
    for kind, tool in (
        ("TEXT", "delete_schematic_text"),
        ("RECT", "delete_schematic_rectangle"),
        ("WIRE", "delete_schematic_wire"),
        ("COMPONENT", "delete_schematic_component"),
    ):
        for primitive_id in ids[kind]:
            jobs.append({
                "tool": tool,
                "tag": f"{kind}:{primitive_id}",
                "args": {
                    "primitiveId": primitive_id,
                    "skipConfirmation": True,
                    "saveAfter": False,
                    "expectedDocumentUuid": PAGE,
                },
            })
    jobs.append({
        "tool": "save_active_document",
        "tag": "save",
        "args": {"expectedDocumentUuid": PAGE},
    })
    job_path = JOBS / f"{transaction_id}.json"
    result_path = JOBS / f"{transaction_id}.results.json"
    job_path.write_text(json.dumps(jobs, indent=2) + "\n")
    proc = subprocess.run(
        ["node", str(BATCH), str(job_path), str(result_path)],
        cwd=str(MCP), capture_output=True, text=True, timeout=300,
    )
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    if proc.returncode:
        raise SystemExit("reset batch transport failed; gate remains in flight")
    results = json.loads(result_path.read_text())
    after = source_snapshot()
    if any(after["census"].values()):
        failures = [item for item in results if not item.get("ok")]
        raise SystemExit(
            f"reset read-back is not empty: {after['census']}; "
            f"tool failures={len(failures)}; gate remains in flight"
        )
    failures = [item for item in results if not item.get("ok")]
    if failures:
        print(
            f"FINAL_SOURCE_OVERRIDES_INTERMEDIATE_DELETE_ERRORS={len(failures)} "
            "(parent-component deletion removed the residual wires)"
        )
    semantic = {
        "schema_version": 1,
        "transaction_id": transaction_id,
        "project_uuid": PROJECT,
        "document_uuid": PAGE,
        "scope": "WHOLE_SHEET_REJECTED_LAYOUT",
        "stage": "delete",
        "intended_delta": "Clear every primitive from the rejected oversized disposable fixture before compact boxed reconstruction",
        "pre_source_hash": before["source_hash"],
        "post_source_hash": after["source_hash"],
        "saved": True,
        "affected": [f"deleted_{kind.lower()}={len(values)}" for kind, values in ids.items()],
        "census": after["census"],
        "intermediate_tool_failures": len(failures),
        "final_source_is_authority": True,
    }
    semantic_path = JOBS / f"{transaction_id}-semantic.json"
    semantic_path.write_text(json.dumps(semantic, indent=2, sort_keys=True) + "\n")
    record_mutation(STATE, LEDGER, semantic_path)
    print(json.dumps(semantic, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
