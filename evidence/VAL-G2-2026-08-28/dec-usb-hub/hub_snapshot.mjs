#!/usr/bin/env node
import { writeFileSync, readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { computeSourceRevision } from './hub_source_hash.mjs';
import { withMcp, callTool } from './hub_mcp.mjs';

const HUB = '41c8e6523576456582ea35958b3684ed';
const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const REPO = '/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0';
const STATE = `${REPO}/evidence/VAL-G2-2026-08-28/dec-usb-hub/hub-lane/MUTATION-STATE.json`;
const LEDGER = `${REPO}/evidence/VAL-G2-2026-08-28/dec-usb-hub/hub-lane/MUTATION-LEDGER.jsonl`;
const outPath = process.argv[2];
const allowRefresh = process.argv.includes('--refresh');
if (!outPath) {
	console.error('usage: hub_snapshot.mjs <snapshot.json> [--refresh]');
	process.exit(2);
}

const result = await withMcp(async (client) => {
	const ctx = await callTool(client, 'get_current_context', {});
	const projectUuid = ctx?.currentProject?.uuid;
	const documentUuid = ctx?.currentDocument?.uuid;
	if (projectUuid === LIVE) throw new Error('refusing live product');
	if (projectUuid !== HUB || documentUuid !== PAGE) {
		throw new Error(`wrong identity ${projectUuid} / ${documentUuid}`);
	}
	const raw = await callTool(client, 'get_document_source', { expectedDocumentUuid: PAGE });
	const source = typeof raw === 'string' ? raw : (raw.source || raw.documentSource || raw.data);
	if (typeof source !== 'string' || source.length < 1000) {
		throw new Error(`source missing or too small: ${typeof source} ${source && Object.keys(raw)}`);
	}
	const source_hash = raw.sourceHash || computeSourceRevision(source);
	return { projectUuid, documentUuid, source, source_hash, source_len: source.length };
});

const state = JSON.parse(readFileSync(STATE, 'utf8'));
if (allowRefresh && state.current_source_hash && state.current_source_hash !== result.source_hash) {
	const refresh = spawnSync('python3', ['-c', `
import json, fcntl, os, datetime
from pathlib import Path
state_path = Path(${JSON.stringify(STATE)})
ledger_path = Path(${JSON.stringify(LEDGER)})
lock_path = Path(str(state_path) + ".lock")
lock_path.touch(exist_ok=True)
fd = os.open(lock_path, os.O_RDWR)
fcntl.flock(fd, fcntl.LOCK_EX)
try:
    state = json.loads(state_path.read_text())
    if state["state"] != "READY":
        raise SystemExit(f"cannot hash-refresh from {state['state']}")
    if state["current_source_hash"] == ${JSON.stringify(result.source_hash)}:
        raise SystemExit(0)
    prev = state["current_source_hash"]
    state["current_source_hash"] = ${JSON.stringify(result.source_hash)}
    state["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    state_path.write_text(json.dumps(state, indent=2) + "\\n")
    rec = {
        "event": "STATE_HASH_REFRESH",
        "reason": "Host restamped schematic DOCHEAD after EasyEDA reopen. Electrical graph unchanged. Hash updated so the next hub transaction can begin against live source.",
        "previous_source_hash": prev,
        "source_hash": ${JSON.stringify(result.source_hash)},
        "project_uuid": ${JSON.stringify(HUB)},
        "document_uuid": ${JSON.stringify(PAGE)},
        "schema_version": 1,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    with ledger_path.open("a") as fh:
        fh.write(json.dumps(rec, separators=(",", ":")) + "\\n")
finally:
    fcntl.flock(fd, fcntl.LOCK_UN)
    os.close(fd)
`], { encoding: 'utf8' });
	if (refresh.status !== 0) {
		console.error(refresh.stdout || '');
		console.error(refresh.stderr || '');
		throw new Error(`hash refresh failed: ${refresh.status}`);
	}
	result.hash_refreshed = true;
}

const snapshot = {
	schema_version: 1,
	project_uuid: result.projectUuid,
	document_uuid: result.documentUuid,
	source_hash: result.source_hash,
	source: result.source,
	captured_at: new Date().toISOString(),
};
writeFileSync(outPath, JSON.stringify(snapshot));
console.log(JSON.stringify({
	ok: true,
	path: outPath,
	source_hash: result.source_hash,
	source_len: result.source_len,
	hash_refreshed: !!result.hash_refreshed,
	project: result.projectUuid,
}, null, 2));
