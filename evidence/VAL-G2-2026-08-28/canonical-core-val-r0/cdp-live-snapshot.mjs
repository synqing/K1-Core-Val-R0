#!/usr/bin/env node
import { writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const OUT = process.argv[2]
  || 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/usb1-reconcile-5-snapshot.json';

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
const evaluate = async (expression, awaitPromise = true) => {
  const reply = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise });
  if (reply.error || reply.result?.exceptionDetails) {
    throw new Error(JSON.stringify(reply.error || reply.result?.exceptionDetails));
  }
  return reply.result?.result?.value;
};
await send('Runtime.enable');

const live = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  const TAB = '${PCB}@${PROJECT}';
  try { await R.dmt_EditorControl.activateDocument(TAB); } catch (e) {}
  await new Promise(r => setTimeout(r, 300));
  const source = await R.sys_FileManager.getDocumentSource();
  const doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const pick = (des) => {
    const c = comps.find(x => x.getState_Designator && x.getState_Designator() === des);
    if (!c) return { des, missing: true };
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    return {
      des,
      id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      model3d: c.getState_Model3D && c.getState_Model3D(),
      transform: other['3D Model Transform'],
      model: other['3D Model'],
      title: other['3D Model Title'],
      footprint: c.getState_Footprint && c.getState_Footprint(),
    };
  };
  return { source, doc, usb1: pick('USB1'), usb2: pick('USB2'), u6: pick('U6-RTC') };
})()`);

const source = live.source;
const digest = createHash('sha256').update(source, 'utf8').digest('hex');
const source_hash = `${source.length}:${digest.slice(0, 8)}`;
const snapshot = {
  schema_version: 1,
  project_uuid: PROJECT,
  document_uuid: PCB,
  source_hash,
  source,
  captured_at: new Date().toISOString(),
  doc: live.doc,
};
writeFileSync(OUT, JSON.stringify(snapshot));
writeFileSync(OUT.replace('snapshot.json', 'census.json'), JSON.stringify({
  source_hash,
  usb1: live.usb1,
  usb2: live.usb2,
  u6: live.u6,
}, null, 2));
console.log(JSON.stringify({
  out: OUT,
  source_hash,
  usb1: live.usb1,
  usb2: { des: live.usb2.des, transform: live.usb2.transform, model: live.usb2.model },
  u6: { des: live.u6.des, transform: live.u6.transform, model: live.u6.model },
}, null, 2));
ws.close();
