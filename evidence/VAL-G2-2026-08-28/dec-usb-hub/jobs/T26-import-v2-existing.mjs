import { readFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const HUB = '41c8e6523576456582ea35958b3684ed';
const ORACLE = 'dcd7e3cab2a24b9aa6e531d2b62e1b6f';
const HUSK = 'f0f6cd233d69411ea478de1037da28fc';
const path = process.argv[2]
  || new URL('../g22/K1-Core-Val-R0-G2.2-from-hub-v2.epro', import.meta.url).pathname;
const mode = process.argv[3] || 'existing';
const uniqueName = process.argv[4] || 'K1-Core-Val-R0-G2.2-READABLE-IMPORT';
const fileBuf = readFileSync(path);
const opts = {
  fileName: path.split('/').pop(),
  fileBase64: fileBuf.toString('base64'),
  fileMime: 'application/zip',
  teamUuid: '27700277ef7a49e48a0293bece6b2993',
  existing: HUSK,
  mode,
  uniqueName,
  uniqueSlug: uniqueName.replace(/[^A-Za-z0-9_-]+/g, '-').slice(0, 80),
};

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const page = targets.find((t) => t.type === 'page' && String(t.url).includes(HUSK))
  || targets.find((t) => t.type === 'page' && String(t.url).includes('pro.easyeda.com') && !String(t.url).includes(LIVE));
if (!page) throw new Error('no EasyEDA page');
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

const expression = `(${async (__opts) => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  if (!sandbox) return { ok: false, error: 'no sandbox' };
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const ORACLE = 'dcd7e3cab2a24b9aa6e531d2b62e1b6f';
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
  let extracted = null;
  try { extracted = await eda.sys_FileManager.extractProjectInfo(projectFile); }
  catch (e) { extracted = { error: String(e && e.message || e).slice(0, 160) }; }
  const saveTo = __opts.mode === 'new'
    ? {
      operation: 'New Project',
      newProjectOwnerTeamUuid: __opts.teamUuid,
      newProjectName: __opts.uniqueSlug,
      newProjectFriendlyName: __opts.uniqueName,
      newProjectDescription: 'G2.2 V2 pack import disposable',
    }
    : {
      operation: 'Existing Project',
      existingProjectUuid: __opts.existing,
    };
  if (__opts.mode === 'existing' && [LIVE, HUB, ORACLE].includes(__opts.existing)) {
    return { stop: true, reason: 'FORBIDDEN_TARGET' };
  }
  const imported = await eda.sys_FileManager.importProjectByProjectFile(
    projectFile,
    'JLCEDA Pro',
    undefined,
    saveTo,
    { ownerTeamUuid: __opts.teamUuid, createDeviceForSingleSymbol: false },
  );
  await new Promise((r) => setTimeout(r, 2500));
  const afterUuid = (imported && imported.uuid) || (__opts.mode === 'existing' ? __opts.existing : null);
  let after = null;
  if (afterUuid) {
    try { after = await eda.dmt_Project.getProjectInfo(afterUuid); }
    catch (e) { after = { err: String(e && e.message || e).slice(0, 160) }; }
  }
  const boards = (after && after.data) || [];
  const inventory = boards.map((b) => ({
    name: b.name || b.title,
    sch: b.schematic && b.schematic.uuid,
    pages: ((b.schematic && b.schematic.page) || []).map((p) => p.uuid),
    pcb: b.pcb && b.pcb.uuid,
  }));
  return {
    extractedOk: !!(extracted && !extracted.error),
    extractedTitle: extracted && (extracted.title || extracted.friendlyName || extracted.name),
    importedNull: imported == null,
    importedUuid: imported && imported.uuid,
    importedName: imported && (imported.friendlyName || imported.name),
    afterUuid: after && after.uuid,
    afterName: after && after.friendlyName,
    inventory,
    currentUuid: current && current.uuid,
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
  console.log(JSON.stringify({
    ok: false,
    exception: String(fired.result.exceptionDetails.exception?.description
      || fired.result.exceptionDetails.text).slice(0, 400),
  }, null, 2));
  process.exit(1);
}
const value = fired.result?.result?.value;
console.log(JSON.stringify(value, null, 2));
if (!value || value.stop || (value.importedNull && value.mode !== 'existing')) process.exit(2);
