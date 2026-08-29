#!/usr/bin/env node
import { writeFile } from 'node:fs/promises';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const OUT = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-gtusb-3d-after-bind.png';

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

const opened = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  try { await R.dmt_EditorControl.activateDocument('${PCB}@${PROJECT}'); } catch (e) {}
  await new Promise(r => setTimeout(r, 400));
  try {
    const comps = await R.pcb_PrimitiveComponent.getAll();
    const u1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'U1');
    if (u1) await R.pcb_SelectControl.select([u1.getState_PrimitiveId()]);
  } catch (e) {}
  try { await R.dmt_EditorControl.activateDocument('2d-${PCB}@${PROJECT}'); } catch (e) {}
  await new Promise(r => setTimeout(r, 500));
  return await R.dmt_SelectControl.getCurrentDocumentInfo();
})()`);

if (opened?.documentType !== 15) {
  await evaluate(`(() => {
    const hit = [...document.querySelectorAll('[title],button,[aria-label]')].find(x =>
      x.offsetParent !== null && String(x.getAttribute('title') || x.getAttribute('aria-label') || '') === '3D Preview');
    if (hit) hit.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    return { ok: !!hit };
  })()`);
  await new Promise(r => setTimeout(r, 10000));
} else {
  await new Promise(r => setTimeout(r, 5000));
}

await evaluate(`(() => {
  const hit = [...document.querySelectorAll('[title]')].find(x =>
    x.offsetParent !== null && /^Fit /.test(String(x.getAttribute('title') || '')));
  if (hit) hit.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  return { ok: !!hit, title: hit && hit.getAttribute('title') };
})()`);
await new Promise(r => setTimeout(r, 2500));

const after = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  return await R.dmt_SelectControl.getCurrentDocumentInfo();
})()`);
const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
if (shot.error || !shot.result?.data) throw new Error('no screenshot');
const buf = Buffer.from(shot.result.data, 'base64');
await writeFile(OUT, buf);
console.log(JSON.stringify({ ok: true, path: OUT, bytes: buf.length, opened, after }, null, 2));
ws.close();
