// Diagnose frames and capture a parent-page zoom of new+old J1.
import { writeFile } from 'node:fs/promises';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const OUT = '/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0/evidence/VAL-G2-2026-08-28/dec-usb-hub/screenshots/T00-j1-place.png';
const TAB = '1435cb46f39e48c8a8aadbb84ca81603@41c8e6523576456582ea35958b3684ed';
const HUB = '41c8e6523576456582ea35958b3684ed';

const targets = await (await fetch(`${CDP_BASE}/json/list`, { signal: AbortSignal.timeout(3000) })).json();
const page = targets.find(t => t.type === 'page' && String(t.url).includes('pro.easyeda.com'));
if (!page) throw new Error('No EasyEDA page');
if (String(page.url).includes('64325d0e55e0435abd018defb0089a9b') && !String(page.url).includes(HUB)) {
	throw new Error('refusing live product window');
}

const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
const ctxs = [];
ws.onmessage = ev => {
	const m = JSON.parse(ev.data);
	if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
	if (m.method === 'Runtime.executionContextCreated') ctxs.push(m.params.context);
};
await new Promise(r => { ws.onopen = r; });
const send = (method, params = {}) => new Promise(res => {
	const i = ++id; pending.set(i, res);
	ws.send(JSON.stringify({ id: i, method, params }));
});
await send('Runtime.enable');
await send('Page.enable');
const tree = await send('Page.getFrameTree');
const frames = [];
(function walk(n) { if (n?.frame) frames.push({ id: n.frame.id, name: n.frame.name, url: n.frame.url }); for (const c of n.childFrames || []) walk(c); })(
	tree.result?.frameTree || tree.result);
await new Promise(r => setTimeout(r, 800));

const diag = await send('Runtime.evaluate', {
	expression: `(() => {
		const eda = globalThis._EXTAPI_ROOT_;
		const keys = eda ? Object.keys(eda).filter(k => /Editor|Document|Select|View|zoom/i.test(k)) : [];
		let zoomed = null;
		try { void eda.dmt_EditorControl.zoomToRegion(-700, 400, 3000, 4300, ${JSON.stringify(TAB)}); zoomed = 'zoomToRegion'; } catch (e) { zoomed = 'zoomFail:'+e; }
		try { void eda.sch_SelectControl.doSelectPrimitives(["ea47c20de228fa3a","e339"], ${JSON.stringify(TAB)}); } catch (e) {}
		return {
			hasEda: !!eda,
			keys,
			iframes: [...document.querySelectorAll('iframe')].map(f => ({ name: f.name, id: f.id, src: (f.src||'').slice(0,120), w: f.clientWidth, h: f.clientHeight })),
			canvases: [...document.querySelectorAll('canvas')].map(c => ({ w: c.width, h: c.height, cls: c.className, id: c.id })).slice(0, 12),
			zoomed,
			title: document.title,
			url: location.href.slice(0, 180),
		};
	})()`,
	returnByValue: true,
});

console.log(JSON.stringify({
	frames,
	ctxs: ctxs.map(c => ({ id: c.id, name: c.name, frameId: c.auxData?.frameId, origin: c.origin })),
	diag: diag.result?.result?.value,
}, null, 2));

await new Promise(r => setTimeout(r, 2500));
const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
if (!shot.result?.data) throw new Error('no screenshot');
const buf = Buffer.from(shot.result.data, 'base64');
await writeFile(OUT, buf);
console.log(JSON.stringify({ out: OUT, bytes: buf.length, width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) }));
ws.close();
