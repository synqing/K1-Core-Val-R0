#!/usr/bin/env node
// HOLD-only schematic screenshot from the editor parent page (iframe may be absent after save).
import { writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const HOLD = '55ed9ee948734a0e903f37744b51f3b8';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
const TAB = `${PAGE}@${HOLD}`;
const SETTLE_MS = Number(process.env.EASYEDA_SETTLE_MS || 2500);

const [outPath, mode, ...rest] = process.argv.slice(2);
if (!outPath || !['region', 'xy', 'whole'].includes(mode)) {
  console.error('usage: hold_parent_shot.mjs <out.png> whole | xy <x> <y> [zoom] | region <l> <r> <t> <b>');
  process.exit(2);
}

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const page = targets.find((t) => t.type === 'page' && String(t.url).includes(HOLD));
if (!page) throw new Error('no HOLD CDP page');
if (String(page.url).includes(LIVE)) throw new Error('refusing live product');

const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) pending.get(m.id)(m);
};
await new Promise((r) => { ws.onopen = r; });
const send = (method, params = {}) => new Promise((res) => {
  const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params }));
});
await send('Runtime.enable');
await send('Page.enable');

const evalPage = async (expression) => {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true, timeout: 60000 });
  if (r.result?.exceptionDetails) {
    throw new Error(r.result.exceptionDetails.exception?.description || r.result.exceptionDetails.text);
  }
  return r.result?.result?.value;
};
const capture = async () => {
  const s = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
  if (!s.result?.data) throw new Error('no screenshot');
  return Buffer.from(s.result.data, 'base64');
};

const before = await capture();
const fired = await evalPage(`(async () => {
  const eda = globalThis._EXTAPI_ROOT_
    || (Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda) || {}).eda;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid !== ${JSON.stringify(HOLD)}) {
    return { ok:false, reason:'WRONG_PROJECT', uuid: info && info.uuid };
  }
  if (info.uuid === ${JSON.stringify(LIVE)}) return { ok:false, reason:'LIVE' };
  const EC = eda.dmt_EditorControl;
  const tab = ${JSON.stringify(TAB)};
  const mode = ${JSON.stringify(mode)};
  try {
    if (mode === 'whole') void EC.zoomToRegion(-200, 2600, -200, 4800, tab);
    else if (mode === 'xy') void EC.zoomTo(${Number(rest[0])}, ${Number(rest[1])}, ${Number(rest[2] || 160)}, tab);
    else void EC.zoomToRegion(${Number(rest[0])}, ${Number(rest[1])}, ${Number(rest[2])}, ${Number(rest[3])}, tab);
  } catch (e) {
    return { ok:false, err: String((e && e.message) || e) };
  }
  return { ok:true, friendly: info.friendlyName, title: document.title };
})()`);
if (!fired?.ok) {
  console.log(JSON.stringify({ ok: false, fired }, null, 2));
  ws.close();
  process.exit(1);
}
await new Promise((r) => setTimeout(r, SETTLE_MS));
const after = await capture();
const h = (b) => createHash('sha256').update(b).digest('hex');
if (after.subarray(0, 8).toString('binary') !== '\x89PNG\r\n\x1a\n') throw new Error('not png');
const width = after.readUInt32BE(16);
const height = after.readUInt32BE(20);
if (width < 640 || height < 360) throw new Error(`too small ${width}x${height}`);
await writeFile(outPath, after);
console.log(JSON.stringify({
  ok: true,
  path: outPath,
  width,
  height,
  view_changed: h(before) !== h(after),
  sha256: h(after).slice(0, 16),
  mode,
  friendly: fired.friendly,
}, null, 2));
ws.close();
