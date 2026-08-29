// Create empty footprint, open editor, drop one millimetre-sized pad, read it back.
import { writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const LIBRARY_UUID = '27700277ef7a49e48a0293bece6b2993';

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
  const personal = "${LIBRARY_UUID}";
  const name = "GT-USB-7005A-IND";
  const existing = await eda.lib_Footprint.search(name, personal, undefined, 5, 1);
  let footprintUuid = (existing||[]).find(s => s.name === name)?.uuid;
  let created = false;
  if (!footprintUuid) {
    footprintUuid = await eda.lib_Footprint.create(
      personal,
      name,
      { libraryUuid: personal, libraryType: "4", primaryClassificationUuid: "f5665dd35d0a4b2e9c8b296f6560808c" },
      "Independent GT-USB-7005A footprint from manufacturer recommended layout. Not LCSC C5250872 cache."
    );
    created = true;
  }
  const opened = await eda.lib_Footprint.openInEditor(footprintUuid, personal);
  await new Promise(r => setTimeout(r, 1200));
  const idsBefore = await eda.pcb_PrimitivePad.getAllPrimitiveId();
  // Probe millimetre coordinates: A1 at -2.75, 0, 0.35 x 1.00 rectangle.
  const pad = await eda.pcb_PrimitivePad.create(
    1, "PROBE", -2.75, 0, 0,
    ["RECT", 0.35, 1.00, 0],
    "",
    null,
    0, 0, 0,
    true,
    0
  );
  const ids = await eda.pcb_PrimitivePad.getAllPrimitiveId();
  const got = [];
  for (const pid of ids || []) {
    const p = await eda.pcb_PrimitivePad.get(pid);
    const st = p && (typeof p.getState === "function" ? p.getState() : p);
    got.push({
      id: pid,
      num: st && (st.padNumber || st.number),
      x: st && st.x,
      y: st && st.y,
      pad: st && st.pad,
      keys: st && Object.keys(st).slice(0, 20)
    });
  }
  const origin = await eda.pcb_Document.getCanvasOrigin();
  return { footprintUuid, created, opened, idsBefore, probePad: Boolean(pad), got, origin };
})()`);

writeFileSync(
	'/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0/evidence/VAL-G2-2026-08-28/dec-usb-hub/jobs/t00-fp-probe.json',
	JSON.stringify(result, null, 2),
);
console.log(JSON.stringify(result, null, 2));
ws.close();
