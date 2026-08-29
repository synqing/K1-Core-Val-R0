#!/usr/bin/env node
import { writeFile } from 'node:fs/promises';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const OUT = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-zup-rebuild.png';

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
  const r = hit.getBoundingClientRect();
  hit.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  return { ok: true, title: ${JSON.stringify(title)}, x: r.left + r.width/2, y: r.top + r.height/2 };
})()`;

await send('Runtime.enable');
await send('Page.enable');

const to2d = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  try { await R.dmt_EditorControl.activateDocument('${PCB}@${PROJECT}'); } catch (e) {}
  await new Promise(r => setTimeout(r, 800));
  return await R.dmt_SelectControl.getCurrentDocumentInfo();
})()`);

const preview = await evaluate(clickTitle('3D Preview'));
await new Promise(r => setTimeout(r, 12000));
const refresh = await evaluate(clickTitle('Refresh'));
await new Promise(r => setTimeout(r, 8000));
const fit = await evaluate(clickTitle('Fit All in Window'));
await new Promise(r => setTimeout(r, 2500));

const info = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  const doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  const canvases = [...document.querySelectorAll('canvas')].map(c => {
    const r = c.getBoundingClientRect();
    return { w: c.width, h: c.height, dw: r.width, dh: r.height, vis: c.offsetParent !== null, id: c.id, cls: c.className };
  });
  return { doc, canvases };
})()`);

const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
const buf = Buffer.from(shot.result.data, 'base64');
await writeFile(OUT, buf);
console.log(JSON.stringify({ ok: true, path: OUT, bytes: buf.length, to2d, preview, refresh, fit, info }, null, 2));
ws.close();
