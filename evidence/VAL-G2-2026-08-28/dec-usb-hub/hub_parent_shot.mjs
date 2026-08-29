#!/usr/bin/env node
import { writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const TAB = '1435cb46f39e48c8a8aadbb84ca81603@41c8e6523576456582ea35958b3684ed';
const HUB = '41c8e6523576456582ea35958b3684ed';
const LIVE = '64325d0e55e0435abd018defb0089a9b';

const [outPath, mode, ...rest] = process.argv.slice(2);
if (!outPath || !['select', 'xy', 'region'].includes(mode)) {
	console.error('usage: hub_parent_shot.mjs <out.png> select <id,id,...> [zoomPct]');
	console.error('       hub_parent_shot.mjs <out.png> xy <x> <y> [zoomPct]');
	process.exit(2);
}

const targets = await (await fetch(`${CDP_BASE}/json/list`, { signal: AbortSignal.timeout(3000) })).json();
const page = targets.find(t => t.type === 'page' && String(t.url).includes('pro.easyeda.com'));
if (!page) throw new Error('No EasyEDA page');
if (String(page.url).includes(LIVE) && !String(page.url).includes(HUB)) {
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
const capture = async () => {
	const s = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
	if (!s.result?.data) throw new Error('no screenshot');
	return Buffer.from(s.result.data, 'base64');
};

let js;
if (mode === 'select') {
	const ids = String(rest[0] || '').split(',').map(s => s.trim()).filter(Boolean);
	const zoom = Number(rest[1] || 120);
	js = `(() => {
		const eda = globalThis._EXTAPI_ROOT_;
		const tab = ${JSON.stringify(TAB)};
		const ids = ${JSON.stringify(ids)};
		try { eda.sch_SelectControl.doSelectPrimitives(ids, tab); } catch (e) {}
		try { void eda.dmt_EditorControl.zoomToSelectedPrimitives(tab); } catch (e) {}
		const p = ids[0] ? null : null;
		try { void eda.dmt_EditorControl.zoomTo(0, 0, ${zoom}, tab); } catch (e) {}
		return { ok: true, ids, zoom: ${zoom} };
	})()`;
	// zoomTo(0,0,zoom) would lose selection center. Do select+zoomToSelected then zoomTo around first primitive via a second call after we know coords.
} else if (mode === 'xy') {
	const x = Number(rest[0]), y = Number(rest[1]), zoom = Number(rest[2] || 120);
	js = `(() => {
		const eda = globalThis._EXTAPI_ROOT_;
		const tab = ${JSON.stringify(TAB)};
		try { void eda.dmt_EditorControl.zoomTo(${x}, ${y}, ${zoom}, tab); } catch (e) {}
		return { ok: true, x: ${x}, y: ${y}, zoom: ${zoom} };
	})()`;
} else {
	const [l, r, t, b] = rest.map(Number);
	js = `(() => {
		const eda = globalThis._EXTAPI_ROOT_;
		const tab = ${JSON.stringify(TAB)};
		try { void eda.dmt_EditorControl.zoomToRegion(${l}, ${r}, ${t}, ${b}, tab); } catch (e) {}
		return { ok: true };
	})()`;
}

const before = await capture();
if (mode === 'select') {
	const ids = String(rest[0] || '').split(',').map(s => s.trim()).filter(Boolean);
	const zoom = Number(rest[1] || 120);
	await evalPage(`(() => {
		const eda = globalThis._EXTAPI_ROOT_;
		const tab = ${JSON.stringify(TAB)};
		try { eda.sch_SelectControl.doSelectPrimitives(${JSON.stringify(ids)}, tab); } catch (e) {}
		return true;
	})()`);
	const bbox = await evalPage(`(() => {
		const eda = globalThis._EXTAPI_ROOT_;
		try { return eda.sch_Document && null; } catch (e) { return null; }
	})()`);
	void bbox;
	// Center on first selected primitive via host zoomTo after reading coords from a data attribute is unreliable.
	// Use zoomToSelected first (may be 5%), then a high percent zoom at a provided fallback later.
	await evalPage(`(() => {
		const eda = globalThis._EXTAPI_ROOT_;
		const tab = ${JSON.stringify(TAB)};
		try { void eda.dmt_EditorControl.zoomToSelectedPrimitives(tab); } catch (e) {}
		return true;
	})()`);
	await new Promise(r => setTimeout(r, 800));
	// If caller passed zoom percent, also zoomTo the first id by asking Editor after select.
	await evalPage(`(() => {
		const eda = globalThis._EXTAPI_ROOT_;
		const tab = ${JSON.stringify(TAB)};
		try { void eda.dmt_EditorControl.zoomToSelectedPrimitives(tab); } catch (e) {}
		try { void eda.dmt_EditorControl.zoomTo(0, 0, ${zoom}, tab); } catch (e) {}
		return true;
	})()`);
} else {
	await evalPage(js);
}
await new Promise(r => setTimeout(r, 2200));
const after = await capture();
const h = b => createHash('sha256').update(b).digest('hex');
if (after.subarray(0, 8).toString('binary') !== '\x89PNG\r\n\x1a\n') throw new Error('not png');
const width = after.readUInt32BE(16), height = after.readUInt32BE(20);
if (width < 640 || height < 360) throw new Error(`too small ${width}x${height}`);
await writeFile(outPath, after);
console.log(JSON.stringify({
	ok: true,
	path: outPath,
	width,
	height,
	view_changed: h(before) !== h(after),
	sha256: h(after).slice(0, 16),
	mode,
}, null, 2));
ws.close();
