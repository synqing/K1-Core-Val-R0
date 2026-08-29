#!/usr/bin/env node
import { writeFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const BASE = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-seat-probe6mm';

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
const clickAt = async (x, y) => {
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
};
const wheelAt = async (x, y, steps) => {
  for (let i = 0; i < steps; i++) {
    await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x, y, deltaX: 0, deltaY: -180 });
    await new Promise(r => setTimeout(r, 50));
  }
};

await send('Runtime.enable');
await send('Page.enable');

const pcb = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  try { await R.dmt_EditorControl.activateDocument('${PCB}@${PROJECT}'); } catch (e) {}
  await new Promise(r => setTimeout(r, 600));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const u1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'U1');
  if (u1) {
    try { await R.pcb_SelectControl.select([u1.getState_PrimitiveId()]); } catch (e) {}
  }
  const other = u1 && u1.getState_OtherProperty && u1.getState_OtherProperty();
  return {
    doc: await R.dmt_SelectControl.getCurrentDocumentInfo(),
    u1: u1 ? {
      id: u1.getState_PrimitiveId(),
      xf: other && other['3D Model Transform'],
      model: other && other['3D Model'],
    } : null,
  };
})()`);

const preview = await evaluate(clickTitle('3D Preview'));
await new Promise(r => setTimeout(r, 10000));
const refresh = await evaluate(clickTitle('Refresh'));
await new Promise(r => setTimeout(r, 9000));
const top = await evaluate(clickTitle('Top Side'));
await new Promise(r => setTimeout(r, 800));
const fit = await evaluate(clickTitle('Fit All in Window'));
await new Promise(r => setTimeout(r, 2000));

const probe = await evaluate(`(() => {
  const canvases = [...document.querySelectorAll('canvas')].map(c => {
    const r = c.getBoundingClientRect();
    return { w: c.width, h: c.height, dw: r.width, dh: r.height, x: r.left, y: r.top, vis: c.offsetParent !== null };
  });
  return { canvases, titles: [...document.querySelectorAll('[title]')].filter(x => x.offsetParent !== null).map(x => x.getAttribute('title')).filter(t => /fit|zoom|3d|preview|top|front|side|refresh/i.test(String(t))) };
})()`);

const wideTop = `${BASE}-wide-top.png`;
const results = [{ view: 'wide-top', path: wideTop, bytes: await shot(wideTop) }];

const crop = spawnSync('python3', [
  'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/crop-navy-u1.py',
  wideTop,
  `${BASE}-navy.png`,
  `${BASE}-navy-u1.png`,
], { encoding: 'utf8' });
let cropInfo = {};
try { cropInfo = JSON.parse(crop.stdout || '{}'); } catch { cropInfo = { raw: crop.stdout, err: crop.stderr }; }

const c3d = (probe.canvases || []).filter(c => c.vis && c.dw > 80 && c.dh > 80).sort((a, b) => (b.dw * b.dh) - (a.dw * a.dh))[0];
let zoomPt = null;
if (cropInfo.u1_css && c3d) {
  zoomPt = { x: cropInfo.u1_css[0], y: cropInfo.u1_css[1] };
} else if (c3d) {
  zoomPt = { x: c3d.x + c3d.dw * 0.28, y: c3d.y + c3d.dh * 0.22 };
}
if (zoomPt) {
  await clickAt(zoomPt.x, zoomPt.y);
  await wheelAt(zoomPt.x, zoomPt.y, 26);
  await new Promise(r => setTimeout(r, 1200));
}

const tightTop = `${BASE}-top.png`;
results.push({ view: 'top', path: tightTop, bytes: await shot(tightTop) });
spawnSync('python3', [
  'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/crop-navy-u1.py',
  tightTop,
  `${BASE}-top-navy.png`,
  `${BASE}-top-navy-u1.png`,
]);

const front = await evaluate(clickTitle('Front Side'));
await new Promise(r => setTimeout(r, 1500));
if (zoomPt) {
  await wheelAt(zoomPt.x, zoomPt.y + 40, 4);
  await new Promise(r => setTimeout(r, 800));
}
const edge = `${BASE}-edge.png`;
results.push({ view: 'edge', path: edge, bytes: await shot(edge), front });
spawnSync('python3', [
  'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/crop-navy-u1.py',
  edge,
  `${BASE}-edge-navy.png`,
  `${BASE}-edge-navy-u1.png`,
]);

const top2 = await evaluate(clickTitle('Top Side'));
await new Promise(r => setTimeout(r, 1000));
if (zoomPt) {
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: zoomPt.x, y: zoomPt.y, button: 'left', clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: zoomPt.x + 110, y: zoomPt.y + 70, button: 'left' });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: zoomPt.x + 110, y: zoomPt.y + 70, button: 'left', clickCount: 1 });
  await new Promise(r => setTimeout(r, 1000));
}
const iso = `${BASE}-iso.png`;
results.push({ view: 'iso', path: iso, bytes: await shot(iso), top2 });
spawnSync('python3', [
  'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/crop-navy-u1.py',
  iso,
  `${BASE}-iso-navy.png`,
  `${BASE}-iso-navy-u1.png`,
]);

console.log(JSON.stringify({ ok: true, pcb, preview, refresh, top, fit, probe, c3d, zoomPt, cropInfo, results }, null, 2));
ws.close();
