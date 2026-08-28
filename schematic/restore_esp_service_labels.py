#!/usr/bin/env python3
"""Restore visible endpoint net labels hidden by the ESP declutter stage."""
from __future__ import annotations

import json
import time
from pathlib import Path

from execute_canonical_container import JOBS, PAGE, PROJECT, SNAPSHOTS, load_fixture_executor
from repair_esp_service import pin_maps
from repair_power_buck import component_records
from wire_led_efuse_support import endpoint, points_for, source_rows

TX = "canonical-esp-service-label-visibility-repair-2026-08-28"
STATE = Path("evidence/VAL-G2-2026-08-28/canonical-core-val-r0/MUTATION-STATE.json")
LEDGER = Path("evidence/VAL-G2-2026-08-28/canonical-core-val-r0/MUTATION-LEDGER.jsonl")
TARGETS = ("U10-ESP", "J6-ESP", "R71-ESP", "R72-ESP", "R73-ESP", "R74-ESP")
INTENDED = "Restore visible endpoint net labels for ESP service USB support parts without changing electrical topology"

def main() -> int:
    base = load_fixture_executor(); base.assert_identity()
    previous = None
    for _ in range(12):
        snap = base.source_snapshot()
        if snap["source_hash"] == previous:
            break
        previous = snap["source_hash"]; time.sleep(1)
    else:
        raise SystemExit("source did not settle")
    before = snap
    snapshot_path = SNAPSHOTS / f"{TX}-before.json"
    snapshot_path.write_text(json.dumps(before, indent=2, sort_keys=True) + "\n")
    state = json.loads(STATE.read_text())
    if state.get("state") not in ("READY", "REJECTED"):
        raise SystemExit(f"gate not ready: {state.get('state')}")
    base.begin_transaction(STATE, LEDGER, transaction_id=TX, project_uuid=PROJECT,
        document_uuid=PAGE, scope="ESP_SERVICE_USB", stage="repair", kind="repair",
        intended_delta=INTENDED, snapshot_path=snapshot_path,
        repairs_transaction_id=(state.get("blocked_transaction_id") if state.get("state") == "REJECTED" else None),
        expected_checks=["R73/R74, R71/R72 and U10/J6 endpoint labels are visible",
                         "USB D+/D- and VBUS sense labels remain readable at box-5 scale",
                         "named-net topology and component count are unchanged",
                         "no PCB or unrelated domain changes"])
    live = component_records(before["source"])
    pins = pin_maps(base, {ref: live[ref] for ref in TARGETS}, f"{TX}-pins")
    points = {endpoint(pin) for ref in TARGETS for pin in pins[ref].values()}
    rows = source_rows(before["source"])
    wire_ids = {str(row[1]) for row in rows if row[0] == "WIRE" and
                any((int(x1), int(y1)) in points or (int(x2), int(y2)) in points for x1,y1,x2,y2 in row[2])}
    changed = 0
    for row in rows:
        if row[0] == "ATTR" and len(row) > 6 and str(row[2]) in wire_ids and row[3] == "NET" and row[6] == 0:
            row[6] = 1; changed += 1
    if changed not in (0, 20): raise SystemExit(f"expected 0 or 20 hidden labels, found {changed}")
    source = "\n".join(json.dumps(row, separators=(",", ":")) for row in rows)
    result = base.mcp_call("set_document_source", {"source": source, "expectedSourceHash": before["source_hash"], "skipConfirmation": True, "expectedDocumentUuid": PAGE}, timeout=240)
    (JOBS / f"{TX}-set-source-result.json").write_text(json.dumps(result, indent=2) + "\n")
    if result.get("bridge_message") or result.get("error"): raise SystemExit(f"source write refused: {result}")
    if base.mcp_call("save_active_document", {"expectedDocumentUuid": PAGE}).get("saved") is not True: raise SystemExit("save not confirmed")
    after = base.source_snapshot()
    if after["census"] != before["census"]: raise SystemExit("census changed")
    semantic = JOBS / f"{TX}-semantic.json"
    semantic.write_text(json.dumps({"schema_version":1,"transaction_id":TX,"project_uuid":PROJECT,"document_uuid":PAGE,"scope":"ESP_SERVICE_USB","stage":"repair","intended_delta":INTENDED,"pre_source_hash":before["source_hash"],"post_source_hash":after["source_hash"],"saved":True,"restored_labels":changed,"component_count":after["census"]["components"],"source_basis":["prior repair_esp_service.py declutter stage and live visual inspection"]}, indent=2, sort_keys=True)+"\n")
    base.record_mutation(STATE, LEDGER, semantic)
    print(f"RESTORED_LABELS={changed} POST_SOURCE_HASH={after['source_hash']} SEMANTIC={semantic}")
    return 0

if __name__ == "__main__": raise SystemExit(main())
