// Dismiss leftover library-editor modal, activate hub schematic, close library tabs.
import { writeFile } from 'node:fs/promises';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const OUT = '/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0/evidence/VAL-G2-2026-08-28/dec-usb-hub/screenshots/T00-j1-place.png';
const HUB_PROJECT = '41c8e6523576456582ea35958b3684ed';
const HUB_PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
const TAB = `${HUB_PAGE}@${HUB_PROJECT}`;

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
await send('Runtime.enable');

const restored = await send('Runtime.evaluate', {
	expression: `(async () => {
		const eda = globalThis._EXTAPI_ROOT_;
		const closed = [];
		// Dismiss modal if present.
		const buttons = [...document.querySelectorAll('button, .ant-btn, [role="button"]')];
		const cancel = buttons.find(b => /cancel|取消/i.test(b.textContent || ''));
		if (cancel) { cancel.click(); closed.push('clicked-cancel'); }
		const mask = document.querySelector('.ant-modal-mask, .el-overlay, .modal-mask');
		await new Promise(r => setTimeout(r, 400));
		try { await eda.dmt_Project.openProject("${HUB_PROJECT}"); closed.push('openProject'); } catch (e) { closed.push('openProject:'+e); }
		try { await eda.dmt_EditorControl.activateDocument("${TAB}"); closed.push('activate'); } catch (e) { closed.push('activate:'+e); }
		try { await eda.dmt_EditorControl.openDocument("${HUB_PAGE}"); closed.push('openDoc'); } catch (e) { closed.push('openDoc:'+e); }
		// Close leftover library tabs if the API accepts tab ids.
		const tabs = await eda.dmt_EditorControl.getTabsBySplitScreenId?.("editor-window-main");
		const tabIds = (tabs || []).map(t => t.tabId || t.id || t.title);
		for (const t of tabs || []) {
			const title = String(t.title || '');
			const id = t.tabId || t.id;
			if (/GT-USB-7005A/i.test(title) && id) {
				try { await eda.dmt_EditorControl.closeDocument(id); closed.push('closed:'+title); } catch (e) { closed.push('closeFail:'+title); }
			}
		}
		await new Promise(r => setTimeout(r, 600));
		try { void eda.dmt_EditorControl.zoomToRegion(40, 520, 3280, 4220, "${TAB}"); } catch (e) {}
		try { void eda.sch_Document.navigateToRegion(40, 3280, 480, 940); } catch (e) {}
		return { closed, tabIds, nTabs: (tabs||[]).length };
	})()`,
	returnByValue: true,
	awaitPromise: true,
	timeout: 30000,
});
console.log(JSON.stringify(restored.result?.result?.value || restored.result, null, 2));
await new Promise(r => setTimeout(r, 2000));
const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
const data = shot.result?.data;
if (!data) throw new Error('no screenshot');
await writeFile(OUT, Buffer.from(data, 'base64'));
console.log(JSON.stringify({ out: OUT, bytes: Buffer.from(data, 'base64').length }));
ws.close();
