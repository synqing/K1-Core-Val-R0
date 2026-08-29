// Fire zoomTo at the new J1 (do not await the hanging promise), settle, screenshot.
import { writeFile } from 'node:fs/promises';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const OUT = '/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0/evidence/VAL-G2-2026-08-28/dec-usb-hub/screenshots/T00-j1-place.png';
const TAB = '1435cb46f39e48c8a8aadbb84ca81603@41c8e6523576456582ea35958b3684ed';

const targets = await (await fetch(`${CDP_BASE}/json/list`, { signal: AbortSignal.timeout(3000) })).json();
const page = targets.find(t => t.type === 'page' && String(t.url).includes('pro.easyeda.com'));
if (!page) throw new Error('No EasyEDA page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
ws.onmessage = ev => {
	const m = JSON.parse(ev.data);
	if (m.id && pending.has(m.id)) {
		pending.get(m.id)(m);
		pending.delete(m.id);
	}
};
await new Promise(r => { ws.onopen = r; });
const send = (method, params = {}) => new Promise(res => {
	const i = ++id;
	pending.set(i, res);
	ws.send(JSON.stringify({ id: i, method, params }));
});
await send('Page.enable');
const fired = await send('Runtime.evaluate', {
	expression: `(() => {
		const eda = globalThis._EXTAPI_ROOT_;
		const tab = ${JSON.stringify(TAB)};
		try { void eda.dmt_EditorControl.zoomTo(185, 3480, 2.5, tab); } catch (e) {}
		try { void eda.dmt_EditorControl.zoomToRegion(40, 520, 3280, 4220, tab); } catch (e) {}
		return { ok: true };
	})()`,
	returnByValue: true,
	awaitPromise: false,
});
console.log('fired', JSON.stringify(fired.result?.result?.value));
await new Promise(r => setTimeout(r, 2500));
const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
const data = shot.result?.data;
if (!data) throw new Error('no screenshot');
const buf = Buffer.from(data, 'base64');
await writeFile(OUT, buf);
console.log(JSON.stringify({ out: OUT, bytes: buf.length }));
ws.close();
