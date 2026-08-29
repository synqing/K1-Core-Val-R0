import { writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const TAB = '1435cb46f39e48c8a8aadbb84ca81603@41c8e6523576456582ea35958b3684ed';
const HUB = '41c8e6523576456582ea35958b3684ed';
const OUT = process.env.SHOT_OUT || '/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0/evidence/VAL-G2-2026-08-28/dec-usb-hub/screenshots/T07-vbus-det-tight.png';

const targets = await (await fetch(`${CDP_BASE}/json/list`, { signal: AbortSignal.timeout(3000) })).json();
const page = targets.find(t => t.type === 'page' && String(t.url).includes('pro.easyeda.com'));
if (!page) throw new Error('No EasyEDA page');
if (String(page.url).includes('64325d0e55e0435abd018defb0089a9b') && !String(page.url).includes(HUB)) {
	throw new Error('refusing live product window');
}
if (!String(page.url).includes(HUB)) throw new Error('not hub: ' + page.url);

const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
ws.onmessage = ev => {
	const m = JSON.parse(ev.data);
	if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
};
await new Promise(r => { ws.onopen = r; });
const send = (method, params = {}) => new Promise(res => {
	const i = ++id; pending.set(i, res);
	ws.send(JSON.stringify({ id: i, method, params }));
});
await send('Runtime.enable');
await send('Page.enable');
const evalPage = async (expression) => {
	const r = await send('Runtime.evaluate', { expression, returnByValue: true });
	if (r.result?.exceptionDetails) {
		throw new Error(r.result.exceptionDetails.exception?.description || r.result.exceptionDetails.text);
	}
	return r.result?.result?.value;
};
const capture = async () => {
	const s = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
	if (!s.result?.data) throw new Error('no screenshot');
	return Buffer.from(s.result.data, 'base64');
};
const h = b => createHash('sha256').update(b).digest('hex');
const before = await capture();
const fired = await evalPage(`(() => {
	const eda = globalThis._EXTAPI_ROOT_;
	const tab = ${JSON.stringify(TAB)};
	try { eda.sch_SelectControl.doSelectPrimitives(["a60d36245cbf4e86","d7ed808dd32d71fa","f6a62bb1e7d23ff6","92edd0bd8901c171"], tab); } catch (e) {}
	try { void eda.dmt_EditorControl.zoomTo(380, 880, 140, tab); } catch (e) {}
	return { ok: true };
})()`);
await new Promise(r => setTimeout(r, 2200));
const after = await capture();
await writeFile(OUT, after);
const moved = h(before) !== h(after);
console.log(JSON.stringify({
	ok: moved, path: OUT, width: after.readUInt32BE(16), height: after.readUInt32BE(20),
	view_changed: moved, sha: h(after).slice(0, 16), fired,
}, null, 2));
ws.close();
if (!moved) process.exit(1);
