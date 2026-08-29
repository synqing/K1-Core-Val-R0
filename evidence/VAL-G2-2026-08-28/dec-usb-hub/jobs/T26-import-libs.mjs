import { readFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const HUB = '41c8e6523576456582ea35958b3684ed';
const G22 = 'f0f6cd233d69411ea478de1037da28fc';
const path = new URL('../anchors/hub-export-v3.epro2', import.meta.url);
const fileBuf = readFileSync(path);
const opts = {
  fileName: 'K1-Core-Val-R0-G2.1-HUB-CANDIDATE.epro2',
  fileBase64: fileBuf.toString('base64'),
  teamUuid: '27700277ef7a49e48a0293bece6b2993',
  existing: G22,
};

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const page = targets.find((t) => t.type === 'page' && String(t.url).includes(G22));
if (!page) throw new Error('no G2.2 page');
if (String(page.url).includes(LIVE) || String(page.url).includes(HUB)) throw new Error('FORBIDDEN');

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

const expression = `(${async (__opts) => {
  const eda = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda).eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== __opts.existing) return { stop: true, uuid: current && current.uuid };
  if ([LIVE, HUB].includes(current.uuid)) return { stop: true, reason: 'FORBIDDEN' };
  const binary = atob(__opts.fileBase64);
  const chunks = [];
  for (let offset = 0; offset < binary.length; offset += 0x8000) {
    const slice = binary.slice(offset, offset + 0x8000);
    const bytes = new Uint8Array(slice.length);
    for (let i = 0; i < slice.length; i += 1) bytes[i] = slice.charCodeAt(i);
    chunks.push(bytes);
  }
  const projectFile = new File(chunks, __opts.fileName, { type: 'application/zip' });
  const imported = await eda.sys_FileManager.importProjectByProjectFile(
    projectFile,
    'JLCEDA Pro',
    { importOption: 'ExtractLibraries' },
    { operation: 'Existing Project', existingProjectUuid: __opts.existing },
    { ownerTeamUuid: __opts.teamUuid, createDeviceForSingleSymbol: false },
  );
  return { importedUuid: imported && imported.uuid, importedType: imported == null ? 'null' : typeof imported };
}})(${JSON.stringify(opts)})`;

const fired = await send('Runtime.evaluate', {
  expression,
  returnByValue: true,
  awaitPromise: true,
  timeout: 180000,
});
ws.close();
if (fired.result?.exceptionDetails) {
  console.log(JSON.stringify({ ok: false, exception: String(fired.result.exceptionDetails.exception?.description).slice(0, 300) }));
  process.exit(1);
}
console.log(JSON.stringify(fired.result?.result?.value, null, 2));
