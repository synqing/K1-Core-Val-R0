#!/usr/bin/env node
import { writeFile } from 'node:fs/promises';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const BASE = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-seat-recapture';

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
    await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x, y, deltaX: 0, deltaY: -200 });
    await new Promise(r => setTimeout(r, 60));
  }
};

await send('Runtime.enable');
await send('Page.enable');

const pcb = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  try { await R.dmt_EditorControl.activateDocument('${PCB}@${PROJECT}'); } catch (e) {}
  await new Promise(r => setTimeout(r, 800));
  return await R.dmt_SelectControl.getCurrentDocumentInfo();
})()`);

const preview = await evaluate(clickTitle('3D Preview'));
await new Promise(r => setTimeout(r, 12000));
const refresh = await evaluate(clickTitle('Refresh'));
await new Promise(r => setTimeout(r, 8000));
const top = await evaluate(clickTitle('Top Side'));
await new Promise(r => setTimeout(r, 1000));
const fit = await evaluate(clickTitle('Fit All in Window'));
await new Promise(r => setTimeout(r, 2500));

const probe = await evaluate(`(() => {
  const canvases = [...document.querySelectorAll('canvas')].map(c => {
    const r = c.getBoundingClientRect();
    return { w: c.width, h: c.height, dw: r.width, dh: r.height, x: r.left, y: r.top, vis: c.offsetParent !== null, id: c.id, cls: String(c.className).slice(0, 80) };
  });
  const titles = [...document.querySelectorAll('[title]')].filter(x => x.offsetParent !== null).map(x => x.getAttribute('title'));
  return { canvases, titles: titles.filter(t => /fit|zoom|3d|preview|top|front|side|camera/i.test(String(t))) };
})()`);

const c3d = (probe.canvases || [])
  .filter(c => c.vis && c.dw > 80 && c.dh > 80)
  .sort((a, b) => (b.dw * b.dh) - (a.dw * a.dh))[0];

const results = [];
if (c3d) {
  const cx = c3d.x + c3d.dw * 0.45;
  const cy = c3d.y + c3d.dh * 0.22;
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: cx, y: cy, button: 'left', clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: cx, y: cy, button: 'left', clickCount: 1 });
  await wheelAt(cx, cy, 22);
  await new Promise(r => setTimeout(r, 1200));
}
results.push({ view: 'top', path: `${BASE}-top.png`, bytes: await shot(`${BASE}-top.png`) });

const front = await evaluate(clickTitle('Front Side'));
await new Promise(r => setTimeout(r, 1500));
if (c3d) {
  const cx = c3d.x + c3d.dw * 0.45;
  const cy = c3d.y + c3d.dh * 0.40;
  await wheelAt(cx, cy, 6);
  await new Promise(r => setTimeout(r, 1000));
}
results.push({ view: 'edge', path: `${BASE}-edge.png`, bytes: await shot(`${BASE}-edge.png`), front });

const top2 = await evaluate(clickTitle('Top Side'));
await new Promise(r => setTimeout(r, 1000));
if (c3d) {
  const cx = c3d.x + c3d.dw * 0.45;
  const cy = c3d.y + c3d.dh * 0.28;
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: cx, y: cy, button: 'left', clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: cx + 120, y: cy + 80, button: 'left' });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: cx + 120, y: cy + 80, button: 'left', clickCount: 1 });
  await new Promise(r => setTimeout(r, 1000));
}
results.push({ view: 'iso', path: `${BASE}-iso.png`, bytes: await shot(`${BASE}-iso.png`), top2 });

console.log(JSON.stringify({ ok: true, pcb, preview, refresh, top, fit, probe, c3d, results }, null, 2));
ws.close();
