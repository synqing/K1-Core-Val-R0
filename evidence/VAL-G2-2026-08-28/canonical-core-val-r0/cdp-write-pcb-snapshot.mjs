#!/usr/bin/env node
import { readFileSync, writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const OUT = process.argv[2]
  || 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/usb1-prewrite-snapshot.json';

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const page = targets.find(t => t.type === 'page' && String(t.url).includes(PROJECT));
if (!page) throw new Error(`no CDP page for ${PROJECT}`);
const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
ws.onmessage = ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    pending.get(m.id)(m);
    pending.delete(m.id);
  }
};
await new Promise(r => { ws.onopen = r; });
const send = (method, params = {}) => new Promise(res => {
  const i = ++id;
  pending.set(i, res);
  ws.send(JSON.stringify({ id: i, method, params }));
});
await send('Runtime.enable');
const expr = readFileSync(
  'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/cdp-dump-pcb-source.js',
  'utf8',
);
const fired = await send('Runtime.evaluate', {
  expression: expr,
  returnByValue: true,
  awaitPromise: true,
});
if (fired.result?.exceptionDetails) {
  console.log(JSON.stringify({ ok: false, exception: fired.result.exceptionDetails }, null, 2));
  ws.close();
  process.exit(1);
}
const v = fired.result?.result?.value;
if (!v?.source) {
  console.log(JSON.stringify({ ok: false, value: v }, null, 2));
  ws.close();
  process.exit(1);
}
const snap = {
  schema_version: 1,
  project_uuid: PROJECT,
  document_uuid: PCB,
  source_hash: v.sourceHash,
  source: v.source,
  captured_at: new Date().toISOString(),
  doc: v.doc,
};
writeFileSync(OUT, JSON.stringify(snap));
console.log(JSON.stringify({
  ok: true,
  out: OUT,
  source_hash: v.sourceHash,
  characters: v.characters,
  projectUuid: v.projectUuid,
  docUuid: v.docUuid,
}, null, 2));
ws.close();
