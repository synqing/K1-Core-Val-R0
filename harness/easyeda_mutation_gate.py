#!/usr/bin/env python3
"""Fail-closed EasyEDA mutation state machine.

The gate binds one source snapshot, one bounded write, one semantic read-back and one
settled screenshot/inspection record. Normal writes are refused until the preceding
transaction is completely closed.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import struct
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE = REPO / "evidence" / "VAL-G2-2026-08-28"
DEFAULT_STATE = DEFAULT_EVIDENCE / "EASYEDA-MUTATION-STATE.json"
DEFAULT_LEDGER = DEFAULT_EVIDENCE / "EASYEDA-MUTATION-LEDGER.jsonl"

SCHEMA_VERSION = 1
STATES = {
    "FROZEN_INCIDENT",
    "BLOCKED_RECONCILIATION",
    "READY",
    "IN_FLIGHT",
    "AWAITING_EVIDENCE",
    "REJECTED",
}
MUTATION_STAGES = {"place", "designate", "wire", "repair", "delete", "move", "rotate", "text", "pcb"}
KINDS = {"normal", "repair"}
VISUAL_SCALES = {"block", "whole_sheet", "both"}
VISUAL_RESULTS = {"OK", "DEFECT"}
VERDICTS = {"ACCEPTED", "REJECTED"}


class GateError(RuntimeError):
    """Raised when a mutation/evidence transition is unsafe or incomplete."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def _state_lock(state_path: Path):
    """Serialise every state transition across independent agent processes."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = state_path.with_name(f"{state_path.name}.lock")
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def _append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"schema_version": SCHEMA_VERSION, "recorded_at": _now(), **event}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise GateError(f"{label} is missing: {path}")
    if path.stat().st_size == 0:
        raise GateError(f"{label} is empty: {path}")
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise GateError(f"{label} is not valid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise GateError(f"{label} must contain a JSON object: {path}")
    return value


def _load_state(path: Path) -> dict[str, Any]:
    state = _load_json(path, "state file")
    if state.get("schema_version") != SCHEMA_VERSION:
        raise GateError(f"state schema_version must be {SCHEMA_VERSION}")
    if state.get("state") not in STATES:
        raise GateError(f"state has unknown value: {state.get('state')!r}")
    return state


def _require_nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GateError(f"{label} must be a non-empty string")
    return value.strip()


def _require_identity(
    record: dict[str, Any], project_uuid: str, document_uuid: str, label: str
) -> None:
    if record.get("project_uuid") != project_uuid:
        raise GateError(
            f"{label} project_uuid mismatch: expected {project_uuid}, found {record.get('project_uuid')}"
        )
    if record.get("document_uuid") != document_uuid:
        raise GateError(
            f"{label} document_uuid mismatch: expected {document_uuid}, found {record.get('document_uuid')}"
        )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_png(path: Path) -> tuple[int, int]:
    if not path.is_file():
        raise GateError(f"screenshot is missing: {path}")
    if path.stat().st_size == 0:
        raise GateError(f"screenshot is empty: {path}")
    header = path.read_bytes()[:24]
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise GateError(f"screenshot is not a PNG with an IHDR record: {path}")
    width, height = struct.unpack(">II", header[16:24])
    if width < 640 or height < 360:
        raise GateError(f"screenshot is too small for granular inspection: {width}x{height}")
    return width, height


def _validate_visual_evidence(
    path: Path,
    *,
    transaction_id: str,
    project_uuid: str,
    document_uuid: str,
    intended_delta: str,
) -> tuple[dict[str, Any], Path, tuple[int, int]]:
    evidence = _load_json(path, "visual evidence")
    if evidence.get("schema_version") != SCHEMA_VERSION:
        raise GateError(f"visual evidence schema_version must be {SCHEMA_VERSION}")
    if evidence.get("transaction_id") != transaction_id:
        raise GateError(
            f"visual evidence transaction_id mismatch: expected {transaction_id}, "
            f"found {evidence.get('transaction_id')}"
        )
    _require_identity(evidence, project_uuid, document_uuid, "visual evidence")
    if evidence.get("captured_after_settle") is not True:
        raise GateError("visual evidence must declare captured_after_settle=true")
    if evidence.get("scale") not in VISUAL_SCALES:
        raise GateError(f"visual evidence scale must be one of {sorted(VISUAL_SCALES)}")
    if evidence.get("intended_delta") != intended_delta:
        raise GateError("visual evidence intended_delta does not match the declared transaction")
    _require_nonempty(evidence.get("observed_delta"), "visual evidence observed_delta")
    screenshot_value = _require_nonempty(evidence.get("screenshot_path"), "visual evidence screenshot_path")
    screenshot = Path(screenshot_value).expanduser()
    if not screenshot.is_absolute():
        screenshot = (REPO / screenshot).resolve()
    dimensions = _validate_png(screenshot)

    unexpected = evidence.get("unexpected_changes")
    if not isinstance(unexpected, list):
        raise GateError("visual evidence unexpected_changes must be a list")
    checks = evidence.get("checks")
    if not isinstance(checks, list) or len(checks) < 4:
        raise GateError("visual evidence requires at least four granular checks")
    seen_names: set[str] = set()
    check_results: list[str] = []
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            raise GateError(f"visual evidence checks[{index}] must be an object")
        name = _require_nonempty(check.get("name"), f"visual evidence checks[{index}].name")
        if name in seen_names:
            raise GateError(f"visual evidence contains duplicate check name: {name}")
        seen_names.add(name)
        result = check.get("result")
        if result not in VISUAL_RESULTS:
            raise GateError(
                f"visual evidence checks[{index}].result must be one of {sorted(VISUAL_RESULTS)}"
            )
        _require_nonempty(check.get("detail"), f"visual evidence checks[{index}].detail")
        check_results.append(result)

    verdict = evidence.get("verdict")
    if verdict not in VERDICTS:
        raise GateError(f"visual evidence verdict must be one of {sorted(VERDICTS)}")
    if verdict == "ACCEPTED":
        if unexpected:
            raise GateError("accepted visual evidence may not contain unexpected changes")
        if any(result != "OK" for result in check_results):
            raise GateError("accepted visual evidence requires every granular check to be OK")
    else:
        if not unexpected and all(result == "OK" for result in check_results):
            raise GateError("rejected visual evidence must identify a defect or unexpected change")
    return evidence, screenshot, dimensions


def block_state(
    state_path: Path,
    ledger_path: Path,
    project_uuid: str,
    document_uuid: str,
    reason: str,
) -> dict[str, Any]:
    with _state_lock(state_path):
        return _block_state_unlocked(
            state_path, ledger_path, project_uuid, document_uuid, reason
        )


def _block_state_unlocked(
    state_path: Path,
    ledger_path: Path,
    project_uuid: str,
    document_uuid: str,
    reason: str,
) -> dict[str, Any]:
    project_uuid = _require_nonempty(project_uuid, "project_uuid")
    document_uuid = _require_nonempty(document_uuid, "document_uuid")
    reason = _require_nonempty(reason, "blocking reason")
    if state_path.exists():
        raise GateError(f"state file already exists; refusing to overwrite it: {state_path}")
    state = {
        "schema_version": SCHEMA_VERSION,
        "state": "BLOCKED_RECONCILIATION",
        "project_uuid": project_uuid,
        "document_uuid": document_uuid,
        "current_source_hash": None,
        "active_transaction": None,
        "blocked_transaction_id": None,
        "blocking_reason": reason,
        "updated_at": _now(),
    }
    _atomic_write_json(state_path, state)
    _append_event(
        ledger_path,
        {
            "event": "STATE_BLOCKED_FOR_RECONCILIATION",
            "project_uuid": project_uuid,
            "document_uuid": document_uuid,
            "reason": reason,
        },
    )
    return state


def quarantine_state(state_path: Path, ledger_path: Path, reason: str) -> dict[str, Any]:
    """Close an existing gate after corruption, conflict or unowned concurrent activity."""
    with _state_lock(state_path):
        state = _load_state(state_path)
        reason = _require_nonempty(reason, "quarantine reason")
        prior_state = state["state"]
        state.update(
            {
                "state": "BLOCKED_RECONCILIATION",
                "current_source_hash": None,
                "active_transaction": None,
                "blocked_transaction_id": None,
                "blocking_reason": reason,
                "updated_at": _now(),
            }
        )
        _atomic_write_json(state_path, state)
        _append_event(
            ledger_path,
            {
                "event": "STATE_QUARANTINED",
                "project_uuid": state["project_uuid"],
                "document_uuid": state["document_uuid"],
                "prior_state": prior_state,
                "reason": reason,
            },
        )
        return state


def freeze_incident(state_path: Path, ledger_path: Path, reason: str) -> dict[str, Any]:
    """Stop all automatic actuation; no gate command releases an incident freeze."""
    with _state_lock(state_path):
        state = _load_state(state_path)
        reason = _require_nonempty(reason, "incident freeze reason")
        prior_state = state["state"]
        state.update(
            {
                "state": "FROZEN_INCIDENT",
                "current_source_hash": None,
                "active_transaction": None,
                "blocked_transaction_id": None,
                "blocking_reason": reason,
                "updated_at": _now(),
            }
        )
        _atomic_write_json(state_path, state)
        _append_event(
            ledger_path,
            {
                "event": "STATE_FROZEN",
                "project_uuid": state["project_uuid"],
                "document_uuid": state["document_uuid"],
                "prior_state": prior_state,
                "reason": reason,
            },
        )
        return state


def reconcile_state(
    state_path: Path,
    ledger_path: Path,
    semantic_path: Path,
    visual_path: Path,
) -> dict[str, Any]:
    with _state_lock(state_path):
        return _reconcile_state_unlocked(state_path, ledger_path, semantic_path, visual_path)


def _reconcile_state_unlocked(
    state_path: Path,
    ledger_path: Path,
    semantic_path: Path,
    visual_path: Path,
) -> dict[str, Any]:
    state = _load_state(state_path)
    if state["state"] != "BLOCKED_RECONCILIATION":
        raise GateError(f"reconciliation requires BLOCKED_RECONCILIATION, found {state['state']}")
    semantic = _load_json(semantic_path, "reconciliation semantic read-back")
    if semantic.get("schema_version") != SCHEMA_VERSION:
        raise GateError(f"reconciliation semantic schema_version must be {SCHEMA_VERSION}")
    transaction_id = _require_nonempty(semantic.get("transaction_id"), "reconciliation transaction_id")
    _require_identity(semantic, state["project_uuid"], state["document_uuid"], "reconciliation semantic")
    source_hash = _require_nonempty(semantic.get("source_hash"), "reconciliation source_hash")
    census = semantic.get("census")
    if not isinstance(census, dict) or not census:
        raise GateError("reconciliation semantic census must be a non-empty object")
    visual_raw = _load_json(visual_path, "visual evidence")
    intended = _require_nonempty(visual_raw.get("intended_delta"), "visual evidence intended_delta")
    if "reconcil" not in intended.lower():
        raise GateError("reconciliation visual evidence must explicitly describe reconciliation")
    visual, screenshot, dimensions = _validate_visual_evidence(
        visual_path,
        transaction_id=transaction_id,
        project_uuid=state["project_uuid"],
        document_uuid=state["document_uuid"],
        intended_delta=intended,
    )
    if visual["verdict"] != "ACCEPTED":
        raise GateError("reconciliation cannot open the write lock with rejected visual evidence")
    state.update(
        {
            "state": "READY",
            "current_source_hash": source_hash,
            "active_transaction": None,
            "blocked_transaction_id": None,
            "blocking_reason": None,
            "last_closed_transaction_id": transaction_id,
            "updated_at": _now(),
        }
    )
    _atomic_write_json(state_path, state)
    _append_event(
        ledger_path,
        {
            "event": "STATE_RECONCILED",
            "transaction_id": transaction_id,
            "project_uuid": state["project_uuid"],
            "document_uuid": state["document_uuid"],
            "source_hash": source_hash,
            "semantic_path": str(semantic_path),
            "semantic_sha256": _sha256(semantic_path),
            "visual_path": str(visual_path),
            "visual_sha256": _sha256(visual_path),
            "screenshot_path": str(screenshot),
            "screenshot_sha256": _sha256(screenshot),
            "screenshot_dimensions": list(dimensions),
        },
    )
    return state


def assert_ready(state_path: Path, project_uuid: str, document_uuid: str) -> dict[str, Any]:
    with _state_lock(state_path):
        state = _load_state(state_path)
        _require_identity(state, project_uuid, document_uuid, "state")
        if state["state"] != "READY":
            raise GateError(f"write lock is {state['state']}; no normal EasyEDA mutation is allowed")
        return state


def begin_transaction(
    state_path: Path,
    ledger_path: Path,
    *,
    transaction_id: str,
    project_uuid: str,
    document_uuid: str,
    scope: str,
    stage: str,
    kind: str,
    intended_delta: str,
    snapshot_path: Path,
    expected_checks: list[str],
    repairs_transaction_id: str | None = None,
) -> dict[str, Any]:
    with _state_lock(state_path):
        return _begin_transaction_unlocked(
            state_path,
            ledger_path,
            transaction_id=transaction_id,
            project_uuid=project_uuid,
            document_uuid=document_uuid,
            scope=scope,
            stage=stage,
            kind=kind,
            intended_delta=intended_delta,
            snapshot_path=snapshot_path,
            expected_checks=expected_checks,
            repairs_transaction_id=repairs_transaction_id,
        )


def _begin_transaction_unlocked(
    state_path: Path,
    ledger_path: Path,
    *,
    transaction_id: str,
    project_uuid: str,
    document_uuid: str,
    scope: str,
    stage: str,
    kind: str,
    intended_delta: str,
    snapshot_path: Path,
    expected_checks: list[str],
    repairs_transaction_id: str | None = None,
) -> dict[str, Any]:
    state = _load_state(state_path)
    _require_identity(state, project_uuid, document_uuid, "state")
    transaction_id = _require_nonempty(transaction_id, "transaction_id")
    scope = _require_nonempty(scope, "scope")
    intended_delta = _require_nonempty(intended_delta, "intended_delta")
    if stage == "all" or stage not in MUTATION_STAGES:
        raise GateError(f"stage must be one visual mutation stage, found {stage!r}")
    if kind not in KINDS:
        raise GateError(f"kind must be one of {sorted(KINDS)}")
    if not isinstance(expected_checks, list) or len(expected_checks) < 4:
        raise GateError("expected_checks must name at least four granular inspections")
    if any(not isinstance(value, str) or not value.strip() for value in expected_checks):
        raise GateError("every expected check must be a non-empty string")
    if len(set(expected_checks)) != len(expected_checks):
        raise GateError("expected_checks must not contain duplicates")

    previous_state = state["state"]
    if previous_state == "REJECTED":
        if kind != "repair":
            raise GateError("write lock is REJECTED; only a repair transaction is allowed")
        if repairs_transaction_id != state.get("blocked_transaction_id"):
            raise GateError(
                "repair must name the rejected transaction: "
                f"{state.get('blocked_transaction_id')}"
            )
    elif previous_state == "READY":
        if kind != "normal":
            raise GateError("repair transactions require a rejected transaction")
        if repairs_transaction_id is not None:
            raise GateError("normal transaction may not declare repairs_transaction_id")
    else:
        raise GateError(f"write lock is {previous_state}; a second begin is refused")

    snapshot = _load_json(snapshot_path, "snapshot")
    if snapshot.get("schema_version") != SCHEMA_VERSION:
        raise GateError(f"snapshot schema_version must be {SCHEMA_VERSION}")
    _require_identity(snapshot, project_uuid, document_uuid, "snapshot")
    pre_hash = _require_nonempty(snapshot.get("source_hash"), "snapshot source_hash")
    _require_nonempty(snapshot.get("source"), "snapshot source")
    current_hash = state.get("current_source_hash")
    if current_hash and pre_hash != current_hash:
        raise GateError(
            f"snapshot is stale: state source hash is {current_hash}, snapshot is {pre_hash}"
        )

    active = {
        "transaction_id": transaction_id,
        "kind": kind,
        "scope": scope,
        "stage": stage,
        "intended_delta": intended_delta,
        "expected_checks": expected_checks,
        "snapshot_path": str(snapshot_path),
        "snapshot_sha256": _sha256(snapshot_path),
        "pre_source_hash": pre_hash,
        "repairs_transaction_id": repairs_transaction_id,
        "previous_state": previous_state,
        "began_at": _now(),
    }
    state.update(
        {
            "state": "IN_FLIGHT",
            "active_transaction": active,
            "blocking_reason": "Mutation began; semantic and visual evidence are required",
            "updated_at": _now(),
        }
    )
    _atomic_write_json(state_path, state)
    _append_event(
        ledger_path,
        {
            "event": "MUTATION_BEGAN",
            "project_uuid": project_uuid,
            "document_uuid": document_uuid,
            **active,
        },
    )
    return state


def record_mutation(
    state_path: Path,
    ledger_path: Path,
    semantic_path: Path,
) -> dict[str, Any]:
    with _state_lock(state_path):
        return _record_mutation_unlocked(state_path, ledger_path, semantic_path)


def _record_mutation_unlocked(
    state_path: Path,
    ledger_path: Path,
    semantic_path: Path,
) -> dict[str, Any]:
    state = _load_state(state_path)
    if state["state"] != "IN_FLIGHT":
        raise GateError(f"record_mutation requires IN_FLIGHT, found {state['state']}")
    active = state.get("active_transaction")
    if not isinstance(active, dict):
        raise GateError("IN_FLIGHT state has no active_transaction")
    semantic = _load_json(semantic_path, "semantic read-back")
    if semantic.get("schema_version") != SCHEMA_VERSION:
        raise GateError(f"semantic read-back schema_version must be {SCHEMA_VERSION}")
    if semantic.get("transaction_id") != active["transaction_id"]:
        raise GateError(
            "semantic read-back transaction_id mismatch: "
            f"expected {active['transaction_id']}, found {semantic.get('transaction_id')}"
        )
    _require_identity(semantic, state["project_uuid"], state["document_uuid"], "semantic read-back")
    if semantic.get("pre_source_hash") != active["pre_source_hash"]:
        raise GateError("semantic read-back pre_source_hash does not match the transaction snapshot")
    post_hash = _require_nonempty(semantic.get("post_source_hash"), "semantic post_source_hash")
    if post_hash == active["pre_source_hash"]:
        raise GateError("source hash did not change after the claimed mutation")
    if semantic.get("saved") is not True:
        raise GateError("semantic read-back must prove saved=true")
    affected = semantic.get("affected")
    if not isinstance(affected, list) or not affected:
        raise GateError("semantic read-back affected must be a non-empty list")
    census = semantic.get("census")
    if not isinstance(census, dict) or not census:
        raise GateError("semantic read-back census must be a non-empty object")

    active.update(
        {
            "semantic_path": str(semantic_path),
            "semantic_sha256": _sha256(semantic_path),
            "post_source_hash": post_hash,
            "mutation_recorded_at": _now(),
        }
    )
    state.update(
        {
            "state": "AWAITING_EVIDENCE",
            "current_source_hash": post_hash,
            "active_transaction": active,
            "blocking_reason": "Mutation exists; settled screenshot and visual inspection are required",
            "updated_at": _now(),
        }
    )
    _atomic_write_json(state_path, state)
    _append_event(
        ledger_path,
        {
            "event": "MUTATION_RECORDED",
            "transaction_id": active["transaction_id"],
            "project_uuid": state["project_uuid"],
            "document_uuid": state["document_uuid"],
            "semantic_path": str(semantic_path),
            "semantic_sha256": active["semantic_sha256"],
            "pre_source_hash": active["pre_source_hash"],
            "post_source_hash": post_hash,
        },
    )
    return state


def close_transaction(
    state_path: Path,
    ledger_path: Path,
    visual_path: Path,
) -> dict[str, Any]:
    with _state_lock(state_path):
        return _close_transaction_unlocked(state_path, ledger_path, visual_path)


def _close_transaction_unlocked(
    state_path: Path,
    ledger_path: Path,
    visual_path: Path,
) -> dict[str, Any]:
    state = _load_state(state_path)
    if state["state"] != "AWAITING_EVIDENCE":
        raise GateError(f"close_transaction requires AWAITING_EVIDENCE, found {state['state']}")
    active = state.get("active_transaction")
    if not isinstance(active, dict):
        raise GateError("AWAITING_EVIDENCE state has no active_transaction")
    visual, screenshot, dimensions = _validate_visual_evidence(
        visual_path,
        transaction_id=active["transaction_id"],
        project_uuid=state["project_uuid"],
        document_uuid=state["document_uuid"],
        intended_delta=active["intended_delta"],
    )
    verdict = visual["verdict"]
    closed_id = active["transaction_id"]
    if verdict == "ACCEPTED":
        state.update(
            {
                "state": "READY",
                "active_transaction": None,
                "blocked_transaction_id": None,
                "blocking_reason": None,
                "last_closed_transaction_id": closed_id,
                "updated_at": _now(),
            }
        )
    else:
        state.update(
            {
                "state": "REJECTED",
                "active_transaction": None,
                "blocked_transaction_id": closed_id,
                "blocking_reason": "Visual or semantic evidence rejected the mutation; repair only",
                "last_closed_transaction_id": closed_id,
                "updated_at": _now(),
            }
        )
    _atomic_write_json(state_path, state)
    _append_event(
        ledger_path,
        {
            "event": "MUTATION_INSPECTED",
            "transaction_id": closed_id,
            "project_uuid": state["project_uuid"],
            "document_uuid": state["document_uuid"],
            "verdict": verdict,
            "visual_path": str(visual_path),
            "visual_sha256": _sha256(visual_path),
            "screenshot_path": str(screenshot),
            "screenshot_sha256": _sha256(screenshot),
            "screenshot_dimensions": list(dimensions),
        },
    )
    return state


def abort_unchanged(
    state_path: Path,
    ledger_path: Path,
    transaction_id: str,
    post_source_hash: str,
) -> dict[str, Any]:
    with _state_lock(state_path):
        return _abort_unchanged_unlocked(
            state_path, ledger_path, transaction_id, post_source_hash
        )


def _abort_unchanged_unlocked(
    state_path: Path,
    ledger_path: Path,
    transaction_id: str,
    post_source_hash: str,
) -> dict[str, Any]:
    state = _load_state(state_path)
    if state["state"] != "IN_FLIGHT":
        raise GateError(f"abort_unchanged requires IN_FLIGHT, found {state['state']}")
    active = state.get("active_transaction")
    if not isinstance(active, dict) or active.get("transaction_id") != transaction_id:
        raise GateError("abort transaction_id does not match the active transaction")
    if post_source_hash != active["pre_source_hash"]:
        raise GateError("cannot abort: source changed; record and inspect the partial mutation")
    previous_state = active["previous_state"]
    blocked_id = active.get("repairs_transaction_id") if previous_state == "REJECTED" else None
    state.update(
        {
            "state": previous_state,
            "active_transaction": None,
            "blocked_transaction_id": blocked_id,
            "blocking_reason": (
                "Prior rejected mutation still requires repair" if previous_state == "REJECTED" else None
            ),
            "updated_at": _now(),
        }
    )
    _atomic_write_json(state_path, state)
    _append_event(
        ledger_path,
        {
            "event": "MUTATION_ABORTED_NO_CHANGE",
            "transaction_id": transaction_id,
            "project_uuid": state["project_uuid"],
            "document_uuid": state["document_uuid"],
            "source_hash": post_source_hash,
            "resulting_state": previous_state,
        },
    )
    return state


def validate_repository_state(state_path: Path, ledger_path: Path) -> dict[str, Any]:
    """Validate current state, evidence references and the terminal ledger event."""
    with _state_lock(state_path):
        state = _load_state(state_path)
        _require_nonempty(state.get("project_uuid"), "state project_uuid")
        _require_nonempty(state.get("document_uuid"), "state document_uuid")

        if not ledger_path.is_file() or ledger_path.stat().st_size == 0:
            raise GateError(f"mutation ledger is missing or empty: {ledger_path}")
        records: list[dict[str, Any]] = []
        for line_number, line in enumerate(ledger_path.read_text().splitlines(), 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise GateError(f"mutation ledger line {line_number} is invalid JSON: {exc}") from exc
            if not isinstance(record, dict):
                raise GateError(f"mutation ledger line {line_number} is not an object")
            records.append(record)
        if not records:
            raise GateError("mutation ledger contains zero records")

        boundary_events = {
            "STATE_BLOCKED_FOR_RECONCILIATION",
            "STATE_QUARANTINED",
            "STATE_FROZEN",
        }
        boundary_indices = [
            index for index, record in enumerate(records) if record.get("event") in boundary_events
        ]
        if not boundary_indices:
            raise GateError("mutation ledger has no blocked/quarantined trust boundary")
        replay_records = records[boundary_indices[-1] :]
        replay_state = (
            "FROZEN_INCIDENT"
            if replay_records[0].get("event") == "STATE_FROZEN"
            else "BLOCKED_RECONCILIATION"
        )
        replay_hash: str | None = None
        replay_transaction: str | None = None
        for offset, record in enumerate(replay_records[1:], boundary_indices[-1] + 2):
            event = record.get("event")
            if event == "STATE_RECONCILED":
                if replay_state != "BLOCKED_RECONCILIATION":
                    raise GateError(f"ledger line {offset} reconciles from {replay_state}")
                replay_hash = _require_nonempty(record.get("source_hash"), "ledger source_hash")
                replay_state = "READY"
                replay_transaction = None
            elif event == "MUTATION_BEGAN":
                if replay_state not in {"READY", "REJECTED"}:
                    raise GateError(f"ledger line {offset} begins from {replay_state}")
                pre_hash = _require_nonempty(record.get("pre_source_hash"), "ledger pre_source_hash")
                if replay_hash and pre_hash != replay_hash:
                    raise GateError(
                        f"ledger line {offset} breaks the source-hash chain: "
                        f"expected {replay_hash}, found {pre_hash}"
                    )
                replay_transaction = _require_nonempty(
                    record.get("transaction_id"), "ledger transaction_id"
                )
                replay_state = "IN_FLIGHT"
            elif event == "MUTATION_RECORDED":
                if replay_state != "IN_FLIGHT":
                    raise GateError(f"ledger line {offset} records from {replay_state}")
                if record.get("transaction_id") != replay_transaction:
                    raise GateError(f"ledger line {offset} changes transaction identity")
                pre_hash = _require_nonempty(record.get("pre_source_hash"), "ledger pre_source_hash")
                if replay_hash and pre_hash != replay_hash:
                    raise GateError(f"ledger line {offset} semantic pre-hash breaks the chain")
                post_hash = _require_nonempty(
                    record.get("post_source_hash"), "ledger post_source_hash"
                )
                if post_hash == pre_hash:
                    raise GateError(f"ledger line {offset} records an unchanged mutation")
                replay_hash = post_hash
                replay_state = "AWAITING_EVIDENCE"
            elif event == "MUTATION_INSPECTED":
                if replay_state != "AWAITING_EVIDENCE":
                    raise GateError(f"ledger line {offset} inspects from {replay_state}")
                if record.get("transaction_id") != replay_transaction:
                    raise GateError(f"ledger line {offset} changes transaction identity")
                verdict = record.get("verdict")
                if verdict not in VERDICTS:
                    raise GateError(f"ledger line {offset} has invalid visual verdict")
                replay_state = "READY" if verdict == "ACCEPTED" else "REJECTED"
                replay_transaction = None
            elif event == "MUTATION_ABORTED_NO_CHANGE":
                if replay_state != "IN_FLIGHT":
                    raise GateError(f"ledger line {offset} aborts from {replay_state}")
                if record.get("transaction_id") != replay_transaction:
                    raise GateError(f"ledger line {offset} changes transaction identity")
                if record.get("source_hash") != replay_hash:
                    raise GateError(f"ledger line {offset} abort hash breaks the chain")
                replay_state = record.get("resulting_state", "READY")
                if replay_state not in {"READY", "REJECTED"}:
                    raise GateError(f"ledger line {offset} has invalid abort resulting_state")
                replay_transaction = None
            else:
                raise GateError(f"ledger line {offset} has unknown event {event!r}")

        if replay_state != state["state"]:
            raise GateError(
                f"replayed ledger state {replay_state} conflicts with state file {state['state']}"
            )
        if replay_hash != state.get("current_source_hash"):
            raise GateError(
                f"replayed source hash {replay_hash!r} conflicts with state file "
                f"{state.get('current_source_hash')!r}"
            )

        expected_terminal_events = {
            "FROZEN_INCIDENT": {"STATE_FROZEN"},
            "BLOCKED_RECONCILIATION": {
                "STATE_BLOCKED_FOR_RECONCILIATION",
                "STATE_QUARANTINED",
            },
            "READY": {"STATE_RECONCILED", "MUTATION_INSPECTED", "MUTATION_ABORTED_NO_CHANGE"},
            "IN_FLIGHT": {"MUTATION_BEGAN"},
            "AWAITING_EVIDENCE": {"MUTATION_RECORDED"},
            "REJECTED": {"MUTATION_INSPECTED"},
        }
        last = records[-1]
        if last.get("event") not in expected_terminal_events[state["state"]]:
            raise GateError(
                f"state {state['state']} conflicts with terminal ledger event {last.get('event')!r}"
            )
        _require_identity(last, state["project_uuid"], state["document_uuid"], "terminal ledger event")

        active = state.get("active_transaction")
        if state["state"] in {"IN_FLIGHT", "AWAITING_EVIDENCE"}:
            if not isinstance(active, dict):
                raise GateError(f"state {state['state']} requires an active_transaction")
            if last.get("transaction_id") != active.get("transaction_id"):
                raise GateError("active transaction does not match the terminal ledger event")
            snapshot_path = Path(_require_nonempty(active.get("snapshot_path"), "snapshot_path"))
            if not snapshot_path.is_file() or _sha256(snapshot_path) != active.get("snapshot_sha256"):
                raise GateError("active transaction snapshot is missing or its digest changed")
            if state["state"] == "AWAITING_EVIDENCE":
                semantic_path = Path(
                    _require_nonempty(active.get("semantic_path"), "semantic_path")
                )
                if not semantic_path.is_file() or _sha256(semantic_path) != active.get(
                    "semantic_sha256"
                ):
                    raise GateError("active semantic read-back is missing or its digest changed")
                if state.get("current_source_hash") != active.get("post_source_hash"):
                    raise GateError("state source hash does not match the active semantic read-back")
        elif active is not None:
            raise GateError(f"state {state['state']} may not retain an active_transaction")

        if state["state"] == "REJECTED" and not state.get("blocked_transaction_id"):
            raise GateError("REJECTED state requires blocked_transaction_id")
        return {"state": state, "records_parsed": len(records), "terminal_event": last["event"]}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    subparsers = parser.add_subparsers(dest="command", required=True)

    block = subparsers.add_parser("block")
    block.add_argument("--project-uuid", required=True)
    block.add_argument("--document-uuid", required=True)
    block.add_argument("--reason", required=True)

    quarantine = subparsers.add_parser("quarantine")
    quarantine.add_argument("--reason", required=True)

    freeze = subparsers.add_parser("freeze-incident")
    freeze.add_argument("--reason", required=True)

    reconcile = subparsers.add_parser("reconcile")
    reconcile.add_argument("--semantic", type=Path, required=True)
    reconcile.add_argument("--visual", type=Path, required=True)

    ready = subparsers.add_parser("assert-ready")
    ready.add_argument("--project-uuid", required=True)
    ready.add_argument("--document-uuid", required=True)

    begin = subparsers.add_parser("begin")
    begin.add_argument("--transaction-id", required=True)
    begin.add_argument("--project-uuid", required=True)
    begin.add_argument("--document-uuid", required=True)
    begin.add_argument("--scope", required=True)
    begin.add_argument("--stage", required=True)
    begin.add_argument("--kind", choices=sorted(KINDS), default="normal")
    begin.add_argument("--intended-delta", required=True)
    begin.add_argument("--snapshot", type=Path, required=True)
    begin.add_argument("--check", action="append", dest="checks", required=True)
    begin.add_argument("--repairs-transaction-id")

    record = subparsers.add_parser("record")
    record.add_argument("--semantic", type=Path, required=True)

    close = subparsers.add_parser("close")
    close.add_argument("--visual", type=Path, required=True)

    abort = subparsers.add_parser("abort-unchanged")
    abort.add_argument("--transaction-id", required=True)
    abort.add_argument("--post-source-hash", required=True)

    subparsers.add_parser("status")
    subparsers.add_parser("validate")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        if args.command == "block":
            result = block_state(
                args.state,
                args.ledger,
                args.project_uuid,
                args.document_uuid,
                args.reason,
            )
        elif args.command == "quarantine":
            result = quarantine_state(args.state, args.ledger, args.reason)
        elif args.command == "freeze-incident":
            result = freeze_incident(args.state, args.ledger, args.reason)
        elif args.command == "reconcile":
            result = reconcile_state(args.state, args.ledger, args.semantic, args.visual)
        elif args.command == "assert-ready":
            result = assert_ready(args.state, args.project_uuid, args.document_uuid)
        elif args.command == "begin":
            result = begin_transaction(
                args.state,
                args.ledger,
                transaction_id=args.transaction_id,
                project_uuid=args.project_uuid,
                document_uuid=args.document_uuid,
                scope=args.scope,
                stage=args.stage,
                kind=args.kind,
                intended_delta=args.intended_delta,
                snapshot_path=args.snapshot,
                expected_checks=args.checks,
                repairs_transaction_id=args.repairs_transaction_id,
            )
        elif args.command == "record":
            result = record_mutation(args.state, args.ledger, args.semantic)
        elif args.command == "close":
            result = close_transaction(args.state, args.ledger, args.visual)
        elif args.command == "abort-unchanged":
            result = abort_unchanged(
                args.state,
                args.ledger,
                args.transaction_id,
                args.post_source_hash,
            )
        elif args.command == "status":
            result = _load_state(args.state)
        elif args.command == "validate":
            validation = validate_repository_state(args.state, args.ledger)
            result = validation["state"]
            print(f"EASYEDA_MUTATION_LEDGER_RECORDS={validation['records_parsed']}")
            print(f"EASYEDA_MUTATION_TERMINAL_EVENT={validation['terminal_event']}")
        else:  # pragma: no cover - argparse owns command validation
            raise GateError(f"unknown command: {args.command}")
    except GateError as exc:
        print(f"EASYEDA_MUTATION_GATE=BLOCKED\nREASON={exc}")
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"EASYEDA_MUTATION_GATE_STATE={result['state']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
