import { readFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const HUB = '41c8e6523576456582ea35958b3684ed';
const ORACLE = 'dcd7e3cab2a24b9aa6e531d2b62e1b6f';
const HUSK = 'f0f6cd233d69411ea478de1037da28fc';
const path = process.argv[2];
const fileBuf = readFileSync(path);
const opts = {
  fileName: path.split('/').pop(),
  fileBase64: fileBuf.toString('base64'),
  fileMime: 'application/zip',
  teamUuid: '27700277ef7a49e48a0293bece6b2993',
  existing: HUSK,
};

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const page = targets.find((t) => t.type === 'page' && String(t.url).includes('pro.easyeda.com'));
if (!page) throw new Error('no EasyEDA page');
if (String(page.url).includes(LIVE)) throw new Error('LIVE_FOCUSED');

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
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  if (!sandbox) return { ok: false, error: 'no sandbox' };
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const ORACLE = 'dcd7e3cab2a24b9aa6e531d2b62e1b6f';
  if ([LIVE, HUB, ORACLE].includes(__opts.existing)) {
    return { stop: true, reason: 'FORBIDDEN_TARGET' };
  }
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (current && [LIVE, HUB, ORACLE].includes(current.uuid)) {
    return { stop: true, reason: 'FORBIDDEN_CURRENT', uuid: current.uuid };
  }
  const binary = atob(__opts.fileBase64);
  const chunks = [];
  for (let offset = 0; offset < binary.length; offset += 0x8000) {
    const slice = binary.slice(offset, offset + 0x8000);
    const bytes = new Uint8Array(slice.length);
    for (let i = 0; i < slice.length; i += 1) bytes[i] = slice.charCodeAt(i);
    chunks.push(bytes);
  }
  const projectFile = new File(chunks, __opts.fileName, { type: __opts.fileMime });
  const saveTo = {
    operation: 'Existing Project',
    existingProjectUuid: __opts.existing,
  };
  const imported = await eda.sys_FileManager.importProjectByProjectFile(
    projectFile,
    'JLCEDA Pro',
    { importOption: 'ImportDocumentExtractLibraries' },
    saveTo,
    { ownerTeamUuid: __opts.teamUuid, createDeviceForSingleSymbol: false },
  );
  await new Promise((r) => setTimeout(r, 3000));
  const after = await eda.dmt_Project.getProjectInfo(__opts.existing);
  const cur = await eda.dmt_Project.getCurrentProjectInfo();
  const pages = ((((after.data || [])[0] || {}).schematic || {}).page || []).map((p) => p.uuid);
  const curPages = ((((cur.data || [])[0] || {}).schematic || {}).page || []).map((p) => ({ uuid: p.uuid, name: p.name }));
  return {
    importedType: imported == null ? 'null' : typeof imported,
    importedUuid: imported && imported.uuid,
    afterFriendly: after && after.friendlyName,
    afterUuid: after && after.uuid,
    afterPages: pages,
    currentUuid: cur && cur.uuid,
    currentPages: curPages,
    forbidden: {
      isLive: cur && cur.uuid === LIVE,
      isHub: cur && cur.uuid === HUB,
    },
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
  console.log(JSON.stringify({ ok: false, exception: String(fired.result.exceptionDetails.exception?.description || fired.result.exceptionDetails.text).slice(0, 400) }, null, 2));
  process.exit(1);
}
console.log(JSON.stringify(fired.result?.result?.value, null, 2));
