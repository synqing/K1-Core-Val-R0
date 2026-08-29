#!/usr/bin/env node
import { writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const SNAP = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-seat-restamp-snapshot.json';
const PNG = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-seat-restamp.png';
const CENSUS = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-seat-restamp-census.json';

const targets = await (await fetch(CDP_BASE + '/json/list')).json();
const page = targets.find(t => t.type === 'page' && String(t.url).includes(PROJECT));
if (!page) throw new Error('no CDP page');
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
const evaluate = async (expression, awaitPromise = true) => {
  const reply = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise });
  if (reply.error || reply.result?.exceptionDetails) {
    throw new Error(JSON.stringify(reply.error || reply.result?.exceptionDetails));
  }
  return reply.result?.result?.value;
};

await send('Runtime.enable');
await send('Page.enable');

const live = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  const doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  const already = doc && doc.uuid === '${PCB}' && doc.documentType === 3;
  if (!already) {
    try { await R.dmt_EditorControl.activateDocument('${PCB}@${PROJECT}'); } catch (e) {}
    await new Promise(r => setTimeout(r, 400));
  }
  const source = await R.sys_FileManager.getDocumentSource();
  const buf = new TextEncoder().encode(source);
  const digest = await crypto.subtle.digest('SHA-256', buf);
  const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
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
      model: other['3D Model'],
      title: other['3D Model Title'],
      xf: other['3D Model Transform'],
      model3d: c.getState_Model3D && c.getState_Model3D(),
    };
  };
  return {
    already,
    doc: await R.dmt_SelectControl.getCurrentDocumentInfo(),
    source,
    sourceHash: source.length + ':' + hex.slice(0, 8),
    u1: pick('U1'),
    u6: pick('U6-RTC'),
    d1: pick('D1-PWR1'),
  };
})()`);

const snap = {
  schema_version: 1,
  project_uuid: PROJECT,
  document_uuid: PCB,
  source_hash: live.sourceHash,
  source: live.source,
  captured_at: new Date().toISOString(),
  doc: live.doc,
};
writeFileSync(SNAP, JSON.stringify(snap));
writeFileSync(CENSUS, JSON.stringify({
  source_hash: live.sourceHash,
  alreadyOnPcb: live.already,
  u1: live.u1,
  u6: live.u6,
  d1: live.d1,
}, null, 2));

const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
if (shot.error || !shot.result?.data) throw new Error('no screenshot');
const buf = Buffer.from(shot.result.data, 'base64');
writeFileSync(PNG, buf);
console.log(JSON.stringify({
  ok: true,
  source_hash: live.sourceHash,
  alreadyOnPcb: live.already,
  pngBytes: buf.length,
  u1: live.u1,
  u6: { model: live.u6.model, xf: live.u6.xf },
  d1: { model: live.d1.model, xf: live.d1.xf },
}, null, 2));
ws.close();
