#!/usr/bin/env python3
"""Quarantine, save, and prepare a hash-restamp snapshot for the canonical gate."""
from __future__ import annotations

import json
import sys

from execute_canonical_container import JOBS, PAGE, PROJECT, load_fixture_executor


TX = "codex-label-hash-reconcile-2026-08-28"


def main() -> int:
    base = load_fixture_executor()
    base.assert_identity()
    before = base.source_snapshot()
    saved = base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE})
    if saved.get("saved") is not True:
        raise SystemExit(f"save not confirmed: {saved}")
    after = base.source_snapshot()
    semantic = JOBS / f"{TX}-semantic.json"
    semantic.write_text(json.dumps({
        "schema_version": 1,
        "transaction_id": TX,
        "project_uuid": PROJECT,
        "document_uuid": PAGE,
        "source_hash": after["source_hash"],
        "saved": True,
        "census": after["census"],
        "pre_save_hash": before["source_hash"],
        "observed": (
            f"Restamp after Codex label-visibility work. Live hash was "
            f"{before['source_hash']}; gate still named 474373:a54002fa. "
            f"Census remains {after['census']['components']} components / "
            f"{after['census']['wires']} wires. save_active_document saved=true; "
            f"post-save hash {after['source_hash']}."
        ),
    }, indent=2, sort_keys=True) + "\n")
    print(f"PRE={before['source_hash']}")
    print(f"POST={after['source_hash']}")
    print(f"CENSUS={after['census']}")
    print(f"SEMANTIC={semantic}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
