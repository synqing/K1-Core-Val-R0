#!/usr/bin/env node
// Hub-candidate zoom+screenshot. Same traps as harness/easyeda_canonical_zoom_shot.mjs
// but parent UUID is the disposable hub, never live 64325d0e.
//
// Usage: node hub_zoom_shot.mjs <out.png> region <l> <r> <t> <b>
//        node hub_zoom_shot.mjs <out.png> select <id,id,...>
//        node hub_zoom_shot.mjs <out.png> whole

import { writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = process.env.EASYEDA_PROJECT || '41c8e6523576456582ea35958b3684ed';
const PAGE = process.env.EASYEDA_PAGE || '1435cb46f39e48c8a8aadbb84ca81603';
const TAB = `${PAGE}@${PROJECT}`;
const CTX_WAIT_MS = Number(process.env.EASYEDA_CTX_WAIT_MS || 1500);
const SETTLE_MS = Number(process.env.EASYEDA_SETTLE_MS || 2500);

const [outPath, mode, ...rest] = process.argv.slice(2);
if (!outPath || !['region', 'select', 'whole'].includes(mode)) {
  console.error('usage: <out.png> region <l> <r> <t> <b> | select <id,id,...> | whole');
  process.exit(2);
}
if (PROJECT === '64325d0e55e0435abd018defb0089a9b') {
  console.error('refusing to screenshot live product');
  process.exit(2);
}

const targets = await (await fetch(`${CDP_BASE}/json/list`, { signal: AbortSignal.timeout(3000) })).json();
const target = targets.find(t => t.type === 'page' && String(t.url).includes(PROJECT));
if (!target) throw new Error(`no CDP page target for hub project ${PROJECT}`);

const ws = new WebSocket(target.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
const ctxs = [];
ws.onmessage = ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  if (m.method === 'Runtime.executionContextCreated') ctxs.push(m.params.context);
};
await new Promise(r => { ws.onopen = r; });
const send = (method, params = {}) => new Promise(res => {
  const i = ++id; pending.set(i, res);
  ws.send(JSON.stringify({ id: i, method, params }));
});

await send('Runtime.enable');
await send('Page.enable');
const tree = await send('Page.getFrameTree');
const frames = [];
(function walk(n) { if (n?.frame) frames.push(n.frame); for (const c of n.childFrames || []) walk(c); })(
  tree.result?.frameTree || tree.result);
await new Promise(r => setTimeout(r, CTX_WAIT_MS));

const hubFrame = frames.find(f => String(f.name || '').includes(PAGE));
if (!hubFrame) throw new Error(`hub schematic frame not found (frame_${TAB})`);
const hubCtx = ctxs.find(c => c.auxData?.frameId === hubFrame.id);
if (!hubCtx) throw new Error('hub frame execution context never arrived — raise EASYEDA_CTX_WAIT_MS');

const fire = async expression => {
  const r = await send('Runtime.evaluate',
    { contextId: hubCtx.id, expression, returnByValue: true, awaitPromise: false });
  return r.result?.result?.value ?? { ok: false, exception: r.result?.exceptionDetails?.text };
};
const capture = async () => {
  const s = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
  if (s.error || !s.result?.data) throw new Error(s.error?.message || 'captureScreenshot returned no data');
  return Buffer.from(s.result.data, 'base64');
};

const before = await capture();

let call;
if (mode === 'region') {
  const [l, r, t, b] = rest.map(Number);
  if (![l, r, t, b].every(Number.isFinite)) throw new Error('region needs four numeric bounds');
  call = `void EC.zoomToRegion(${l}, ${r}, ${t}, ${b}, ${JSON.stringify(TAB)});`;
} else if (mode === 'select') {
  const ids = String(rest[0] || '').split(',').map(s => s.trim()).filter(Boolean);
  if (!ids.length) throw new Error('select needs at least one primitive id');
  call = `void R.sch_SelectControl.doSelectPrimitives(${JSON.stringify(ids)}, ${JSON.stringify(TAB)});
          void EC.zoomToSelectedPrimitives(${JSON.stringify(TAB)});`;
} else {
  call = `void EC.zoomToFit(${JSON.stringify(TAB)});`;
}

const fired = await fire(`(() => {
  const R = window._EXTAPI_ROOT_;
  const EC = R && R.dmt_EditorControl;
  if (!EC) return { ok:false, reason:'dmt_EditorControl absent' };
  try { ${call} } catch (e) { return { ok:false, err:String((e&&e.message)||e) }; }
  return { ok:true, fired:true };
})()`);
if (!fired.ok) { console.log(JSON.stringify({ ok: false, stage: 'call', fired }, null, 2)); ws.close(); process.exit(1); }

await new Promise(r => setTimeout(r, SETTLE_MS));
const after = await capture();

const h = b => createHash('sha256').update(b).digest('hex');
const moved = h(before) !== h(after);
if (!moved) {
  console.log(JSON.stringify({
    ok: false, stage: 'witness',
    reason: 'view did not change — the call returned without acting. Do NOT treat this as evidence.',
    sha256_before: h(before).slice(0, 16), sha256_after: h(after).slice(0, 16),
  }, null, 2));
  ws.close();
  process.exit(1);
}

if (after.subarray(0, 8).toString('binary') !== '\x89PNG\r\n\x1a\n') throw new Error('capture is not a PNG');
const width = after.readUInt32BE(16), height = after.readUInt32BE(20);
if (width < 640 || height < 360) throw new Error(`screenshot too small for granular inspection: ${width}x${height}`);
await writeFile(outPath, after);
console.log(JSON.stringify({ ok: true, path: outPath, width, height, mode,
  view_changed: true, sha256: h(after).slice(0, 16), context_id: hubCtx.id, page_tab: TAB,
  project: PROJECT }, null, 2));
ws.close();
