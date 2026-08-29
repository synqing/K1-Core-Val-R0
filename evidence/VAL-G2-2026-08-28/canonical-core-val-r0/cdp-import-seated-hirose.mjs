#!/usr/bin/env node
// Create a NEW personal Hirose 3D model and bind it to USB1 only,
// using USB2's COMPONENT-attr mechanism (sizeZ auto + mid-mount OFFSET).
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const STEP_PATH = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/USB_C_Hirose_CX_4800304000_seated.STEP';
const OUT = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/usb1-seated-step-bind.json';
const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
const CLASSIF = {
  libraryUuid: PERSONAL,
  libraryType: '5',
  primaryClassificationUuid: 'dcfcb5e86e39474a9511e7c34cacd3d1',
};
const TITLE = 'USB_C_Hirose_CX_4800304000_seated';
const NEW_T = '448.8179849815368,328.7394915521145,0,0,0,0,0,-66.733,-80.315';
const CHUNK = 80_000;

const step = readFileSync(STEP_PATH);
const stepSha = createHash('sha256').update(step).digest('hex');
const stepText = step.toString('utf8');

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
const evaluate = async (expression, { awaitPromise = true } = {}) => {
  const fired = await send('Runtime.evaluate', {
    expression,
    returnByValue: true,
    awaitPromise,
  });
  if (fired.result?.exceptionDetails) {
    return { ok: false, exception: fired.result.exceptionDetails };
  }
  return fired.result?.result?.value;
};

await send('Runtime.enable');
const prep = await evaluate(`(() => {
  const R = window._EXTAPI_ROOT_;
  window.__STEP_CHUNKS = [];
  return { ok: !!R?.lib_3DModel?.create };
})()`, { awaitPromise: false });
if (!prep?.ok) {
  writeFileSync(OUT, JSON.stringify({ ok: false, stage: 'prep', prep, stepSha }, null, 2));
  ws.close();
  process.exit(1);
}

for (let offset = 0; offset < stepText.length; offset += CHUNK) {
  const piece = stepText.slice(offset, offset + CHUNK);
  const pushed = await evaluate(
    `window.__STEP_CHUNKS.push(${JSON.stringify(piece)}); window.__STEP_CHUNKS.length`,
    { awaitPromise: false },
  );
  if (typeof pushed !== 'number') {
    writeFileSync(OUT, JSON.stringify({ ok: false, stage: 'inject', offset, pushed, stepSha }, null, 2));
    ws.close();
    process.exit(1);
  }
}

const result = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  const personal = ${JSON.stringify(PERSONAL)};
  const classif = ${JSON.stringify(CLASSIF)};
  const title = ${JSON.stringify(TITLE)};
  const NEW_T = ${JSON.stringify(NEW_T)};
  const TAB = '${PCB}@${PROJECT}';
  const stepText = window.__STEP_CHUNKS.join('');
  const file = new File([stepText], title + '.STEP', { type: 'application/octet-stream' });
  const out = { fileSize: file.size };
  try { await R.dmt_EditorControl.activateDocument(TAB); } catch (e) { out.actErr = String(e && e.message || e); }
  await new Promise(r => setTimeout(r, 300));
  try {
    out.created = await R.lib_3DModel.create(personal, file, classif, 'mm');
  } catch (e) {
    out.createErr = String(e && e.message || e);
    try { out.created = await R.lib_3DModel.create(personal, file, undefined, 'mm'); }
    catch (e2) { out.createErr2 = String(e2 && e2.message || e2); }
  }
  const modelUuid = Array.isArray(out.created) ? out.created[0] : out.created;
  out.modelUuid = modelUuid;
  if (modelUuid) {
    try { out.renamed = await R.lib_3DModel.modify(modelUuid, personal, title, classif, 'CX70M-24P1 seating-plane bind for USB1 only'); }
    catch (e) { out.renameErr = String(e && e.message || e); }
    try { out.model = await R.lib_3DModel.get(modelUuid, personal); }
    catch (e) { out.modelErr = String(e && e.message || e); }
  }
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const usb1 = comps.find(c => c.getState_Designator() === 'USB1');
  const usb2 = comps.find(c => c.getState_Designator() === 'USB2');
  const u6 = comps.find(c => c.getState_Designator() === 'U6-RTC');
  const inspect = (c) => {
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    return {
      des: c.getState_Designator(),
      sid: c.getState_SupplierId(),
      mid: c.getState_ManufacturerId(),
      model: other['3D Model'],
      title: other['3D Model Title'],
      transform: other['3D Model Transform'],
      model3d: c.getState_Model3D && c.getState_Model3D(),
    };
  };
  out.before = { usb1: inspect(usb1), usb2: inspect(usb2), u6: inspect(u6) };
  if (!usb1 || usb1.getState_SupplierId() !== 'C778726') {
    out.ok = false;
    out.identity = out.before.usb1;
    delete window.__STEP_CHUNKS;
    return out;
  }
  if (!modelUuid) {
    out.ok = false;
    delete window.__STEP_CHUNKS;
    return out;
  }
  const prev = usb1.getState_OtherProperty() || {};
  out.modify = await R.pcb_PrimitiveComponent.modify(usb1, {
    otherProperty: {
      ...prev,
      '3D Model': modelUuid,
      '3D Model Title': title,
      '3D Model Transform': NEW_T,
    },
    model3D: { libraryUuid: personal, uuid: modelUuid, name: title },
  });
  out.saved = await R.pcb_Document.save('${PCB}');
  const again = await R.pcb_PrimitiveComponent.getAll();
  out.after = {
    usb1: inspect(again.find(c => c.getState_Designator() === 'USB1')),
    usb2: inspect(again.find(c => c.getState_Designator() === 'USB2')),
    u6: inspect(again.find(c => c.getState_Designator() === 'U6-RTC')),
  };
  out.ok = out.after.usb1.model === modelUuid
    && out.after.usb1.transform === NEW_T
    && out.after.usb2.transform === out.before.usb2.transform
    && out.after.u6.transform === out.before.u6.transform
    && out.after.usb2.model === out.before.usb2.model
    && out.after.u6.model === out.before.u6.model;
  delete window.__STEP_CHUNKS;
  return out;
})()`);

writeFileSync(OUT, JSON.stringify({ recorded_at: new Date().toISOString(), step_path: STEP_PATH, step_sha256: stepSha, result }, null, 2));
console.log(JSON.stringify({
  out: OUT,
  ok: result?.ok,
  modelUuid: result?.modelUuid,
  saved: result?.saved,
  createErr: result?.createErr,
  after: result?.after,
}, null, 2));
ws.close();
process.exit(result?.ok ? 0 : 1);
