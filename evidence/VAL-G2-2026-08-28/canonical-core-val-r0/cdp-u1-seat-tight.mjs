#!/usr/bin/env node
import { writeFile } from 'node:fs/promises';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const BASE = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-seat-tight';

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
const clickStarts = (prefix) => `(() => {
  const hit = [...document.querySelectorAll('[title]')].find(x =>
    x.offsetParent !== null && String(x.getAttribute('title') || '').startsWith(${JSON.stringify(prefix)}));
  if (!hit) return { ok: false, prefix: ${JSON.stringify(prefix)} };
  hit.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  return { ok: true, title: hit.getAttribute('title') };
})()`;
const shot = async (path) => {
  const reply = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
  if (reply.error || !reply.result?.data) throw new Error('no screenshot');
  const buf = Buffer.from(reply.result.data, 'base64');
  await writeFile(path, buf);
  return buf.length;
};
const wheelAt = async (x, y, steps) => {
  for (let i = 0; i < steps; i++) {
    await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x, y, deltaX: 0, deltaY: -180 });
    await new Promise(r => setTimeout(r, 70));
  }
};

await send('Runtime.enable');
await send('Page.enable');

const pcb = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  try { await R.dmt_EditorControl.activateDocument('${PCB}@${PROJECT}'); } catch (e) {}
  await new Promise(r => setTimeout(r, 400));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const u1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'U1');
  if (u1) {
    try { await R.pcb_SelectControl.select([u1.getState_PrimitiveId()]); } catch (e) {}
  }
  const other = u1 && (u1.getState_OtherProperty && u1.getState_OtherProperty()) || {};
  return u1 ? {
    id: u1.getState_PrimitiveId(),
    model: other['3D Model'],
    xf: other['3D Model Transform'],
  } : null;
})()`);

const threeD = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  try { await R.dmt_EditorControl.activateDocument('2d-${PCB}@${PROJECT}'); } catch (e) {}
  await new Promise(r => setTimeout(r, 400));
  return await R.dmt_SelectControl.getCurrentDocumentInfo();
})()`);
if (threeD?.documentType !== 15) {
  await evaluate(clickTitle('3D Preview'));
  await new Promise(r => setTimeout(r, 10000));
}
const refresh = await evaluate(clickTitle('Refresh'));
await new Promise(r => setTimeout(r, 8000));

const canvas = await evaluate(`(() => {
  const canvases = [...document.querySelectorAll('canvas')].filter(c => c.offsetParent !== null && c.width > 400 && c.height > 300);
  const c = canvases.sort((a,b) => (b.width*b.height) - (a.width*a.height))[0];
  if (!c) return null;
  const r = c.getBoundingClientRect();
  return { x: r.left, y: r.top, w: r.width, h: r.height, cw: c.width, ch: c.height };
})()`);

const results = [];
const frame = async (view, extra) => {
  const clicked = view ? await evaluate(clickTitle(view)) : { skipped: true };
  await new Promise(r => setTimeout(r, 800));
  const fitSel = await evaluate(clickStarts('Fit Selection View'));
  await new Promise(r => setTimeout(r, 900));
  if (!fitSel?.ok) {
    await evaluate(clickTitle('Fit All in Window'));
    await new Promise(r => setTimeout(r, 900));
  }
  const cx = canvas ? canvas.x + canvas.w * 0.42 : 900;
  const cy = canvas ? canvas.y + canvas.h * 0.38 : 500;
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: cx, y: cy, button: 'left', clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: cx, y: cy, button: 'left', clickCount: 1 });
  await wheelAt(cx, cy, 14);
  if (extra) await extra(cx, cy);
  await new Promise(r => setTimeout(r, 1000));
  return { clicked, fitSel };
};

let meta = await frame('Top Side');
let path = `${BASE}-top.png`;
results.push({ view: 'top', ...meta, path, bytes: await shot(path) });

meta = await frame('Front Side');
path = `${BASE}-edge.png`;
results.push({ view: 'edge-front', ...meta, path, bytes: await shot(path) });

meta = await frame('Top Side', async (cx, cy) => {
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: cx, y: cy, button: 'left', clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: cx + 150, y: cy + 100, button: 'left' });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: cx + 150, y: cy + 100, button: 'left', clickCount: 1 });
});
path = `${BASE}-iso.png`;
results.push({ view: 'iso', ...meta, path, bytes: await shot(path) });

console.log(JSON.stringify({ ok: true, pcb, threeD, refresh, canvas, results }, null, 2));
ws.close();
