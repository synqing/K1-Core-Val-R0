// Restore hub schematic without awaiting host promises (they never settle).
const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const HUB_PROJECT = '41c8e6523576456582ea35958b3684ed';
const HUB_PAGE = '1435cb46f39e48c8a8aadbb84ca81603';

const page = (await (await fetch(`${CDP_BASE}/json/list`, { signal: AbortSignal.timeout(3000) })).json())
	.find((t) => t.type === 'page' && String(t.url).includes(HUB_PROJECT));
if (!page) throw new Error('hub window not found');
const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
ws.onmessage = (ev) => {
	const m = JSON.parse(ev.data);
	if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
};
const send = (method, params) => new Promise((resolve) => {
	const messageId = ++id;
	pending.set(messageId, resolve);
	ws.send(JSON.stringify({ id: messageId, method, params }));
});
await new Promise((r) => { ws.onopen = r; });

const fire = async (expression) => {
	const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: false });
	return r.result?.result?.value ?? { exception: r.result?.exceptionDetails?.text };
};

const fired = await fire(`(() => {
  const eda = globalThis._EXTAPI_ROOT_;
  if (!eda || !eda.dmt_EditorControl) return { ok:false, reason:'no editor' };
  try { void eda.dmt_EditorControl.openDocument("${HUB_PAGE}"); } catch (e) { return { ok:false, err:String(e&&e.message||e) }; }
  try { if (eda.dmt_EditorControl.activateDocument) void eda.dmt_EditorControl.activateDocument("${HUB_PAGE}"); } catch (e) {}
  return { ok:true, fired:true };
})()`);
await new Promise((r) => setTimeout(r, 1500));
const after = await (await fetch(`${CDP_BASE}/json/list`, { signal: AbortSignal.timeout(3000) })).json();
const url = after.find((t) => t.type === 'page' && String(t.url).includes(HUB_PROJECT))?.url || '';
console.log(JSON.stringify({ fired, url }, null, 2));
ws.close();
if (!url.includes(`*${HUB_PAGE}`) && !url.includes(`*${HUB_PAGE}@`)) {
	// *! means library tab; * without ! should be schematic
	if (url.includes(`*!`)) process.exit(2);
}
