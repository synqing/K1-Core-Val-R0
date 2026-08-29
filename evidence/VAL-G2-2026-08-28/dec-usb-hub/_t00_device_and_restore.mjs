// Associate independent symbol+footprint as a personal device, then restore the hub schematic.
import { writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const LIBRARY_UUID = '27700277ef7a49e48a0293bece6b2993';
const SYMBOL_UUID = 'cb1918895dba4e1691885a1892e9235a';
const FOOTPRINT_UUID = 'db6aa4d157814027bb31dae8aae789aa';
const HUB_PROJECT = '41c8e6523576456582ea35958b3684ed';
const HUB_PAGE = '1435cb46f39e48c8a8aadbb84ca81603';

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
  const existing = await eda.lib_Device.search(name, personal, undefined, undefined, 5, 1);
  let deviceUuid = (existing||[]).find(d => d.name === name)?.uuid;
  let created = false;
  if (!deviceUuid) {
    deviceUuid = await eda.lib_Device.create(
      personal,
      name,
      {
        libraryUuid: personal,
        libraryType: "3",
        primaryClassificationUuid: "0c6123eef9994a71a80f19a1170c44f0",
        secondaryClassificationUuid: "4d4524b7560c4cd5a3bf20676566ece5"
      },
      {
        symbolType: 2,
        symbol: { uuid: "${SYMBOL_UUID}", libraryUuid: personal },
        footprint: { uuid: "${FOOTPRINT_UUID}", libraryUuid: personal }
      },
      "Independent GT-USB-7005A from manufacturer drawing. Not LCSC C5250872 cache artwork."
    );
    created = true;
  }
  const got = await eda.lib_Device.get(deviceUuid, personal);
  const gotKeys = got ? Object.keys(got) : [];
  // Restore hub schematic as the write target.
  let openedProject = null;
  let openedDoc = null;
  try {
    if (eda.dmt_Project.openProject) {
      openedProject = await eda.dmt_Project.openProject("${HUB_PROJECT}");
    }
  } catch (e) {
    openedProject = { err: String(e && e.message || e) };
  }
  try {
    openedDoc = await eda.dmt_EditorControl.openDocument("${HUB_PAGE}");
  } catch (e) {
    openedDoc = { err: String(e && e.message || e) };
  }
  await new Promise(r => setTimeout(r, 800));
  return {
    deviceUuid, created, gotKeys,
    symbolUuid: got && (got.symbolUuid || (got.symbol && got.symbol.uuid)),
    footprintUuid: got && (got.footprintUuid || (got.footprint && got.footprint.uuid)),
    name: got && got.name,
    openedProject, openedDoc
  };
})()`);

writeFileSync(
	'/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0/evidence/VAL-G2-2026-08-28/dec-usb-hub/jobs/t00-device.json',
	JSON.stringify(result, null, 2),
);
console.log(JSON.stringify(result, null, 2));
ws.close();
