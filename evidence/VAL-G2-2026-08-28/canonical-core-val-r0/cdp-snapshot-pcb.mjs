#!/usr/bin/env node
import { writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const OUT = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-gtusb-3d-bind-2026-08-30-snapshot.json';

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const page = targets.find(t => t.type === 'page' && String(t.url).includes(PROJECT));
if (!page) throw new Error(`no CDP page for ${PROJECT}`);
const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
ws.onmessage = ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) pending.get(m.id)(m);
};
await new Promise(r => { ws.onopen = r; });
const send = (method, params = {}) => new Promise(res => {
  const i = ++id;
  pending.set(i, res);
  ws.send(JSON.stringify({ id: i, method, params }));
});
await send('Runtime.enable');
const fired = await send('Runtime.evaluate', {
  expression: `(async () => {
    const R = window._EXTAPI_ROOT_;
    const doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
    if (!doc || doc.uuid !== '${PCB}') {
      try { await R.dmt_EditorControl.activateDocument('${PCB}@${PROJECT}'); } catch (e) {}
      await new Promise(r => setTimeout(r, 400));
    }
    const source = await R.sys_FileManager.getDocumentSource();
    const buf = new TextEncoder().encode(source);
    const digest = await crypto.subtle.digest('SHA-256', buf);
    const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
    return {
      schema_version: 1,
      project_uuid: '${PROJECT}',
      document_uuid: '${PCB}',
      source_hash: source.length + ':' + hex.slice(0, 8),
      source,
    };
  })()`,
  returnByValue: true,
  awaitPromise: true,
});
if (fired.result?.exceptionDetails) {
  console.error(JSON.stringify(fired.result.exceptionDetails));
  process.exit(1);
}
const snap = fired.result?.result?.value;
writeFileSync(OUT, JSON.stringify(snap));
console.log(JSON.stringify({ path: OUT, source_hash: snap.source_hash, chars: snap.source.length }));
ws.close();
