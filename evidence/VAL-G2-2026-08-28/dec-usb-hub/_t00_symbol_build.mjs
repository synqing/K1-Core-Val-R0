// Populate the independently created GT-USB-7005A symbol. Hub schematic must not be current.
import { writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const SYMBOL_UUID = 'cb1918895dba4e1691885a1892e9235a';
const LIBRARY_UUID = '27700277ef7a49e48a0293bece6b2993';
const HUB_PAGE = '1435cb46f39e48c8a8aadbb84ca81603';

const PINS = [
	{ n: 'A1', name: 'GND', typ: 'Ground' },
	{ n: 'A2', name: 'TX1+', typ: 'Passive' },
	{ n: 'A3', name: 'TX1-', typ: 'Passive' },
	{ n: 'A4', name: 'VBUS', typ: 'Power' },
	{ n: 'A5', name: 'CC1', typ: 'Passive' },
	{ n: 'A6', name: 'D+', typ: 'BI' },
	{ n: 'A7', name: 'D-', typ: 'BI' },
	{ n: 'A8', name: 'SBU1', typ: 'Passive' },
	{ n: 'A9', name: 'VBUS', typ: 'Power' },
	{ n: 'A10', name: 'RX2-', typ: 'Passive' },
	{ n: 'A11', name: 'RX2+', typ: 'Passive' },
	{ n: 'A12', name: 'GND', typ: 'Ground' },
	{ n: 'B1', name: 'GND', typ: 'Ground' },
	{ n: 'B2', name: 'TX2+', typ: 'Passive' },
	{ n: 'B3', name: 'TX2-', typ: 'Passive' },
	{ n: 'B4', name: 'VBUS', typ: 'Power' },
	{ n: 'B5', name: 'CC2', typ: 'Passive' },
	{ n: 'B6', name: 'D+', typ: 'BI' },
	{ n: 'B7', name: 'D-', typ: 'BI' },
	{ n: 'B8', name: 'SBU2', typ: 'Passive' },
	{ n: 'B9', name: 'VBUS', typ: 'Power' },
	{ n: 'B10', name: 'RX1-', typ: 'Passive' },
	{ n: 'B11', name: 'RX1+', typ: 'Passive' },
	{ n: 'B12', name: 'GND', typ: 'Ground' },
	{ n: 'S1', name: 'SHELL.TAB1', typ: 'Ground' },
	{ n: 'S2', name: 'SHELL.TAB2', typ: 'Ground' },
	{ n: 'S3', name: 'SHELL.TAB3', typ: 'Ground' },
	{ n: 'S4', name: 'SHELL.TAB4', typ: 'Ground' },
];

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
  const opened = await eda.lib_Symbol.openInEditor("${SYMBOL_UUID}", "${LIBRARY_UUID}");
  await new Promise(r => setTimeout(r, 800));
  const existing = await eda.sch_PrimitivePin.getAllPrimitiveId();
  if ((existing||[]).length > 0) {
    return { skipped: true, reason: "symbol already has pins", pinCount: existing.length, opened };
  }
  const body = await eda.sch_PrimitiveRectangle.create(-20, -20, 240, 420, 0, 0, "#000000", null, 1);
  const created = [];
  const a = ${JSON.stringify(PINS.filter(p => p.n.startsWith('A')))};
  const b = ${JSON.stringify(PINS.filter(p => p.n.startsWith('B')))};
  const s = ${JSON.stringify(PINS.filter(p => p.n.startsWith('S')))};
  for (let i = 0; i < a.length; i++) {
    const y = i * 32;
    const pin = await eda.sch_PrimitivePin.create(-40, y, a[i].n, a[i].name, 0, 20, null, "None", a[i].typ);
    created.push({ id: pin && (pin.id || pin.primitiveId || pin.uuid), n: a[i].n, side: "A" });
  }
  for (let i = 0; i < b.length; i++) {
    const y = i * 32;
    const pin = await eda.sch_PrimitivePin.create(240, y, b[i].n, b[i].name, 180, 20, null, "None", b[i].typ);
    created.push({ id: pin && (pin.id || pin.primitiveId || pin.uuid), n: b[i].n, side: "B" });
  }
  for (let i = 0; i < s.length; i++) {
    const x = 20 + i * 50;
    const pin = await eda.sch_PrimitivePin.create(x, 420, s[i].n, s[i].name, 270, 20, null, "None", s[i].typ);
    created.push({ id: pin && (pin.id || pin.primitiveId || pin.uuid), n: s[i].n, side: "S" });
  }
  try { await eda.sch_PrimitiveText.create(100, -50, "GT-USB-7005A", 0, 10); } catch (e) { created.push({ textErr: String(e && e.message || e) }); }
  const saved = await eda.sch_Document.save();
  const pinIds = await eda.sch_PrimitivePin.getAllPrimitiveId();
  const pins = [];
  for (const pid of pinIds || []) {
    const p = await eda.sch_PrimitivePin.get(pid);
    const st = p && (p.getState ? p.getState() : p);
    pins.push({
      id: pid,
      num: st && (st.pinNumber || st.number),
      name: st && (st.pinName || st.name),
      x: st && st.x,
      y: st && st.y,
    });
  }
  return {
    opened, body: Boolean(body), createdCount: created.length, saved,
    pinIdCount: (pinIds||[]).length, pins, created
  };
})()`);

writeFileSync(
	'/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0/evidence/VAL-G2-2026-08-28/dec-usb-hub/jobs/t00-symbol-build.json',
	JSON.stringify(result, null, 2),
);
console.log(JSON.stringify({ pinIdCount: result.pinIdCount, createdCount: result.createdCount, saved: result.saved, pins: result.pins }, null, 2));
ws.close();
