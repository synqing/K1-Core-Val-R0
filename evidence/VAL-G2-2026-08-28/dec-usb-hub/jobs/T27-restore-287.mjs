import { readFileSync, writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const HUB = '41c8e6523576456582ea35958b3684ed';
const TARGET = '54d2a25bce4b44c3af878e8b91af3554';
const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
const source = readFileSync(
  new URL('../g22/G2.2-IMPORT-RESTORE-287.source.txt', import.meta.url),
  'utf8',
);
if (!source.includes('"C1-PWR1"') || !source.includes('"RCC1S-PWR1"')) {
  throw new Error('restore source missing C1-PWR1 or RCC1S-PWR1');
}
if (source.includes('G2.2-READABLE') && !source.includes('U20-USB')) {
  throw new Error('refusing USB-less overlay');
}

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const page = targets.find((t) => t.type === 'page' && String(t.url).includes(TARGET));
if (!page) throw new Error('no import CDP page');
if (String(page.url).includes(LIVE) || String(page.url).includes(HUB)) throw new Error('LIVE_OR_HUB');

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

const opts = { source, project: TARGET, page: PAGE };
const fired = await send('Runtime.evaluate', {
  expression: `(${async (__opts) => {
    const eda = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda).eda;
    const LIVE = '64325d0e55e0435abd018defb0089a9b';
    const HUB = '41c8e6523576456582ea35958b3684ed';
    const current = await eda.dmt_Project.getCurrentProjectInfo();
    if (!current || current.uuid !== __opts.project) {
      return { stop: true, reason: 'NOT_IMPORT', uuid: current && current.uuid };
    }
    if ([LIVE, HUB].includes(current.uuid)) return { stop: true, reason: 'FORBIDDEN' };
    const before = String(await eda.sys_FileManager.getDocumentSource() || '');
    await eda.sys_FileManager.setDocumentSource(__opts.source);
    await new Promise((r) => setTimeout(r, 3500));
    const text = String(await eda.sys_FileManager.getDocumentSource() || '');
    return {
      beforeLen: before.length,
      srcLen: text.length,
      c1: text.includes('"C1-PWR1"'),
      rcc1s: text.includes('"RCC1S-PWR1"'),
      j1: text.includes('J1-PWR1'),
      j6: text.includes('J6-ESP'),
      j7: text.includes('J7'),
      u20: text.includes('U20-USB'),
      u25: text.includes('U25-USB'),
      name: current.friendlyName,
    };
  }})(${JSON.stringify(opts)})`,
  returnByValue: true,
  awaitPromise: true,
  timeout: 180000,
});
ws.close();
if (fired.result?.exceptionDetails) {
  console.log(JSON.stringify({
    ok: false,
    exception: String(fired.result.exceptionDetails.exception?.description
      || fired.result.exceptionDetails.text).slice(0, 400),
  }, null, 2));
  process.exit(1);
}
const value = fired.result?.result?.value;
writeFileSync(new URL('./T27-restore-287-result.json', import.meta.url), JSON.stringify(value, null, 2));
console.log(JSON.stringify(value, null, 2));
if (!value || value.stop || !value.c1 || !value.rcc1s || !value.u20 || value.srcLen < 2000000) {
  process.exit(2);
}
