// Build GT-USB-7005A footprint from locked manufacturer millimetres. Delete the unit probe pad first.
import { writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const FOOTPRINT_UUID = 'db6aa4d157814027bb31dae8aae789aa';
const LIBRARY_UUID = '27700277ef7a49e48a0293bece6b2993';

const A = [
	['A1', -2.75], ['A2', -2.25], ['A3', -1.75], ['A4', -1.25],
	['A5', -0.75], ['A6', -0.25], ['A7', 0.25], ['A8', 0.75],
	['A9', 1.25], ['A10', 1.75], ['A11', 2.25], ['A12', 2.75],
];
const B = A.map(([n, x]) => [n.replace('A', 'B'), x]);

async function getEasyedaPage() {
	const response = await fetch(`${CDP_BASE}/json/list`, { signal: AbortSignal.timeout(3000) });
	const targets = await response.json();
	const page = targets.find(target => target.type === 'page' && String(target.url).includes('pro.easyeda.com'));
	if (!page) throw new Error('No EasyEDA page target');
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
await new Promise(resolve => { ws.onopen = resolve; });

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
  const opened = await eda.lib_Footprint.openInEditor("${FOOTPRINT_UUID}", "${LIBRARY_UUID}");
  await new Promise(r => setTimeout(r, 800));
  const existing = await eda.pcb_PrimitivePad.getAllPrimitiveId();
  for (const pid of existing || []) {
    await eda.pcb_PrimitivePad.delete(pid);
  }
  const created = [];
  const A = ${JSON.stringify(A)};
  const B = ${JSON.stringify(B)};
  for (const [n, x] of A) {
    const p = await eda.pcb_PrimitivePad.create(
      1, n, x, 0, 0, ["RECT", 0.35, 1.00, 0], "", null, 0, 0, 0, true, 0
    );
    created.push({ n, kind: "SMD", ok: Boolean(p) });
  }
  for (const [n, x] of B) {
    const p = await eda.pcb_PrimitivePad.create(
      12, n, x, -1.15, 0, ["ELLIPSE", 0.80, 0.80], "", ["ROUND", 0.40], 0, 0, 0, true, 0
    );
    created.push({ n, kind: "TH", ok: Boolean(p) });
  }
  const slots = [
    ["S1", -6.075, -1.95, 1.20, 2.15, 1.00, 1.95, 0],
    ["S2",  6.075, -1.95, 1.20, 2.15, 1.00, 1.95, 0],
    ["S3", -6.075, -5.80, 1.70, 1.20, 1.50, 1.00, 0],
    ["S4",  6.075, -5.80, 1.70, 1.20, 1.50, 1.00, 0],
  ];
  for (const [n, x, y, pw, ph, hw, hh, rot] of slots) {
    const p = await eda.pcb_PrimitivePad.create(
      12, n, x, y, rot, ["OVAL", pw, ph], "", ["SLOT", hw, hh], 0, 0, rot, true, 0
    );
    created.push({ n, kind: "SLOT", ok: Boolean(p) });
  }
  for (const [n, x] of [["H1", -3.45], ["H2", 3.45]]) {
    const p = await eda.pcb_PrimitivePad.create(
      12, n, x, -0.90, 0, ["ELLIPSE", 0.75, 0.75], "", ["ROUND", 0.75], 0, 0, 0, false, 0
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
  for (const pid of ids || []) {
    const p = await eda.pcb_PrimitivePad.get(pid);
    const st = p && (typeof p.getState === "function" ? p.getState() : p);
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
  return { opened, created, saved, padCount: pads.length, pads, cutout: Boolean(cutout && !cutout.err), cutoutErr: cutout && cutout.err };
})()`);

writeFileSync(
	'/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0/evidence/VAL-G2-2026-08-28/dec-usb-hub/jobs/t00-fp-build.json',
	JSON.stringify(result, null, 2),
);
console.log(JSON.stringify({
	saved: result.saved,
	padCount: result.padCount,
	cutout: result.cutout,
	cutoutErr: result.cutoutErr,
	created: result.created,
	pads: result.pads,
}, null, 2));
ws.close();
