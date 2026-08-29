import { writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const OUT = process.argv[2] || '/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0/evidence/VAL-G2-2026-08-28/dec-usb-hub/screenshots/T00-j1-place-block.png';
const TAB = '1435cb46f39e48c8a8aadbb84ca81603@41c8e6523576456582ea35958b3684ed';
const HUB = '41c8e6523576456582ea35958b3684ed';
const IDS = ['ea47c20de228fa3a', 'e339'];

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

const evalPage = async (expression, awaitPromise = false) => {
	const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise });
	if (r.result?.exceptionDetails) {
		throw new Error(r.result.exceptionDetails.exception?.description || r.result.exceptionDetails.text);
	}
	return r.result?.result?.value;
};

const zoomPct = () => evalPage(`(() => {
	const texts = [...document.querySelectorAll('span,div,button')].map(e => (e.textContent||'').trim()).filter(t => /^\\d+(\\.\\d+)?%$/.test(t));
	return { zoomCandidates: [...new Set(texts)].slice(0, 12) };
})()`);

const capture = async () => {
	const s = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
	if (!s.result?.data) throw new Error('no screenshot');
	return Buffer.from(s.result.data, 'base64');
};

const beforePct = await zoomPct();
const before = await capture();

const fired = await evalPage(`(() => {
	const eda = globalThis._EXTAPI_ROOT_;
	const tab = ${JSON.stringify(TAB)};
	const ids = ${JSON.stringify(IDS)};
	const log = [];
	try { eda.sch_SelectControl.doSelectPrimitives(ids, tab); log.push('selected'); } catch (e) { log.push('select:'+e); }
	try { void eda.dmt_EditorControl.zoomToSelectedPrimitives(tab); log.push('zoomToSelected'); } catch (e) { log.push('zsel:'+e); }
	try { void eda.dmt_EditorControl.zoomTo(-400, 3400, 8, tab); log.push('zoomTo8'); } catch (e) { log.push('zto:'+e); }
	try { void eda.sch_Document.navigateToRegion(-700, 2700, 400, 4200); log.push('navRegion'); } catch (e) { log.push('nav:'+e); }
	try { void eda.sch_Document.navigateToCoordinates(-400, 3400); log.push('navCoord'); } catch (e) { log.push('navc:'+e); }
	return { log };
})()`);

await new Promise(r => setTimeout(r, 2800));
const afterPct = await zoomPct();
const after = await capture();
const h = b => createHash('sha256').update(b).digest('hex');
const moved = h(before) !== h(after);
await writeFile(OUT, after);
console.log(JSON.stringify({
	ok: moved,
	path: OUT,
	width: after.readUInt32BE(16),
	height: after.readUInt32BE(20),
	view_changed: moved,
	sha_before: h(before).slice(0, 16),
	sha_after: h(after).slice(0, 16),
	beforePct,
	afterPct,
	fired,
}, null, 2));
ws.close();
if (!moved) process.exit(1);
