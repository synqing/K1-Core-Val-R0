// Add 9.50 × 5.10 cutout outline to GT-USB-7005A-IND, then restore hub schematic.
import { writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const FOOTPRINT_UUID = 'db6aa4d157814027bb31dae8aae789aa';
const LIBRARY_UUID = '27700277ef7a49e48a0293bece6b2993';
const HUB_PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
const OUT = '/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0/evidence/VAL-G2-2026-08-28/dec-usb-hub/jobs/t00-fp-cutout.json';

const page = (await (await fetch(`${CDP_BASE}/json/list`, { signal: AbortSignal.timeout(3000) })).json())
	.find((t) => t.type === 'page' && String(t.url).includes('pro.easyeda.com'));
if (!page) throw new Error('No EasyEDA page');
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
const evalInPage = async (expression, timeout = 120000) => {
	const response = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true, timeout });
	if (response.result?.exceptionDetails) {
		throw new Error(response.result.exceptionDetails.exception?.description || response.result.exceptionDetails.text);
	}
	return response.result?.result?.value;
};

const result = await evalInPage(`(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  await eda.lib_Footprint.openInEditor("${FOOTPRINT_UUID}", "${LIBRARY_UUID}");
  await new Promise((r) => setTimeout(r, 800));
  const segs = [
    [-4.75, -5.10, 4.75, -5.10],
    [4.75, -5.10, 4.75, 0],
    [4.75, 0, -4.75, 0],
    [-4.75, 0, -4.75, -5.10],
    [-3.12, 0, -3.12, -2.0],
    [3.12, 0, 3.12, -2.0],
    [-3.12, -2.0, 3.12, -2.0],
  ];
  const created = [];
  for (const [x1,y1,x2,y2] of segs) {
    try {
      const p = await eda.pcb_PrimitiveLine.create("", 11, x1, y1, x2, y2, 0.05);
      created.push({ x1,y1,x2,y2, ok: Boolean(p), id: p && (p.id || p.primitiveId || p) });
    } catch (e) {
      created.push({ x1,y1,x2,y2, ok: false, err: String(e && e.message || e) });
    }
  }
  let poly = null;
  try {
    const math = eda.pcb_MathPolygon && eda.pcb_MathPolygon.createPolygon
      ? eda.pcb_MathPolygon.createPolygon([-4.75,-5.10, 4.75,-5.10, 4.75,0, -4.75,0, -4.75,-5.10])
      : null;
    if (math) poly = await eda.pcb_PrimitivePolyline.create("", 11, math, 0.05);
  } catch (e) {
    poly = { err: String(e && e.message || e) };
  }
  const saved = await eda.pcb_Document.save();
  try { await eda.dmt_EditorControl.openDocument("${HUB_PAGE}"); } catch (e) {}
  return { created, poly: Boolean(poly && !poly.err), polyErr: poly && poly.err, saved, lineOk: created.filter(c=>c.ok).length };
})()`);

writeFileSync(OUT, JSON.stringify(result, null, 2));
console.log(JSON.stringify(result, null, 2));
ws.close();
