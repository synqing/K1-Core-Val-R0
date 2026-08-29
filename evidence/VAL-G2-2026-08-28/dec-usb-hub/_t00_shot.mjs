// Zoom to the new J1 block without awaiting the hanging zoom promise, then screenshot.
import { writeFile } from 'node:fs/promises';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const OUT = process.argv[2];
const LEFT = Number(process.argv[3] ?? 40);
const RIGHT = Number(process.argv[4] ?? 480);
const TOP = Number(process.argv[5] ?? 3280);
const BOTTOM = Number(process.argv[6] ?? 4180);
const TAB = '1435cb46f39e48c8a8aadbb84ca81603@41c8e6523576456582ea35958b3684ed';
if (!OUT?.startsWith('/')) {
	console.error('usage: _t00_shot.mjs /abs.png [left right top bottom]');
	process.exit(2);
}

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
await send('Runtime.evaluate', {
	expression: `(() => {
		const root = globalThis._EXTAPI_ROOT_;
		const EC = root && root.dmt_EditorControl;
		const SCH = root && root.sch_Document;
		try { void EC.zoomToRegion(${LEFT}, ${RIGHT}, ${TOP}, ${BOTTOM}, ${JSON.stringify(TAB)}); } catch (e) {}
		try { void SCH.navigateToRegion(${LEFT}, ${TOP}, ${RIGHT - LEFT}, ${BOTTOM - TOP}); } catch (e) {}
		return { ok: true };
	})()`,
	returnByValue: true,
	awaitPromise: false,
});
await new Promise(r => setTimeout(r, 1800));
const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
const data = shot.result?.data;
if (!data) throw new Error('no screenshot data');
await writeFile(OUT, Buffer.from(data, 'base64'));
console.log(JSON.stringify({ out: OUT, bytes: Buffer.from(data, 'base64').length, region: [LEFT, RIGHT, TOP, BOTTOM] }));
ws.close();
