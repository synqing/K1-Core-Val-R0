// Rebuild GT-USB-7005A-IND from J1-GT-USB-7005A-pads.json.
// Withdraws the single B-row at Y=-1.15. Does not import C5250872 cache.
import { writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const FOOTPRINT_UUID = 'db6aa4d157814027bb31dae8aae789aa';
const LIBRARY_UUID = '27700277ef7a49e48a0293bece6b2993';
const HUB_PROJECT = '41c8e6523576456582ea35958b3684ed';
const HUB_PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
const FP_TAB = `${FOOTPRINT_UUID}@${LIBRARY_UUID}`;
const OUT_JSON = '/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0/evidence/VAL-G2-2026-08-28/dec-usb-hub/jobs/t00-fp-rebuild-staggered.json';
const OUT_PNG = '/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0/evidence/VAL-G2-2026-08-28/dec-usb-hub/screenshots/T00-fp-staggered.png';

const A = [
	['A1', -2.75], ['A2', -2.25], ['A3', -1.75], ['A4', -1.25],
	['A5', -0.75], ['A6', -0.25], ['A7', 0.25], ['A8', 0.75],
	['A9', 1.25], ['A10', 1.75], ['A11', 2.25], ['A12', 2.75],
];
const B_UPPER = [
	['B12', -3.12], ['B9', -1.30], ['B7', -0.65],
	['B6', 0.65], ['B4', 1.30], ['B1', 3.12],
];
const B_LOWER = [
	['B11', -2.50], ['B10', -1.70], ['B8', -0.85],
	['B5', 0.85], ['B3', 1.70], ['B2', 2.50],
];

async function getEasyedaPage() {
	const response = await fetch(`${CDP_BASE}/json/list`, { signal: AbortSignal.timeout(3000) });
	const targets = await response.json();
	const page = targets.find((target) => target.type === 'page' && String(target.url).includes('pro.easyeda.com'));
	if (!page) throw new Error('No EasyEDA page target');
	if (String(page.url).includes('64325d0e55e0435abd018defb0089a9b') && !String(page.url).includes(HUB_PROJECT)) {
		throw new Error('refusing live product window');
	}
	return page;
}

const page = await getEasyedaPage();
const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
ws.onmessage = (event) => {
	const message = JSON.parse(event.data);
	if (message.id && pending.has(message.id)) {
		pending.get(message.id)(message);
		pending.delete(message.id);
	}
};
const send = (method, params) => new Promise((resolve) => {
	const messageId = ++id;
	pending.set(messageId, resolve);
	ws.send(JSON.stringify({ id: messageId, method, params }));
});
await new Promise((resolve) => { ws.onopen = resolve; });

async function evalInPage(expression, timeout = 180000) {
	const response = await send('Runtime.evaluate', {
		expression,
		returnByValue: true,
		awaitPromise: true,
		timeout,
	});
	if (response.result?.exceptionDetails) {
		const description = response.result.exceptionDetails.exception?.description
			|| response.result.exceptionDetails.text || 'CDP exception';
		throw new Error(description);
	}
	return response.result?.result?.value;
}

const result = await evalInPage(`(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  if (!eda) return { ok: false, reason: 'no _EXTAPI_ROOT_' };
  const opened = await eda.lib_Footprint.openInEditor("${FOOTPRINT_UUID}", "${LIBRARY_UUID}");
  await new Promise((r) => setTimeout(r, 1000));
  const beforeIds = await eda.pcb_PrimitivePad.getAllPrimitiveId();
  const before = [];
  for (const pid of beforeIds || []) {
    const p = await eda.pcb_PrimitivePad.get(pid);
    const st = p && (typeof p.getState === "function" ? p.getState() : p);
    before.push({ id: pid, num: st && st.padNumber, x: st && st.x, y: st && st.y });
  }
  for (const pid of beforeIds || []) {
    await eda.pcb_PrimitivePad.delete(pid);
  }
  let polyDeleted = 0;
  try {
    const polys = await eda.pcb_PrimitivePolyline.getAllPrimitiveId();
    for (const pid of polys || []) {
      await eda.pcb_PrimitivePolyline.delete(pid);
      polyDeleted += 1;
    }
  } catch (e) {
    polyDeleted = String(e && e.message || e);
  }
  const created = [];
  const A = ${JSON.stringify(A)};
  const B_UPPER = ${JSON.stringify(B_UPPER)};
  const B_LOWER = ${JSON.stringify(B_LOWER)};
  for (const [n, x] of A) {
    const p = await eda.pcb_PrimitivePad.create(
      1, n, x, 0, 0, ["RECT", 0.35, 0.92, 0], "", null, 0, 0, 0, true, 0
    );
    created.push({ n, kind: "SMD", ok: Boolean(p) });
  }
  for (const [n, x] of B_UPPER) {
    const p = await eda.pcb_PrimitivePad.create(
      12, n, x, -1.80, 0, ["ELLIPSE", 0.70, 0.70], "", ["ROUND", 0.40], 0, 0, 0, true, 0
    );
    created.push({ n, kind: "TH_UPPER", ok: Boolean(p) });
  }
  for (const [n, x] of B_LOWER) {
    const p = await eda.pcb_PrimitivePad.create(
      12, n, x, -2.70, 0, ["ELLIPSE", 0.70, 0.70], "", ["ROUND", 0.40], 0, 0, 0, true, 0
    );
    created.push({ n, kind: "TH_LOWER", ok: Boolean(p) });
  }
  const slots = [
    ["S1", -6.075, -1.95, 1.20, 1.70, 1.00, 1.50],
    ["S2",  6.075, -1.95, 1.20, 1.70, 1.00, 1.50],
    ["S3", -6.075, -5.80, 1.20, 2.20, 1.00, 2.00],
    ["S4",  6.075, -5.80, 1.20, 2.20, 1.00, 2.00],
  ];
  for (const [n, x, y, pw, ph, hw, hh] of slots) {
    const p = await eda.pcb_PrimitivePad.create(
      12, n, x, y, 0, ["OVAL", pw, ph], "", ["SLOT", hw, hh], 0, 0, 0, true, 0
    );
    created.push({ n, kind: "SLOT", ok: Boolean(p) });
  }
  for (const [n, x] of [["LOC.1", -3.45], ["LOC.2", 3.45]]) {
    const p = await eda.pcb_PrimitivePad.create(
      12, n, x, -1.10, 0, ["ELLIPSE", 0.75, 0.75], "", ["ROUND", 0.75], 0, 0, 0, false, 0
    );
    created.push({ n, kind: "NPTH", ok: Boolean(p) });
  }
  let cutout = null;
  try {
    cutout = await eda.pcb_PrimitivePolyline.create(
      "", 11,
      [-4.75, -5.10, "L", 4.75, -5.10, 4.75, 0, -4.75, 0, -4.75, -5.10],
      0.05
    );
  } catch (e) {
    cutout = { err: String(e && e.message || e) };
  }
  const saved = await eda.pcb_Document.save();
  const ids = await eda.pcb_PrimitivePad.getAllPrimitiveId();
  const pads = [];
  const ys = new Set();
  for (const pid of ids || []) {
    const p = await eda.pcb_PrimitivePad.get(pid);
    const st = p && (typeof p.getState === "function" ? p.getState() : p);
    const y = st && st.y;
    if (typeof y === "number") ys.add(Number(y.toFixed(3)));
    pads.push({
      id: pid,
      num: st && st.padNumber,
      x: st && st.x,
      y: st && st.y,
      pad: st && st.pad,
      hole: st && st.hole,
      layer: st && st.layer,
      metal: st && st.metallization
    });
  }
  const bYs = pads.filter((p) => String(p.num || "").startsWith("B")).map((p) => Number(Number(p.y).toFixed(2)));
  const uniqueB = [...new Set(bYs)].sort((a, b) => a - b);
  return {
    ok: true,
    opened,
    beforeCount: before.length,
    beforeBYs: [...new Set(before.filter((p) => String(p.num || "").startsWith("B")).map((p) => p.y))],
    polyDeleted,
    created,
    saved,
    padCount: pads.length,
    pads,
    uniqueB,
    staggered: uniqueB.length === 2 && uniqueB.includes(-1.8) && uniqueB.includes(-2.7),
    cutout: Boolean(cutout && !cutout.err),
    cutoutErr: cutout && cutout.err,
  };
})()`);

await send('Page.enable');
try {
	await evalInPage(`(async () => {
    const eda = globalThis._EXTAPI_ROOT_;
    const EC = eda && eda.dmt_EditorControl;
    if (EC && EC.zoomToFit) {
      try { EC.zoomToFit("${FP_TAB}"); } catch (e) { try { EC.zoomToFit(); } catch (e2) {} }
    }
    await new Promise((r) => setTimeout(r, 1800));
    return true;
  })()`);
} catch {
	await new Promise((r) => setTimeout(r, 1800));
}
const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
let shotMeta = { captured: false };
if (shot.result?.data) {
	const buf = Buffer.from(shot.result.data, 'base64');
	if (buf.subarray(0, 8).toString('binary') === '\x89PNG\r\n\x1a\n') {
		writeFileSync(OUT_PNG, buf);
		shotMeta = {
			captured: true,
			path: OUT_PNG,
			width: buf.readUInt32BE(16),
			height: buf.readUInt32BE(20),
			sha256: createHash('sha256').update(buf).digest('hex').slice(0, 16),
		};
	}
}

let restored = null;
try {
	restored = await evalInPage(`(async () => {
    const eda = globalThis._EXTAPI_ROOT_;
    try { await eda.dmt_EditorControl.openDocument("${HUB_PAGE}"); } catch (e) {
      return { err: String(e && e.message || e) };
    }
    await new Promise((r) => setTimeout(r, 600));
    const ctx = await eda.dmt_EditorControl.getCurrentDocument();
    return { uuid: ctx && ctx.uuid, parent: ctx && ctx.parentProjectUuid };
  })()`, 30000);
} catch (error) {
	restored = { err: String(error && error.message || error) };
}

const payload = { ...result, shot: shotMeta, restored };
writeFileSync(OUT_JSON, JSON.stringify(payload, null, 2));
console.log(JSON.stringify({
	ok: result && result.ok,
	saved: result && result.saved,
	padCount: result && result.padCount,
	uniqueB: result && result.uniqueB,
	staggered: result && result.staggered,
	cutout: result && result.cutout,
	cutoutErr: result && result.cutoutErr,
	shot: shotMeta,
	restored,
	createdOk: result && result.created && result.created.filter((c) => c.ok).length,
}, null, 2));
ws.close();
if (!result || !result.staggered || result.padCount !== 30) process.exit(1);
