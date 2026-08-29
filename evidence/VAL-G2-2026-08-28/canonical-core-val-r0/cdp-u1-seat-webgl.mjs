#!/usr/bin/env node
import { writeFile } from 'node:fs/promises';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const BASE = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-seat-webgl';

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
const dumpCanvases = async (suffix) => {
  const data = await evaluate(`(() => {
    const out = [];
    const canvases = [...document.querySelectorAll('canvas')];
    for (const [i, c] of canvases.entries()) {
      const r = c.getBoundingClientRect();
      let dataUrl = null;
      if (c.width >= 400 && c.height >= 300) {
        try { dataUrl = c.toDataURL('image/png'); } catch (e) { dataUrl = 'ERR:' + (e && e.message || e); }
      }
      out.push({
        i, id: c.id, w: c.width, h: c.height, dw: r.width, dh: r.height,
        vis: c.offsetParent !== null, cls: String(c.className).slice(0, 60),
        dataUrl: dataUrl && String(dataUrl).startsWith('data:') ? dataUrl : dataUrl,
      });
    }
    return out;
  })()`);
  const saved = [];
  for (const c of data) {
    if (c.dataUrl && String(c.dataUrl).startsWith('data:image/png')) {
      const b64 = c.dataUrl.split(',')[1];
      const buf = Buffer.from(b64, 'base64');
      const path = `${BASE}-${suffix}-c${c.i}-${c.w}x${c.h}.png`;
      await writeFile(path, buf);
      saved.push({ path, bytes: buf.length, w: c.w, h: c.h, id: c.id });
    }
  }
  return {
    meta: data.map(({ dataUrl, ...rest }) => ({ ...rest, hasPng: !!(dataUrl && String(dataUrl).startsWith('data:')) })),
    saved,
  };
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
  return await R.dmt_SelectControl.getCurrentDocumentInfo();
})()`);

await evaluate(clickTitle('3D Preview'));
await new Promise(r => setTimeout(r, 12000));
await evaluate(clickTitle('Refresh'));
await new Promise(r => setTimeout(r, 8000));
await evaluate(clickTitle('Top Side'));
await new Promise(r => setTimeout(r, 1200));
const fitSel = await evaluate(`(() => {
  const hit = [...document.querySelectorAll('[title]')].find(x =>
    x.offsetParent !== null && String(x.getAttribute('title') || '').startsWith('Fit Selection'));
  if (hit) hit.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  return { ok: !!hit, title: hit && hit.getAttribute('title') };
})()`);
await new Promise(r => setTimeout(r, 1500));

const topDump = await dumpCanvases('top');
const pageTop = await send('Page.captureScreenshot', { format: 'png', fromSurface: true });
if (pageTop.result?.data) {
  await writeFile(`${BASE}-page-top.png`, Buffer.from(pageTop.result.data, 'base64'));
}

await evaluate(clickTitle('Front Side'));
await new Promise(r => setTimeout(r, 1500));
const edgeDump = await dumpCanvases('edge');

await evaluate(clickTitle('Top Side'));
await new Promise(r => setTimeout(r, 800));
console.log(JSON.stringify({
  ok: true,
  pcb,
  fitSel,
  topDump: { meta: topDump.meta, saved: topDump.saved },
  edgeDump: { meta: edgeDump.meta, saved: edgeDump.saved },
}, null, 2));
ws.close();
