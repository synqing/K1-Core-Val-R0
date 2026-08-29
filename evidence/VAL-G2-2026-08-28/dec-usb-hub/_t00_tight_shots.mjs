import { writeFile } from 'node:fs/promises';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const TAB = '1435cb46f39e48c8a8aadbb84ca81603@41c8e6523576456582ea35958b3684ed';
const HUB = '41c8e6523576456582ea35958b3684ed';
const BASE = '/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0/evidence/VAL-G2-2026-08-28/dec-usb-hub/screenshots';

const targets = await (await fetch(`${CDP_BASE}/json/list`, { signal: AbortSignal.timeout(3000) })).json();
const page = targets.find(t => t.type === 'page' && String(t.url).includes('pro.easyeda.com'));
if (!page) throw new Error('No EasyEDA page');
if (String(page.url).includes('64325d0e55e0435abd018defb0089a9b') && !String(page.url).includes(HUB)) {
	throw new Error('refusing live product window');
}

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
const capture = async (path) => {
	const s = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
	if (!s.result?.data) throw new Error('no screenshot');
	const buf = Buffer.from(s.result.data, 'base64');
	await writeFile(path, buf);
	return { path, width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
};

await evalPage(`(() => {
	const eda = globalThis._EXTAPI_ROOT_;
	const tab = ${JSON.stringify(TAB)};
	try { eda.sch_SelectControl.doSelectPrimitives(["ea47c20de228fa3a"], tab); } catch (e) {}
	try { void eda.dmt_EditorControl.zoomTo(-400, 3360, 140, tab); } catch (e) {}
	return true;
})()`);
await new Promise(r => setTimeout(r, 2200));
const a = await capture(`${BASE}/T00-j1-new-tight.png`);

await evalPage(`(() => {
	const eda = globalThis._EXTAPI_ROOT_;
	const tab = ${JSON.stringify(TAB)};
	try { eda.sch_SelectControl.doSelectPrimitives(["e339"], tab); } catch (e) {}
	try { void eda.dmt_EditorControl.zoomTo(185, 4095, 140, tab); } catch (e) {}
	return true;
})()`);
await new Promise(r => setTimeout(r, 2200));
const b = await capture(`${BASE}/T00-j1-old-tight.png`);

console.log(JSON.stringify({ a, b }, null, 2));
ws.close();
