#!/usr/bin/env node
import { writeFile } from 'node:fs/promises';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const OUT = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-gtusb-3d-after-bind-close.png';

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
  await new Promise(r => setTimeout(r, 500));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const u1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'U1');
  if (u1) {
    try { await R.pcb_SelectControl.select([u1.getState_PrimitiveId()]); } catch (e) {}
  }
  return u1 ? { id: u1.getState_PrimitiveId(), x: u1.getState_X(), y: u1.getState_Y() } : null;
})()`);

const threeD = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  try { await R.dmt_EditorControl.activateDocument('2d-${PCB}@${PROJECT}'); } catch (e) {}
  await new Promise(r => setTimeout(r, 400));
  return await R.dmt_SelectControl.getCurrentDocumentInfo();
})()`);
if (threeD?.documentType !== 15) {
  await evaluate(clickTitle('3D Preview'));
  await new Promise(r => setTimeout(r, 8000));
} else {
  await new Promise(r => setTimeout(r, 2000));
}

const fit = await evaluate(`(() => {
  const titles = [...document.querySelectorAll('[title]')].filter(x => x.offsetParent !== null).map(x => x.getAttribute('title'));
  const hit = [...document.querySelectorAll('[title]')].find(x =>
    x.offsetParent !== null && String(x.getAttribute('title') || '').startsWith('Fit Selection View'));
  if (hit) hit.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  return { fitted: !!hit, fitTitle: hit && hit.getAttribute('title'), titles: titles.slice(0, 50) };
})()`);
await new Promise(r => setTimeout(r, 1500));

let zooms = 0;
for (let i = 0; i < 4; i++) {
  const z = await evaluate(`(() => {
    const e = [...document.querySelectorAll('[title]')].find(x =>
      x.offsetParent !== null && String(x.getAttribute('title') || '').startsWith('Zoom In'));
    if (!e) return { ok: false };
    e.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    return { ok: true };
  })()`);
  if (!z?.ok) break;
  zooms += 1;
  await new Promise(r => setTimeout(r, 400));
}
await new Promise(r => setTimeout(r, 1800));

const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
if (shot.error || !shot.result?.data) throw new Error('no screenshot');
const buf = Buffer.from(shot.result.data, 'base64');
await writeFile(OUT, buf);
console.log(JSON.stringify({ ok: true, path: OUT, bytes: buf.length, pcb, threeD, fit, zooms }, null, 2));
ws.close();
