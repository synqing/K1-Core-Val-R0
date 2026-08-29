#!/usr/bin/env node
// Import the Hirose USB-C STEP into the EasyEDA personal library and bind it
// onto a writable copy of CX70M-24P1 (C778726). Official LCSC devices are
// read-only; the personal copy keeps the same LCSC identity.
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = process.env.EASYEDA_PROJECT || '64325d0e55e0435abd018defb0089a9b';
const STEP_PATH = process.env.STEP_PATH
  || '/Users/spectrasynq/Downloads/User Library-USB_C_Hirose_CX_4800304000_v3.STEP';
const OUT = process.env.OUT
  || 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/hirose-usbc-3d-bind.json';
const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
const SYSTEM = '0819f05c4eef4c71ace90d822a990e87';
const OFFICIAL = '4db9e6982d2c421c8c7ea67eaf304069';
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
    return {
      ok: false,
      exception: fired.result.exceptionDetails,
      preview: fired.result.result,
    };
  }
  return fired.result?.result?.value;
};

await send('Runtime.enable');

const prep = await evaluate(`(() => {
  const R = window._EXTAPI_ROOT_;
  window.__STEP_CHUNKS = [];
  return {
    ok: !!R?.lib_3DModel?.create,
    hasDevice: !!R?.lib_Device?.copy,
    personalReady: true,
  };
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
  const system = ${JSON.stringify(SYSTEM)};
  const official = ${JSON.stringify(OFFICIAL)};
  const stepText = window.__STEP_CHUNKS.join('');
  const file = new File([stepText], 'USB_C_Hirose_CX_4800304000_v3.STEP', { type: 'application/octet-stream' });
  const out = {
    stepChars: stepText.length,
    fileSize: file.size,
    fileName: file.name,
  };
  try { out.personalUuid = await R.lib_LibrariesList.getPersonalLibraryUuid(); } catch (e) { out.personalErr = String(e && e.message || e); }
  try { out.classTree = await R.lib_Classification.getAllClassificationTree(personal); } catch (e) { out.classTreeErr = String(e && e.message || e); }

  const tryCreate = async (classification, unit) => {
    try {
      return { ok: true, created: await R.lib_3DModel.create(personal, file, classification, unit) };
    } catch (e) {
      return { ok: false, err: String(e && e.message || e) };
    }
  };
  out.createMm = await tryCreate(undefined, 'mm');
  if (!out.createMm.ok) out.createNoUnit = await tryCreate(undefined, undefined);
  if ((!out.createMm.ok && !out.createNoUnit?.ok) && Array.isArray(out.classTree) && out.classTree[0]) {
    const first = out.classTree[0];
    const classification = first.uuid
      ? { libraryUuid: personal, primaryClassificationUuid: first.uuid }
      : [first.name || 'Connectors'];
    out.createWithClass = await tryCreate(classification, 'mm');
  }
  const created = out.createMm.created || out.createNoUnit?.created || out.createWithClass?.created;
  out.created = created;
  const modelUuid = Array.isArray(created) ? created[0] : created;
  out.modelUuid = modelUuid;
  if (modelUuid) {
    try { out.model = await R.lib_3DModel.get(modelUuid, personal); } catch (e) { out.modelErr = String(e && e.message || e); }
  }

  if (modelUuid) {
    try {
      out.officialModify = await R.lib_Device.modify(
        official, system, undefined, undefined,
        { model3D: { uuid: modelUuid, libraryUuid: personal } },
      );
    } catch (e) {
      out.officialModifyErr = String(e && e.message || e);
    }
    try { out.officialAfter = await R.lib_Device.get(official, system); } catch (e) { out.officialAfterErr = String(e && e.message || e); }

    const copyNames = ['CX70M-24P1', 'CX70M-24P1-C778726', 'CX70M-24P1-HIROSE'];
    for (const name of copyNames) {
      try {
        out.copied = await R.lib_Device.copy(official, system, personal, undefined, name);
        out.copiedName = name;
        if (out.copied) break;
      } catch (e) {
        out['copyErr_' + name] = String(e && e.message || e);
      }
    }
    const destUuid = typeof out.copied === 'string' ? out.copied : null;
    out.destUuid = destUuid;
    if (destUuid) {
      try {
        out.personalModify = await R.lib_Device.modify(
          destUuid, personal, undefined, undefined,
          { model3D: { uuid: modelUuid, libraryUuid: personal } },
        );
      } catch (e) {
        out.personalModifyErr = String(e && e.message || e);
      }
      try { out.personalDevice = await R.lib_Device.get(destUuid, personal); } catch (e) { out.personalDeviceErr = String(e && e.message || e); }
    }
  }

  try { out.searchPersonalCx = await R.lib_Device.search('CX70M-24P1', personal, undefined, 10, 1); } catch (e) { out.searchPersonalCxErr = String(e && e.message || e); }
  try { out.search3dAfter = await R.lib_3DModel.search('4800304000', personal, undefined, 10, 1); } catch (e) { out.search3dAfterErr = String(e && e.message || e); }
  try { out.search3dUsb = await R.lib_3DModel.search('USB_C_Hirose', personal, undefined, 10, 1); } catch (e) { out.search3dUsbErr = String(e && e.message || e); }

  const assoc = out.personalDevice?.association?.model3D || out.officialAfter?.association?.model3D;
  out.ok = !!(modelUuid && assoc && (assoc.uuid === modelUuid));
  delete window.__STEP_CHUNKS;
  return out;
})()`);

const payload = {
  recorded_at: new Date().toISOString(),
  step_path: STEP_PATH,
  step_sha256: stepSha,
  step_bytes: step.length,
  result,
};
writeFileSync(OUT, JSON.stringify(payload, null, 2));
console.log(JSON.stringify({
  out: OUT,
  ok: result?.ok,
  modelUuid: result?.modelUuid,
  destUuid: result?.destUuid,
  officialModify: result?.officialModify,
  officialModifyErr: result?.officialModifyErr,
  personalModify: result?.personalModify,
  createMm: result?.createMm,
  createNoUnit: result?.createNoUnit,
  createWithClass: result?.createWithClass,
  modelName: result?.model?.name,
  personalAssoc: result?.personalDevice?.association?.model3D,
  officialAssoc: result?.officialAfter?.association?.model3D,
}, null, 2));
ws.close();
process.exit(result?.ok ? 0 : 1);
