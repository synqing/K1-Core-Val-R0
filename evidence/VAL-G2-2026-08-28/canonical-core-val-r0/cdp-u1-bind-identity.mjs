#!/usr/bin/env node
import { writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const ORIG = '7e3f17b4e5b64384aaa03075cd65e3e3';
const TITLE = 'J1_GT-USB-7005A';
const XF = '0, 0, 0, 0, 0, 0, 0, 0, 0';
const OUT = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-gtusb-3d-identity-bind-2026-08-30.json';

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
  const fired = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise });
  if (fired.result?.exceptionDetails) {
    return { ok: false, exception: fired.result.exceptionDetails };
  }
  return fired.result?.result?.value;
};

await send('Runtime.enable');
const result = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  const orig = ${JSON.stringify(ORIG)};
  const title = ${JSON.stringify(TITLE)};
  const XF = ${JSON.stringify(XF)};
  const TAB = '${PCB}@${PROJECT}';
  const out = {};
  try { await R.dmt_EditorControl.activateDocument(TAB); } catch (e) { out.actErr = String(e && e.message || e); }
  await new Promise(r => setTimeout(r, 400));
  const inspect = (c) => {
    if (!c) return { missing: true };
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    return {
      des: c.getState_Designator && c.getState_Designator(),
      id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      model: other['3D Model'],
      title: other['3D Model Title'],
      xf: other['3D Model Transform'],
    };
  };
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const u1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'U1');
  const u6 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'U6-RTC');
  const d1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'D1-PWR1');
  out.before = { u1: inspect(u1), u6: inspect(u6), d1: inspect(d1) };
  if (!u1 || u1.getState_SupplierId() !== 'C5250872' || u1.getState_ManufacturerId() !== 'GT-USB-7005A') {
    out.ok = false;
    out.err = 'U1 identity mismatch';
    return out;
  }
  if (out.before.u1.model !== orig) {
    out.ok = false;
    out.err = 'U1 is not on original mesh ' + orig;
    return out;
  }
  const prev = u1.getState_OtherProperty() || {};
  out.modify = await R.pcb_PrimitiveComponent.modify(u1, {
    otherProperty: {
      ...prev,
      '3D Model': orig,
      '3D Model Title': title,
      '3D Model Transform': XF,
    },
  });
  out.saved = await R.pcb_Document.save('${PCB}');
  await new Promise(r => setTimeout(r, 400));
  const again = await R.pcb_PrimitiveComponent.getAll();
  out.after = {
    u1: inspect(again.find(c => c.getState_Designator && c.getState_Designator() === 'U1')),
    u6: inspect(again.find(c => c.getState_Designator && c.getState_Designator() === 'U6-RTC')),
    d1: inspect(again.find(c => c.getState_Designator && c.getState_Designator() === 'D1-PWR1')),
  };
  const source = await R.sys_FileManager.getDocumentSource();
  const buf = new TextEncoder().encode(source);
  const digest = await crypto.subtle.digest('SHA-256', buf);
  const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
  out.sourceHash = source.length + ':' + hex.slice(0, 8);
  out.ok = out.after.u1.model === orig
    && out.after.u1.xf === XF
    && out.after.u6.model === out.before.u6.model
    && out.after.u6.xf === out.before.u6.xf
    && out.after.d1.model === out.before.d1.model
    && out.after.d1.xf === out.before.d1.xf;
  return out;
})()`);

writeFileSync(OUT, JSON.stringify({ recorded_at: new Date().toISOString(), transform: XF, result }, null, 2));
console.log(JSON.stringify({
  out: OUT,
  ok: result?.ok,
  saved: result?.saved,
  sourceHash: result?.sourceHash,
  before: result?.before,
  after: result?.after,
  err: result?.err,
}, null, 2));
ws.close();
process.exit(result?.ok ? 0 : 1);
