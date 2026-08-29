#!/usr/bin/env node
import { writeFile } from 'node:fs/promises';
const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = process.env.EASYEDA_PROJECT || '64325d0e55e0435abd018defb0089a9b';
const outPath = process.argv[2];
if (!outPath) {
  console.error('usage: cdp-screenshot.mjs <out.png>');
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
await send('Page.enable');
const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
if (shot.error || !shot.result?.data) throw new Error(shot.error?.message || 'no screenshot');
const buf = Buffer.from(shot.result.data, 'base64');
await writeFile(outPath, buf);
console.log(JSON.stringify({ ok: true, path: outPath, bytes: buf.length }));
ws.close();
