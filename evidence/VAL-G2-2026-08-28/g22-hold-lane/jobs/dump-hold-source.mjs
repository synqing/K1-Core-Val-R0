#!/usr/bin/env node
// Dump HOLD schematic source via CDP. MCP get_document_source is hanging after save.
import { writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const HOLD = '55ed9ee948734a0e903f37744b51f3b8';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
const outPath = process.argv[2];
if (!outPath) throw new Error('usage: dump-hold-source.mjs <snapshot.json>');

const expr = `(async () => {
  const eda = globalThis._EXTAPI_ROOT_
    || (Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda) || {}).eda;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info) return { ok:false, reason:'NO_PROJ' };
  if (info.uuid === ${JSON.stringify(LIVE)}) return { ok:false, reason:'LIVE', uuid: info.uuid };
  if (info.uuid !== ${JSON.stringify(HOLD)}) return { ok:false, reason:'WRONG', uuid: info.uuid, friendly: info.friendlyName };
  const source = await eda.sys_FileManager.getDocumentSource();
  if (typeof source !== 'string' || !source.includes('U1-PWR1')) {
    return { ok:false, reason:'BAD_SOURCE', hint: typeof source, len: typeof source==='string'?source.length:0 };
  }
  let h = 2166136261;
  for (let i = 0; i < source.length; i++) { h ^= source.charCodeAt(i); h = Math.imul(h, 16777619); }
  return {
    ok: true,
    project_uuid: info.uuid,
    friendlyName: info.friendlyName,
    document_uuid: ${JSON.stringify(PAGE)},
    sourceHash: source.length + ':' + (h >>> 0).toString(16).padStart(8, '0'),
    characters: source.length,
    source,
  };
})()`;

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const page = targets.find((t) => t.type === 'page' && String(t.url).includes(HOLD));
if (!page) throw new Error('no HOLD CDP page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) pending.get(m.id)(m);
};
await new Promise((r) => { ws.onopen = r; });
const send = (method, params) => new Promise((res) => {
  const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params }));
});
const fired = await send('Runtime.evaluate', {
  expression: expr,
  returnByValue: true,
  awaitPromise: true,
  timeout: 180000,
});
if (fired.result?.exceptionDetails) {
  console.log(JSON.stringify({ ok: false, exception: fired.result.exceptionDetails.exception?.description || fired.result.exceptionDetails.text }, null, 2));
  ws.close();
  process.exit(1);
}
const value = fired.result?.result?.value ?? fired.result;
if (!value || !value.ok || !value.source) {
  console.log(JSON.stringify(value, null, 2));
  ws.close();
  process.exit(2);
}
const payload = {
  schema_version: 1,
  project_uuid: value.project_uuid,
  document_uuid: value.document_uuid,
  source_hash: value.sourceHash,
  source: value.source,
  friendlyName: value.friendlyName,
};
writeFileSync(outPath, JSON.stringify(payload));
console.log(JSON.stringify({
  ok: true,
  path: outPath,
  sourceHash: value.sourceHash,
  characters: value.characters,
  friendlyName: value.friendlyName,
}, null, 2));
ws.close();
