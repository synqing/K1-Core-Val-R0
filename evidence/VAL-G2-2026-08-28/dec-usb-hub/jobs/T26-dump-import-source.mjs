import { writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const TARGET = process.env.EASYEDA_PROJECT || '54d2a25bce4b44c3af878e8b91af3554';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const HUB = '41c8e6523576456582ea35958b3684ed';
const out = new URL(process.env.EASYEDA_DUMP_OUT || '../g22/G2.2-IMPORT-OPEN.source.txt', import.meta.url);

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const page = targets.find((t) => t.type === 'page' && String(t.url).includes(TARGET));
if (!page) throw new Error('no target page');
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

const fired = await send('Runtime.evaluate', {
  expression: `(async () => {
    const eda = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda).eda;
    const LIVE = '64325d0e55e0435abd018defb0089a9b';
    const HUB = '41c8e6523576456582ea35958b3684ed';
    const current = await eda.dmt_Project.getCurrentProjectInfo();
    if (!current || [LIVE, HUB].includes(current.uuid)) return { stop: true, uuid: current && current.uuid };
    const raw = await eda.sys_FileManager.getDocumentSource();
    return { uuid: current.uuid, name: current.friendlyName, source: String(raw || '') };
  })()`,
  returnByValue: true,
  awaitPromise: true,
  timeout: 60000,
});
ws.close();
if (fired.result?.exceptionDetails) {
  console.log(JSON.stringify({ ok: false, exception: String(fired.result.exceptionDetails.exception?.description).slice(0, 300) }));
  process.exit(1);
}
const value = fired.result?.result?.value;
if (!value || value.stop || value.uuid !== TARGET) {
  console.log(JSON.stringify({ ok: false, uuid: value && value.uuid }));
  process.exit(2);
}
writeFileSync(out, value.source);
const text = value.source;
const hits = {};
for (const k of ['J1', 'J6', 'J7', 'U20', 'U21', 'U22', 'U23', 'U24', 'U25', 'J1-PWR1', 'J6-ESP', 'KILL']) {
  hits[k] = text.includes(k);
}
console.log(JSON.stringify({
  bytes: value.source.length,
  uuid: value.uuid,
  name: value.name,
  hits,
  out: out.pathname,
}, null, 2));
