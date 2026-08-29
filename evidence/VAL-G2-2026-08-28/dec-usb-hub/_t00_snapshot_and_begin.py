#!/usr/bin/env python3
"""Refresh hub-lane hash after host DOCHEAD restamp, write T00 snapshot, begin place."""
from __future__ import annotations

import fcntl
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path("/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0")
EV = REPO / "evidence/VAL-G2-2026-08-28/dec-usb-hub"
STATE = EV / "hub-lane/MUTATION-STATE.json"
LEDGER = EV / "hub-lane/MUTATION-LEDGER.jsonl"
MCP = Path("/Users/spectrasynq/SpectraSynq-EDA/EasyEDA-MCP/tools/mcp_http_call.mjs")
PAGE = "1435cb46f39e48c8a8aadbb84ca81603"
PROJECT = "41c8e6523576456582ea35958b3684ed"
TX = "T00-j1-gt-usb-7005a-place-2026-08-29"


def mcp(tool: str, args: dict) -> dict:
    r = subprocess.run(
        ["node", str(MCP), tool, json.dumps(args)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(r.stdout)


src = mcp("get_document_source", {"expectedDocumentUuid": PAGE})
assert src["documentUuid"] == PAGE
ctx = mcp("get_current_context", {})
assert ctx["currentProject"]["uuid"] == PROJECT
assert ctx["currentDocument"]["uuid"] == PAGE
assert ctx["currentDocument"]["parentProjectUuid"] == PROJECT

snapshot = {
    "schema_version": 1,
    "project_uuid": PROJECT,
    "document_uuid": PAGE,
    "source": src["source"],
    "source_hash": src["sourceHash"],
    "census": {"characters": src["characters"]},
    "note": "Pre-T00 snapshot. Library construction did not write this sheet. Host restamped DOCHEAD after symbol-editor return.",
}
snap_path = EV / "anchors/pre-T00.json"
snap_path.write_text(json.dumps(snapshot))

lock_path = STATE.with_suffix(STATE.suffix + ".lock")
with lock_path.open("a+") as lock_fh:
    fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)
    state = json.loads(STATE.read_text())
    old = state.get("current_source_hash")
    if old != src["sourceHash"]:
        state["current_source_hash"] = src["sourceHash"]
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        STATE.write_text(json.dumps(state, indent=2) + "\n")
        with LEDGER.open("a") as fh:
            fh.write(
                json.dumps(
                    {
                        "event": "STATE_HASH_REFRESH",
                        "reason": "Host restamped schematic DOCHEAD after independent J1 library-editor session. Electrical graph unchanged. Hash updated so T00 can begin against live source.",
                        "previous_source_hash": old,
                        "source_hash": src["sourceHash"],
                        "project_uuid": PROJECT,
                        "document_uuid": PAGE,
                        "at": state["updated_at"],
                    }
                )
                + "\n"
            )

print(json.dumps({"snapshot": str(snap_path), "source_hash": src["sourceHash"], "refreshed_from": old}, indent=2))
