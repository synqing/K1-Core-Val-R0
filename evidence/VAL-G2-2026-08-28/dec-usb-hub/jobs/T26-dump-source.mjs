import { writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const G22 = 'f0f6cd233d69411ea478de1037da28fc';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const out = new URL('../g22/G2.2-LIVE-AFTER-LOAD.source.txt', import.meta.url);

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const page = targets.find((t) => t.type === 'page' && String(t.url).includes(G22));
if (!page) throw new Error('no G2.2 page');
if (String(page.url).includes(LIVE)) throw new Error('LIVE');

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
    const current = await eda.dmt_Project.getCurrentProjectInfo();
    const raw = await eda.sys_FileManager.getDocumentSource();
    return { uuid: current && current.uuid, source: String(raw || '') };
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
if (!value || value.uuid !== G22) {
  console.log(JSON.stringify({ ok: false, uuid: value && value.uuid }));
  process.exit(2);
}
writeFileSync(out, value.source);
const text = value.source;
const hits = {};
for (const k of ['J1', 'J6', 'J7', 'U20', 'U21', 'U22', 'U23', 'U24', 'U25', 'U20-USB']) {
  hits[k] = text.includes(k);
}
console.log(JSON.stringify({
  bytes: value.source.length,
  uuid: value.uuid,
  hits,
  out: out.pathname,
}, null, 2));
