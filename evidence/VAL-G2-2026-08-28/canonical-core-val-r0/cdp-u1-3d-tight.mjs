#!/usr/bin/env node
import { writeFile } from 'node:fs/promises';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const BASE = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-zup-tight';

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
const shot = async (path) => {
  const reply = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
  if (reply.error || !reply.result?.data) throw new Error('no screenshot');
  const buf = Buffer.from(reply.result.data, 'base64');
  await writeFile(path, buf);
  return buf.length;
};
const wheelAt = async (x, y, steps) => {
  for (let i = 0; i < steps; i++) {
    await send('Input.dispatchMouseEvent', {
      type: 'mouseWheel',
      x, y,
      deltaX: 0,
      deltaY: -180,
    });
    await new Promise(r => setTimeout(r, 80));
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
  return u1 ? { id: u1.getState_PrimitiveId(), x: u1.getState_X(), y: u1.getState_Y(), rot: u1.getState_Rotation && u1.getState_Rotation() } : null;
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
} else {
  await new Promise(r => setTimeout(r, 4000));
}

const canvas = await evaluate(`(() => {
  const canvases = [...document.querySelectorAll('canvas')].filter(c => c.offsetParent !== null && c.width > 400 && c.height > 300);
  const c = canvases.sort((a,b) => (b.width*b.height) - (a.width*a.height))[0];
  if (!c) return null;
  const r = c.getBoundingClientRect();
  return { x: r.left, y: r.top, w: r.width, h: r.height, cw: c.width, ch: c.height };
})()`);

const results = [];
const views = ['Top Side', 'Front Side'];
for (const view of views) {
  const clicked = await evaluate(clickTitle(view));
  await new Promise(r => setTimeout(r, 1000));
  await evaluate(clickTitle('Fit All in Window'));
  await new Promise(r => setTimeout(r, 1500));
  const cx = canvas ? canvas.x + canvas.w * 0.42 : 900;
  const cy = canvas ? canvas.y + canvas.h * 0.38 : 500;
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: cx, y: cy, button: 'left', clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: cx, y: cy, button: 'left', clickCount: 1 });
  await wheelAt(cx, cy, 18);
  await new Promise(r => setTimeout(r, 1200));
  const slug = view.toLowerCase().replace(/\s+/g, '-');
  const path = `${BASE}-${slug}.png`;
  const bytes = await shot(path);
  results.push({ view, clicked, path, bytes, zoomAt: { cx, cy } });
}

// iso-ish: from top, drag orbit
if (canvas) {
  await evaluate(clickTitle('Top Side'));
  await new Promise(r => setTimeout(r, 800));
  await evaluate(clickTitle('Fit All in Window'));
  await new Promise(r => setTimeout(r, 1200));
  const cx = canvas.x + canvas.w * 0.42;
  const cy = canvas.y + canvas.h * 0.38;
  await wheelAt(cx, cy, 16);
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: cx, y: cy, button: 'left', clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: cx + 140, y: cy + 90, button: 'left' });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: cx + 140, y: cy + 90, button: 'left', clickCount: 1 });
  await new Promise(r => setTimeout(r, 1000));
  const path = `${BASE}-iso.png`;
  const bytes = await shot(path);
  results.push({ view: 'iso-orbit', path, bytes });
}

console.log(JSON.stringify({ ok: true, pcb, threeD, canvas, results }, null, 2));
ws.close();
