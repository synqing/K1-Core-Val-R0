import { writeFileSync } from 'node:fs';
import { readFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const HUB = '41c8e6523576456582ea35958b3684ed';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
const outPath = process.argv[2];
if (!outPath) throw new Error('usage: T00-dump-snapshot.mjs <snapshot.json>');

function sourceHash(source) {
  let hash = 2166136261;
  for (let i = 0; i < source.length; i += 1) {
    hash ^= source.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return source.length + ':' + (hash >>> 0).toString(16).padStart(8, '0');
}

const expr = `(() => (async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = ${JSON.stringify(HUB)};
  const LIVE = ${JSON.stringify(LIVE)};
  const PAGE = ${JSON.stringify(PAGE)};
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE) return { stop: true, reason: info && info.uuid === LIVE ? 'LIVE' : 'NO_PROJ', uuid: info && info.uuid };
  if (info.uuid !== HUB) return { stop: true, reason: 'WRONG', uuid: info.uuid };
  await eda.dmt_EditorControl.openDocument(PAGE);
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  const source = await eda.sys_FileManager.getDocumentSource();
  if (typeof source !== 'string' || source.includes('"docType":"SYMBOL"')) {
    return { stop: true, reason: 'BAD_SOURCE', hint: typeof source };
  }
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  const interesting = [];
  for (const id of ids || []) {
    try {
      const c = await eda.sch_PrimitiveComponent.get(id);
      const st = c && (c.getState ? c.getState() : c);
      const des = String((st && st.designator) || '');
      const name = String((st && (st.name || st.deviceName)) || '');
      if (des.includes('J1') || des === 'U?' || name.includes('7005') || name.includes('USB4105') || id === 'e339' || id === 'ea47c20de228fa3a') {
        interesting.push({ id, designator: des, name, x: st && st.x, y: st && st.y });
      }
    } catch (e) { /* skip */ }
  }
  return {
    proj: info.uuid,
    friendly: info.friendlyName,
    source,
    components: (ids || []).length,
    wires: (wires || []).length,
    interesting,
  };
})())()`;

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const pages = targets.filter((t) => t.type === 'page' && String(t.url).includes('pro.easyeda.com'));
for (const p of pages) console.error('page', (p.title || '').slice(0, 80), (p.url || '').slice(0, 140));
if (pages.some((t) => String(t.url).includes(LIVE)) && !pages.some((t) => String(t.url).includes(HUB))) {
  console.log(JSON.stringify({ stop: true, reason: 'ONLY_LIVE_CDP_PAGE' }));
  process.exit(2);
}
const page = pages.find((t) => String(t.url).includes(HUB));
if (!page) throw new Error('no hub CDP page');

const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) pending.get(m.id)(m);
};
await new Promise((r) => { ws.onopen = r; });
const send = (method, params) => new Promise((res) => {
  const i = ++id; pending.set(i, res);
  ws.send(JSON.stringify({ id: i, method, params }));
});
const fired = await send('Runtime.evaluate', {
  expression: expr,
  returnByValue: true,
  awaitPromise: true,
  timeout: 180000,
});
if (fired.result?.exceptionDetails) {
  console.log(JSON.stringify({ ok: false, exception: fired.result.exceptionDetails.exception?.description || fired.result.exceptionDetails.text }, null, 2));
  ws.close();
  process.exit(1);
}
const value = fired.result?.result?.value;
ws.close();
if (!value || value.stop) {
  console.log(JSON.stringify(value || { ok: false }, null, 2));
  process.exit(2);
}
const hash = sourceHash(value.source);
const snap = {
  schema_version: 1,
  project_uuid: HUB,
  document_uuid: PAGE,
  source: value.source,
  source_hash: hash,
  census: { characters: value.source.length, components: value.components, wires: value.wires },
  note: 'Hub schematic snapshot before next hub-lane mutation. Live 64325d0e not in this file.',
};
writeFileSync(outPath, JSON.stringify(snap));
console.log(JSON.stringify({
  ok: true,
  path: outPath,
  source_hash: hash,
  proj: value.proj,
  friendly: value.friendly,
  components: value.components,
  wires: value.wires,
  interesting: value.interesting,
}, null, 2));
