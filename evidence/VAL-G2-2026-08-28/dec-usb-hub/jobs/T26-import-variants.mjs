import { readFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const path = process.argv[2];
const fileType = process.argv[3] === 'undef' ? null : (process.argv[3] || 'JLCEDA Pro');
const slug = process.argv[4] || 'K1-Core-Val-R0-G2-2-READABLE-CANDIDATE';
const option = process.argv[5] || 'ImportDocumentExtractLibraries';
const fileBuf = readFileSync(path);
const opts = {
  fileName: path.split('/').pop(),
  fileBase64: fileBuf.toString('base64'),
  fileMime: 'application/zip',
  fileType,
  slug,
  option,
  teamUuid: '27700277ef7a49e48a0293bece6b2993',
  friendly: 'K1-Core-Val-R0-G2.2-READABLE-CANDIDATE',
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
    operation: 'New Project',
    newProjectOwnerTeamUuid: __opts.teamUuid,
    newProjectName: __opts.slug,
    newProjectFriendlyName: __opts.friendly,
    newProjectDescription: 'G2.2 readable candidate import',
  };
  const props = __opts.option ? { importOption: __opts.option } : undefined;
  let extracted = null;
  try { extracted = await eda.sys_FileManager.extractProjectInfo(projectFile); }
  catch (e) { extracted = { error: String(e && e.message || e).slice(0, 160) }; }
  const imported = await eda.sys_FileManager.importProjectByProjectFile(
    projectFile,
    __opts.fileType || undefined,
    props,
    saveTo,
    { ownerTeamUuid: __opts.teamUuid, createDeviceForSingleSymbol: false },
  );
  const slim = imported && typeof imported === 'object' ? {
    uuid: imported.uuid,
    friendlyName: imported.friendlyName || imported.name,
    keys: Object.keys(imported).slice(0, 20),
  } : imported;
  return { extracted, imported: slim, saveTo, fileType: __opts.fileType, option: __opts.option };
}})(${JSON.stringify(opts)})`;

const fired = await send('Runtime.evaluate', {
  expression,
  returnByValue: true,
  awaitPromise: true,
  timeout: 120000,
});
ws.close();
if (fired.result?.exceptionDetails) {
  console.log(JSON.stringify({ ok: false, exception: String(fired.result.exceptionDetails.exception?.description || fired.result.exceptionDetails.text).slice(0, 400) }, null, 2));
  process.exit(1);
}
const value = fired.result?.result?.value;
console.log(JSON.stringify(value, null, 2));
if (!value?.imported?.uuid) process.exit(2);
