#!/usr/bin/env node
import { writeFile } from 'node:fs/promises';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const USB1 = '19bbd06e9438ab5d';
const OUT = process.argv[2]
  || 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/usb1-3d-after-persisted-refresh.png';

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
const send = (method, params = {}) => new Promise((res) => {
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

const prepared = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  const TAB = '${PCB}@${PROJECT}';
  await R.dmt_EditorControl.activateDocument(TAB);
  await new Promise(r => setTimeout(r, 400));
  const before = await R.dmt_SelectControl.getCurrentDocumentInfo();
  try {
    if (R.pcb_SelectControl && R.pcb_SelectControl.doSelectPrimitives) {
      R.pcb_SelectControl.doSelectPrimitives(['${USB1}'], TAB);
    }
  } catch (e) {}
  const api = Object.keys(R).filter(k => /3d|3D|preview|Preview/i.test(k));
  return {
    docType: before.documentType,
    tabId: before.tabId,
    api,
  };
})()`);

const threeD = await evaluate(`(() => {
  const nodes = [...document.querySelectorAll('[title],button,[aria-label]')].filter(x => x.offsetParent !== null);
  const hit = nodes.find(x => String(x.getAttribute('title') || x.getAttribute('aria-label') || '') === '3D Preview');
  if (!hit) {
    return {
      ok: false,
      titles: nodes.map(x => x.getAttribute('title') || x.getAttribute('aria-label')).filter(Boolean).slice(0, 40),
    };
  }
  hit.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  return { ok: true, tag: hit.tagName };
})()`);

await new Promise(r => setTimeout(r, 8000));

const after = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  const cur = await R.dmt_SelectControl.getCurrentDocumentInfo();
  const fit = [...document.querySelectorAll('[title]')].find(x =>
    x.offsetParent !== null && String(x.getAttribute('title') || '').startsWith('Fit Selection View'));
  if (fit) {
    fit.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  }
  const dialogs = [...document.querySelectorAll('[role="dialog"], .ant-modal, .el-dialog')]
    .filter(el => el.offsetParent !== null)
    .map(el => (el.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 160));
  return {
    docType: cur.documentType,
    tabId: cur.tabId,
    name: cur.name,
    title: cur.title,
    fitted: !!fit,
    dialogs,
  };
})()`);

await new Promise(r => setTimeout(r, after?.fitted ? 1800 : 400));

const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
if (shot.error || !shot.result?.data) throw new Error(shot.error?.message || 'no screenshot');
const buf = Buffer.from(shot.result.data, 'base64');
await writeFile(OUT, buf);
console.log(JSON.stringify({ ok: true, path: OUT, bytes: buf.length, prepared, threeD, after }, null, 2));
ws.close();
