import { readFileSync, writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const HUB = '41c8e6523576456582ea35958b3684ed';
const G22 = 'f0f6cd233d69411ea478de1037da28fc';
const PAGE = '1a0d4e1c8ed3fe8f';
const SCH = 'cffcdb562c1b48d1a5214cfc263b6c90';
const OLD = '1435cb46f39e48c8a8aadbb84ca81603';

let source = readFileSync(
  new URL('../g22/G2.2-READABLE.source.txt', import.meta.url),
  'utf8',
);
if (!source.includes(OLD)) throw new Error('G2.2 source missing archive page uuid');
source = source.replace(OLD, PAGE);
if (!source.includes('"type":"META"')) {
  const lines = source.split('\n');
  const meta = `{"type":"META","ticket":230,"id":"META"}||{"title":"P1","schematic":"${SCH}","zIndex":1}|`;
  lines.splice(1, 0, meta);
  source = lines.join('\n');
}
if (!source.endsWith('\n')) source += '\n';

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const page = targets.find((t) => t.type === 'page' && String(t.url).includes(G22));
if (!page) throw new Error('no G2.2 CDP page');
if (String(page.url).includes(LIVE) || String(page.url).includes(HUB)) {
  throw new Error('refusing live/hub');
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

const opts = { source, page: PAGE, project: G22 };
const expression = `(${async (__opts) => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  if (!sandbox) return { ok: false, error: 'no sandbox' };
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== __opts.project) {
    return { stop: true, reason: 'NOT_G22', uuid: current && current.uuid };
  }
  if ([LIVE, HUB].includes(current.uuid)) return { stop: true, reason: 'FORBIDDEN' };
  const pages = ((((current.data || [])[0] || {}).schematic || {}).page || []).map((p) => p.uuid);
  if (!pages.includes(__opts.page)) {
    return { stop: true, reason: 'PAGE_NOT_OPEN', pages };
  }
  const setResult = await eda.sys_FileManager.setDocumentSource(__opts.source);
  await new Promise((r) => setTimeout(r, 2500));
  const raw = await eda.sys_FileManager.getDocumentSource();
  const text = String(raw || '');
  return {
    setResult: setResult == null ? null : (typeof setResult === 'object' ? Object.keys(setResult) : typeof setResult),
    srcLen: text.length,
    j1: text.includes('J1'),
    j6: text.includes('J6'),
    j7: text.includes('J7'),
    u20: text.includes('U20'),
    u25: text.includes('U25'),
    pageUuid: text.includes(__opts.page),
    currentUuid: current.uuid,
  };
}})(${JSON.stringify(opts)})`;

const fired = await send('Runtime.evaluate', {
  expression,
  returnByValue: true,
  awaitPromise: true,
  timeout: 180000,
});
ws.close();
if (fired.result?.exceptionDetails) {
  const desc = fired.result.exceptionDetails.exception?.description || fired.result.exceptionDetails.text;
  console.log(JSON.stringify({ ok: false, exception: String(desc).slice(0, 500) }, null, 2));
  process.exit(1);
}
const value = fired.result?.result?.value;
writeFileSync(new URL('./T26-load-g22-result.json', import.meta.url), JSON.stringify(value, null, 2));
console.log(JSON.stringify(value, null, 2));
if (!value || value.stop || !value.j1) process.exit(2);
