const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const G22 = 'f0f6cd233d69411ea478de1037da28fc';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const PAGE = '1a0d4e1c8ed3fe8f';

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

await send('Page.enable');
const url = `https://pro.easyeda.com/editor?cll=warn#id=${G22},tab=*${PAGE}@${G22}`;
await send('Page.navigate', { url });
await new Promise((r) => setTimeout(r, 8000));
const fired = await send('Runtime.evaluate', {
  expression: `(async () => {
    const eda = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda)?.eda;
    if (!eda) return { ok: false, error: 'no sandbox after navigate' };
    const current = await eda.dmt_Project.getCurrentProjectInfo();
    let srcLen = 0;
    try { srcLen = String(await eda.sys_FileManager.getDocumentSource() || '').length; } catch (e) { srcLen = -1; }
    return { uuid: current && current.uuid, name: current && current.friendlyName, srcLen };
  })()`,
  returnByValue: true,
  awaitPromise: true,
  timeout: 30000,
});
ws.close();
console.log(JSON.stringify(fired.result?.result?.value || fired.result, null, 2));
