#!/usr/bin/env node
const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const page = targets.find(t => t.type === 'page' && String(t.url).includes(PROJECT));
if (!page) throw new Error('no page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
const ctxs = [];
ws.onmessage = ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  if (m.method === 'Runtime.executionContextCreated') ctxs.push(m.params.context);
};
await new Promise(r => { ws.onopen = r; });
const send = (method, params = {}) => new Promise(res => {
  const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params }));
});
await send('Runtime.enable');
await send('Page.enable');
const tree = await send('Page.getFrameTree');
const frames = [];
(function walk(n) { if (n?.frame) frames.push(n.frame); for (const c of n.childFrames || []) walk(c); })(tree.result?.frameTree || tree.result);
await new Promise(r => setTimeout(r, 1500));
const out = frames.map(f => ({
  id: f.id,
  name: f.name,
  url: String(f.url || '').slice(0, 120),
  ctx: (ctxs.find(c => c.auxData?.frameId === f.id) || {}).id,
}));
console.log(JSON.stringify({ url: page.url, frames: out, ctxCount: ctxs.length }, null, 2));
ws.close();
