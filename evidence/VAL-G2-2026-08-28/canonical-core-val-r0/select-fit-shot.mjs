#!/usr/bin/env node
// View-only: select primitives on live K1-Core-Val-R0, Fit Selection View, screenshot.
const { writeFile } = await import('node:fs/promises');

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
const TAB = `${PAGE}@${PROJECT}`;
const ids = String(process.argv[2] || '').split(',').map(s => s.trim()).filter(Boolean);
const outPath = process.argv[3];
if (!ids.length || !outPath) {
  console.error('usage: select-fit-shot.mjs <id,id,...> <out.png>');
  process.exit(2);
}

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
    throw new Error(reply.error?.message || reply.result.exceptionDetails.text);
  }
  return reply.result?.result?.value;
};

await send('Runtime.enable');
await send('Page.enable');
await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Escape', code: 'Escape' });
await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Escape', code: 'Escape' });
await new Promise(r => setTimeout(r, 200));

const selected = await evaluate(`(() => {
  const R = window._EXTAPI_ROOT_;
  if (!R?.sch_SelectControl?.doSelectPrimitives) return { ok: false, reason: 'sch_SelectControl absent' };
  void R.sch_SelectControl.doSelectPrimitives(${JSON.stringify(ids)}, ${JSON.stringify(TAB)});
  return { ok: true };
})()`, false);
if (!selected?.ok) throw new Error(selected?.reason || 'select fire failed');
await new Promise(r => setTimeout(r, 600));

const fit = await evaluate(`(() => {
  const e = [...document.querySelectorAll('[title]')].find(x =>
    x.offsetParent !== null && String(x.getAttribute('title') || '').startsWith('Fit Selection View'));
  if (!e) return { ok: false, reason: 'Fit Selection View not found' };
  const r = e.getBoundingClientRect();
  e.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  return { ok: true, x: r.left + r.width / 2, y: r.top + r.height / 2 };
})()`);
if (!fit?.ok) throw new Error(fit?.reason || 'fit failed');
await new Promise(r => setTimeout(r, 800));
const zooms = Number(process.env.ZOOM_IN_CLICKS || 0);
for (let i = 0; i < zooms; i++) {
  const z = await evaluate(`(() => {
    const e = [...document.querySelectorAll('[title]')].find(x =>
      x.offsetParent !== null && String(x.getAttribute('title') || '').startsWith('Zoom In'));
    if (!e) return { ok: false };
    e.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    return { ok: true };
  })()`);
  if (!z?.ok) break;
  await new Promise(r => setTimeout(r, 350));
}
await new Promise(r => setTimeout(r, 900));

const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
if (shot.error || !shot.result?.data) throw new Error(shot.error?.message || 'no screenshot');
const buf = Buffer.from(shot.result.data, 'base64');
await writeFile(outPath, buf);
console.log(JSON.stringify({ ok: true, path: outPath, bytes: buf.length, ids, selected, fit }));
ws.close();
