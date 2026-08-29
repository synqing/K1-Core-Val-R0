#!/usr/bin/env node
import { writeFile } from 'node:fs/promises';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const OUT3D = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/usb1-3d-reconcile-identity-2026-08-30b.png';
const OUT2D = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-gtusb-2d-identity-2026-08-30.png';

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const page = targets.find(t => t.type === 'page' && String(t.url).includes(PROJECT));
if (!page) throw new Error(`no CDP page for ${PROJECT}`);
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
const shot = async (path) => {
  const reply = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
  if (reply.error || !reply.result?.data) throw new Error(reply.error?.message || 'no screenshot');
  const buf = Buffer.from(reply.result.data, 'base64');
  await writeFile(path, buf);
  return buf.length;
};

await send('Runtime.enable');
await send('Page.enable');

const clickTitle = (title) => `(() => {
  const nodes = [...document.querySelectorAll('[title],button,[aria-label]')].filter(x => x.offsetParent !== null);
  const hit = nodes.find(x => String(x.getAttribute('title') || x.getAttribute('aria-label') || '') === ${JSON.stringify(title)});
  if (!hit) return { ok: false, title: ${JSON.stringify(title)} };
  hit.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  return { ok: true, title: ${JSON.stringify(title)} };
})()`;

const threeDTab = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  try { await R.dmt_EditorControl.activateDocument('2d-${PCB}@${PROJECT}'); } catch (e) {}
  await new Promise(r => setTimeout(r, 400));
  return await R.dmt_SelectControl.getCurrentDocumentInfo();
})()`);

let clicked3d = { skipped: true };
if (threeDTab?.documentType !== 15) {
  clicked3d = await evaluate(clickTitle('3D Preview'));
  await new Promise(r => setTimeout(r, 12000));
} else {
  await new Promise(r => setTimeout(r, 4000));
}

const fit3d = await evaluate(`(() => {
  const titles = [...document.querySelectorAll('[title]')].filter(x => x.offsetParent !== null).map(x => x.getAttribute('title'));
  const hit = [...document.querySelectorAll('[title]')].find(x => x.offsetParent !== null && /^Fit /.test(String(x.getAttribute('title') || '')));
  if (hit) hit.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  return { titles: titles.slice(0, 40), fitted: !!hit, fitTitle: hit && hit.getAttribute('title') };
})()`);
await new Promise(r => setTimeout(r, 2500));
const after3d = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  return await R.dmt_SelectControl.getCurrentDocumentInfo();
})()`);
const bytes3d = await shot(OUT3D);

const pcb = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  await R.dmt_EditorControl.activateDocument('${PCB}@${PROJECT}');
  await new Promise(r => setTimeout(r, 800));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const u1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'U1');
  if (u1) {
    try { await R.pcb_SelectControl.select([u1.getState_PrimitiveId()]); } catch (e) {}
  }
  return {
    doc: await R.dmt_SelectControl.getCurrentDocumentInfo(),
    u1: u1 ? { id: u1.getState_PrimitiveId(), sid: u1.getState_SupplierId(), mid: u1.getState_ManufacturerId(), x: u1.getState_X(), y: u1.getState_Y() } : null,
  };
})()`);
await new Promise(r => setTimeout(r, 400));
const fit2d = await evaluate(clickTitle('Fit Selection View'));
if (!fit2d?.ok) {
  await evaluate(`(() => {
    const hit = [...document.querySelectorAll('[title]')].find(x => x.offsetParent !== null && /^Fit /.test(String(x.getAttribute('title') || '')));
    if (hit) hit.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    return { ok: !!hit, title: hit && hit.getAttribute('title') };
  })()`);
}
await new Promise(r => setTimeout(r, 1800));
const bytes2d = await shot(OUT2D);

console.log(JSON.stringify({
  ok: true,
  threeDTab, clicked3d, fit3d, after3d, bytes3d, path3d: OUT3D,
  pcb, fit2d, bytes2d, path2d: OUT2D,
}, null, 2));
ws.close();
