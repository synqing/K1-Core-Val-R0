import { readFileSync, writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const HUB = '41c8e6523576456582ea35958b3684ed';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const script = process.argv[2] || './T00-open-hub-and-place.js';
const expr = readFileSync(new URL(script, import.meta.url), 'utf8');

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const pages = targets.filter((t) => t.type === 'page' && String(t.url).includes('pro.easyeda.com'));
for (const p of pages) {
  console.error('page', (p.title || '').slice(0, 80), (p.url || '').slice(0, 140));
}
const live = pages.find((t) => String(t.url).includes(LIVE));
if (live && !pages.some((t) => String(t.url).includes(HUB))) {
  console.log(JSON.stringify({ stop: true, reason: 'ONLY_LIVE_CDP_PAGE', url: live.url }));
  process.exit(2);
}
const page = pages.find((t) => String(t.url).includes(HUB)) || pages[0];
if (!page) throw new Error('no EasyEDA page');

const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    pending.get(m.id)(m);
    pending.delete(m.id);
  }
};
await new Promise((r) => { ws.onopen = r; });
const send = (method, params) => new Promise((res) => {
  const i = ++id;
  pending.set(i, res);
  ws.send(JSON.stringify({ id: i, method, params }));
});

const fired = await send('Runtime.evaluate', {
  expression: expr,
  returnByValue: true,
  awaitPromise: true,
  timeout: 180000,
});
if (fired.result?.exceptionDetails) {
  const desc = fired.result.exceptionDetails.exception?.description
    || fired.result.exceptionDetails.text;
  writeFileSync(new URL('./T00-open-hub-and-place-result.json', import.meta.url), JSON.stringify({ ok: false, exception: desc }, null, 2));
  console.log(JSON.stringify({ ok: false, exception: String(desc).slice(0, 500) }, null, 2));
  ws.close();
  process.exit(1);
}
const value = fired.result?.result?.value ?? fired.result;
writeFileSync(new URL('./T00-open-hub-and-place-result.json', import.meta.url), JSON.stringify(value, null, 2));
console.log(JSON.stringify(value, null, 2));
ws.close();
if (value && value.stop) process.exit(2);
