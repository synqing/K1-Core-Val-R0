#!/usr/bin/env node
// Import NXP/SamacSys MIMXRT1061DVJ6B STEP into the personal 3D library.
// Silicon identity stays MIMXRT1062DVJ6B — this is a donor body for the same 12x12/0.8 package.
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = process.env.EASYEDA_PROJECT || '64325d0e55e0435abd018defb0089a9b';
const STEP_PATH = process.env.STEP_PATH
  || '/Users/spectrasynq/Downloads/LIB_MIMXRT1061DVJ6B/MIMXRT1061DVJ6B/3D/MIMXRT1061DVJ6B.stp';
const OUT = process.env.OUT
  || 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/nxp-rt1062-3d-import.json';
const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
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
  window.__STEP_CHUNKS = [];
  return { ok: !!window._EXTAPI_ROOT_?.lib_3DModel?.create };
})()`, { awaitPromise: false });
if (!prep?.ok) {
  writeFileSync(OUT, JSON.stringify({ ok: false, stage: 'prep', prep, stepSha }, null, 2));
  ws.close();
  process.exit(1);
}
for (let offset = 0; offset < stepText.length; offset += CHUNK) {
  const piece = stepText.slice(offset, offset + CHUNK);
  await evaluate(
    `window.__STEP_CHUNKS.push(${JSON.stringify(piece)}); window.__STEP_CHUNKS.length`,
    { awaitPromise: false },
  );
}

const result = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  const personal = ${JSON.stringify(PERSONAL)};
  const stepText = window.__STEP_CHUNKS.join('');
  const file = new File([stepText], 'MIMXRT1061DVJ6B.stp', { type: 'application/octet-stream' });
  const classif = { libraryUuid: personal, libraryType: '5', primaryClassificationUuid: 'dcfcb5e86e39474a9511e7c34cacd3d1' };
  const out = { stepChars: stepText.length, fileSize: file.size };
  try { out.created = await R.lib_3DModel.create(personal, file, classif, 'mm'); }
  catch (e) { out.createErr = String(e && e.message || e); }
  const modelUuid = Array.isArray(out.created) ? out.created[0] : out.created;
  out.modelUuid = modelUuid;
  if (modelUuid) {
    try { out.model = await R.lib_3DModel.get(modelUuid, personal); } catch (e) { out.modelErr = String(e && e.message || e); }
    try {
      out.reclass = await R.lib_3DModel.modify(modelUuid, personal, 'MIMXRT1062DVJ6B-NXP-BODY', classif, 'NXP/SamacSys donor body for MIMXRT1062DVJ6B 12x12/0.8 MAPBGA');
    } catch (e) { out.reclassErr = String(e && e.message || e); }
  }
  try { out.search = await R.lib_3DModel.search('MIMXRT1061', personal, undefined, 5, 1); } catch (e) { out.searchErr = String(e && e.message || e); }
  out.ok = !!modelUuid;
  delete window.__STEP_CHUNKS;
  return out;
})()`);

const payload = {
  recorded_at: new Date().toISOString(),
  step_path: STEP_PATH,
  step_sha256: stepSha,
  step_bytes: step.length,
  note: 'Donor 3D only. Frozen MPN remains MIMXRT1062DVJ6B.',
  result,
};
writeFileSync(OUT, JSON.stringify(payload, null, 2));
console.log(JSON.stringify({
  out: OUT,
  ok: result?.ok,
  modelUuid: result?.modelUuid,
  modelName: result?.model?.name,
  search: result?.search,
  createErr: result?.createErr,
}, null, 2));
ws.close();
process.exit(result?.ok ? 0 : 1);
