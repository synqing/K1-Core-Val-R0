// Probe: create empty personal symbol and confirm the editor leaves the hub schematic.
import { writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const HUB_PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
const HUB_PROJECT = '41c8e6523576456582ea35958b3684ed';

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

async function evalInPage(expression, timeout = 120000) {
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
  const personal = await eda.lib_LibrariesList.getPersonalLibraryUuid();
  const classification = {
    libraryUuid: personal,
    libraryType: "2",
    primaryClassificationUuid: "a4709da65d5e436ab083c70292e06701",
    secondaryClassificationUuid: "ea1ebcce4d4e4b4d8a45580063ed291a"
  };
  const name = "GT-USB-7005A-IND";
  const existing = await eda.lib_Symbol.search(name, personal, undefined, 2, 5, 1);
  let symbolUuid = (existing||[]).find(s => s.name === name)?.uuid;
  let created = false;
  if (!symbolUuid) {
    symbolUuid = await eda.lib_Symbol.create(
      personal,
      name,
      classification,
      2,
      "Independent GT-USB-7005A schematic symbol. Manufacturer pin table. Not LCSC C5250872 cache."
    );
    created = true;
  }
  const opened = await eda.lib_Symbol.openInEditor(symbolUuid, personal);
  await new Promise(r => setTimeout(r, 1500));
  const ctxDoc = eda.dmt_EditorControl.getCurrentDocumentUuid
    ? await eda.dmt_EditorControl.getCurrentDocumentUuid()
    : null;
  const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(eda.dmt_EditorControl)).filter(n => /current|active|tab|document/i.test(n));
  const pinIds = await eda.sch_PrimitivePin.getAllPrimitiveId();
  const stillHub = ctxDoc === "${HUB_PAGE}";
  return {
    personal, symbolUuid, created, opened, ctxDoc, methods, pinCount: (pinIds||[]).length, stillHub,
    hubPage: "${HUB_PAGE}", hubProject: "${HUB_PROJECT}"
  };
})()`);

writeFileSync(
	'/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0/evidence/VAL-G2-2026-08-28/dec-usb-hub/jobs/t00-lib-probe.json',
	JSON.stringify(result, null, 2),
);
console.log(JSON.stringify(result, null, 2));
ws.close();
