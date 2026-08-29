import { readFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const HUB = '41c8e6523576456582ea35958b3684ed';
const TARGET = '54d2a25bce4b44c3af878e8b91af3554';
const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
const source = readFileSync(new URL('../g22/G2.2-IMPORT-OPEN.source.txt', import.meta.url), 'utf8');
if (source.length < 2000000) throw new Error(`restore source too small: ${source.length}`);

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
    if (!current || current.uuid !== __opts.project) return { stop: true, reason: 'NOT_IMPORT', uuid: current && current.uuid };
    if ([LIVE, HUB].includes(current.uuid)) return { stop: true, reason: 'FORBIDDEN' };
    await eda.sys_FileManager.setDocumentSource(__opts.source);
    await new Promise((r) => setTimeout(r, 3000));
    const text = String(await eda.sys_FileManager.getDocumentSource() || '');
    return {
      srcLen: text.length,
      j1: text.includes('J1'),
      j6: text.includes('J6'),
      j7: text.includes('J7'),
      u20: text.includes('U20'),
      u25: text.includes('U25'),
      name: current.friendlyName,
    };
  }})(${JSON.stringify(opts)})`,
  returnByValue: true,
  awaitPromise: true,
  timeout: 180000,
});
ws.close();
const value = fired.result?.result?.value;
console.log(JSON.stringify(value || fired.result, null, 2));
if (!value || value.srcLen < 2000000 || !value.u20) process.exit(2);
