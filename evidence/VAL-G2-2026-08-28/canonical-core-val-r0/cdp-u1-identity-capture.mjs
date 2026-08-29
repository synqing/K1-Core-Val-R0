#!/usr/bin/env node
import { writeFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const WIDE = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-identity-wide.png';
const TIGHT = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-identity-tight.png';

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
const clickTitle = (title) => `(() => {
  const nodes = [...document.querySelectorAll('[title],button,[aria-label]')].filter(x => x.offsetParent !== null);
  const hit = nodes.find(x => String(x.getAttribute('title') || x.getAttribute('aria-label') || '') === ${JSON.stringify(title)});
  if (!hit) return { ok: false, title: ${JSON.stringify(title)} };
  hit.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  return { ok: true, title: ${JSON.stringify(title)} };
})()`;

await send('Runtime.enable');
await send('Page.enable');
const pcb = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  try { await R.dmt_EditorControl.activateDocument('${PCB}@${PROJECT}'); } catch (e) {}
  await new Promise(r => setTimeout(r, 400));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const u1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'U1');
  const other = u1 && u1.getState_OtherProperty && u1.getState_OtherProperty();
  return {
    id: u1 && u1.getState_PrimitiveId(),
    model: other && other['3D Model'],
    xf: other && other['3D Model Transform'],
  };
})()`);

await evaluate(clickTitle('3D Preview'));
await new Promise(r => setTimeout(r, 10000));
const refresh = await evaluate(clickTitle('Refresh'));
await new Promise(r => setTimeout(r, 9000));
const top = await evaluate(clickTitle('Top Side'));
await new Promise(r => setTimeout(r, 800));
const fit = await evaluate(clickTitle('Fit All in Window'));
await new Promise(r => setTimeout(r, 2000));
const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
if (shot.error || !shot.result?.data) throw new Error('no screenshot');
const buf = Buffer.from(shot.result.data, 'base64');
await writeFile(WIDE, buf);

const crop = spawnSync('python3', [
  'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/crop-identity-u1.py',
  WIDE,
  TIGHT,
], { encoding: 'utf8' });
let cropInfo = {};
try { cropInfo = JSON.parse(crop.stdout || '{}'); } catch { cropInfo = { raw: crop.stdout, err: crop.stderr }; }
console.log(JSON.stringify({ ok: true, pcb, refresh, top, fit, wide: WIDE, bytes: buf.length, cropInfo }, null, 2));
ws.close();
