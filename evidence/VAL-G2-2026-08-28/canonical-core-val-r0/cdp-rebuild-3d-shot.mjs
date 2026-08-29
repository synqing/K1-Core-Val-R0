#!/usr/bin/env node
import { writeFile } from 'node:fs/promises';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const OUT = process.argv[2]
  || 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/usb1-3d-after-seated-step.png';

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
await send('Page.enable');

const prep = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  const pcb = '${PCB}@${PROJECT}';
  const threeD = '2d-${PCB}@${PROJECT}';
  let closed = false;
  try {
    if (R.dmt_EditorControl.closeDocument) {
      await R.dmt_EditorControl.closeDocument(threeD);
      closed = true;
    }
  } catch (e) {}
  try { await R.dmt_EditorControl.activateDocument(pcb); } catch (e) {}
  await new Promise(r => setTimeout(r, 500));
  const doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  return { closed, doc, closeMethods: Object.getOwnPropertyNames(Object.getPrototypeOf(R.dmt_EditorControl || {})).filter(k => /close|Close|tab|Tab/.test(k)) };
})()`);

const clicked = await evaluate(`(() => {
  const nodes = [...document.querySelectorAll('[title],button,[aria-label]')].filter(x => x.offsetParent !== null);
  const hit = nodes.find(x => String(x.getAttribute('title') || x.getAttribute('aria-label') || '') === '3D Preview');
  if (!hit) return { ok: false, titles: nodes.map(x => x.getAttribute('title') || x.getAttribute('aria-label')).filter(Boolean).slice(0, 30) };
  hit.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  return { ok: true };
})()`);

await new Promise(r => setTimeout(r, 12000));

const after = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  const doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  const loading = [...document.querySelectorAll('*')].some(el =>
    el.offsetParent !== null && /loading|生成|Building|3D/i.test((el.textContent || '').slice(0, 40))
      && (el.textContent || '').length < 40);
  return { doc, loading };
})()`);

const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
if (shot.error || !shot.result?.data) throw new Error(shot.error?.message || 'no screenshot');
const buf = Buffer.from(shot.result.data, 'base64');
await writeFile(OUT, buf);
console.log(JSON.stringify({ ok: true, path: OUT, bytes: buf.length, prep, clicked, after }, null, 2));
ws.close();
