#!/usr/bin/env node
import { writeFile } from 'node:fs/promises';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const BASE = 'evidence/VAL-G2-2026-08-28/canonical-core-val-r0/u1-gtusb-3d-after-bind';

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

await send('Runtime.enable');
await send('Page.enable');

const views = ['Front Side', 'Top Side'];
const results = [];
for (const view of views) {
  const clicked = await evaluate(clickTitle(view));
  await new Promise(r => setTimeout(r, 1200));
  const fit = await evaluate(clickTitle('Fit All in Window'));
  await new Promise(r => setTimeout(r, 1800));
  const slug = view.toLowerCase().replace(/\s+/g, '-');
  const path = `${BASE}-${slug}.png`;
  const bytes = await shot(path);
  results.push({ view, clicked, fit, path, bytes });
}

console.log(JSON.stringify({ ok: true, results }, null, 2));
ws.close();
