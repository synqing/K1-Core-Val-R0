import { readFileSync, writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const G22 = 'f0f6cd233d69411ea478de1037da28fc';
const IMPORT = '54d2a25bce4b44c3af878e8b91af3554';
const HUB = '41c8e6523576456582ea35958b3684ed';
const script = process.argv[2] || './T26-open-g22.js';
const expr = readFileSync(new URL(script, import.meta.url), 'utf8');

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const pages = targets.filter((t) => t.type === 'page' && String(t.url).includes('pro.easyeda.com'));
for (const p of pages) {
  console.error('page', (p.title || '').slice(0, 80), (p.url || '').slice(0, 140));
}
if (pages.some((t) => String(t.url).includes(LIVE)) && pages.every((t) => String(t.url).includes(LIVE))) {
  console.log(JSON.stringify({ stop: true, reason: 'ONLY_LIVE_CDP_PAGE' }));
  process.exit(2);
}
const page = pages.find((t) => String(t.url).includes(IMPORT))
  || pages.find((t) => String(t.url).includes(G22))
  || pages.find((t) => !String(t.url).includes(LIVE) && !String(t.url).includes(HUB))
  || pages[0];
if (!page) throw new Error('no EasyEDA page');
if (String(page.url).includes(LIVE) || String(page.url).includes(HUB)) {
  console.log(JSON.stringify({ stop: true, reason: 'WOULD_EVAL_LIVE_OR_HUB' }));
  process.exit(2);
}

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
  console.log(JSON.stringify({ ok: false, exception: String(desc).slice(0, 500) }, null, 2));
  ws.close();
  process.exit(1);
}
const value = fired.result?.result?.value ?? fired.result;
if (value && typeof value.source === 'string' && value.source.length) {
  const dumpPath = new URL('../g22/G2.2-IMPORT-OPEN.source.txt', import.meta.url);
  writeFileSync(dumpPath, value.source);
  const slim = { ...value, source: undefined, sourceWrote: dumpPath.pathname, sourceLen: value.source.length };
  writeFileSync(new URL('./T26-open-g22-result.json', import.meta.url), JSON.stringify(slim, null, 2));
  console.log(JSON.stringify(slim, null, 2));
} else {
  writeFileSync(new URL('./T26-open-g22-result.json', import.meta.url), JSON.stringify(value, null, 2));
  console.log(JSON.stringify(value, null, 2));
}
ws.close();
if (value && value.stop) process.exit(2);
