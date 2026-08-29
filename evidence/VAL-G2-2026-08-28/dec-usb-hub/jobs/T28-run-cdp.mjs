import { readFileSync, writeFileSync, existsSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const HUB = '41c8e6523576456582ea35958b3684ed';
const ORACLE = 'dcd7e3cab2a24b9aa6e531d2b62e1b6f';
const SCAR = '54d2a25bce4b44c3af878e8b91af3554';
const HUSK = 'f0f6cd233d69411ea478de1037da28fc';

const script = process.argv[2] || './T28-inventory.js';
const dumpOut = process.env.EASYEDA_DUMP_OUT || '';
const targetFile = new URL('./T28-target.json', import.meta.url);
const targetMeta = existsSync(targetFile) ? JSON.parse(readFileSync(targetFile, 'utf8')) : {};
const prefer = process.env.EASYEDA_PROJECT || targetMeta.uuid || '';

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const pages = targets.filter((t) => t.type === 'page' && String(t.url).includes('pro.easyeda.com'));
for (const p of pages) {
  console.error('page', (p.title || '').slice(0, 80), (p.url || '').slice(0, 160));
}
if (!pages.length) throw new Error('no EasyEDA page');
if (pages.every((t) => String(t.url).includes(LIVE))) {
  console.log(JSON.stringify({ stop: true, reason: 'ONLY_LIVE_CDP_PAGE' }));
  process.exit(2);
}

const page = (prefer && pages.find((t) => String(t.url).includes(prefer)))
  || pages.find((t) => !String(t.url).includes(LIVE)
    && !String(t.url).includes(HUB)
    && !String(t.url).includes(ORACLE))
  || pages.find((t) => String(t.url).includes(SCAR))
  || pages.find((t) => String(t.url).includes(HUSK));
if (!page) throw new Error('no safe EasyEDA page');
if (String(page.url).includes(LIVE) || String(page.url).includes(HUB) || String(page.url).includes(ORACLE)) {
  console.log(JSON.stringify({ stop: true, reason: 'WOULD_EVAL_FORBIDDEN' }));
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

const expr = readFileSync(new URL(script, import.meta.url), 'utf8');
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
if (value && typeof value.source === 'string' && value.source.length && dumpOut) {
  writeFileSync(dumpOut, value.source);
  const slim = { ...value, source: undefined, sourceWrote: dumpOut, sourceLen: value.source.length };
  console.log(JSON.stringify(slim, null, 2));
} else {
  console.log(JSON.stringify(value, null, 2));
}
ws.close();
if (value && value.stop) process.exit(2);
