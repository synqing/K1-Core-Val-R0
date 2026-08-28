#!/usr/bin/env node
// Set or clear the EasyEDA schematic No Connect cross on named pins.
// The official MCP setter is dead on this host (no setState_NoConnected).
// This writes the same attrPara NO_CONNECT=1 object the editor uses.

const fs = await import('node:fs/promises');
const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const payloadPath = process.argv[2];
if (!payloadPath) throw new Error('usage: easyeda_set_pin_noconnect.mjs payload.json');
const payload = JSON.parse(await fs.readFile(payloadPath, 'utf8'));
const pins = payload.pins;
if (!Array.isArray(pins) || !pins.length) throw new Error('payload.pins required');

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const page = targets.find(t => t.type === 'page' && String(t.url).includes(PROJECT));
if (!page) throw new Error('canonical EasyEDA page not found');
const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
ws.onmessage = event => {
  const msg = JSON.parse(event.data);
  if (msg.id && pending.has(msg.id)) {
    pending.get(msg.id)(msg);
    pending.delete(msg.id);
  }
};
await new Promise(resolve => { ws.onopen = resolve; });
const send = (method, params = {}) => new Promise(resolve => {
  const messageId = ++id;
  pending.set(messageId, resolve);
  ws.send(JSON.stringify({ id: messageId, method, params }));
});
const evaluate = async expression => {
  const reply = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (reply.error || reply.result?.exceptionDetails)
    throw new Error(reply.error?.message || reply.result.exceptionDetails.text);
  return reply.result?.result?.value;
};

const result = await evaluate(`(async () => {
  const requested = ${JSON.stringify(pins)};
  const eda = globalThis._EXTAPI_ROOT_;
  const sch = [...document.querySelectorAll('iframe')]
    .find(f => (f.src || '').includes('entry=sch') && f.contentWindow?.callCommand?.hooks?.getEditJson);
  if (!sch) return { ok:false, reason:'schematic iframe hooks unavailable' };
  const hooks = sch.contentWindow.callCommand.hooks;
  const ej = hooks.getEditJson();
  const nextId = () => {
    const raw = String(ej.getMaxId() || 'e0');
    const match = raw.match(/^e(\\d+)$/);
    let n = match ? Number(match[1]) : 0;
    let candidate = 'e' + n;
    while (ej.getObj(candidate)) {
      n += 1;
      candidate = 'e' + n;
    }
    return candidate;
  };
  const applied = [];
  const skipped = [];
  for (const item of requested) {
    const pinsOf = await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(item.componentPrimitiveId);
    const list = Array.isArray(pinsOf) ? pinsOf : [];
    const pin = list.find(p => String(p.pinNumber) === String(item.pinNumber));
    if (!pin) {
      skipped.push({ ...item, reason:'pin-not-found' });
      continue;
    }
    const pinId = pin.primitiveId;
    const obj = hooks.getEditJsonObj(pinId);
    if (!obj) {
      skipped.push({ ...item, pinId, reason:'editjson-missing' });
      continue;
    }
    const existing = obj.attrPara
      ? Object.entries(obj.attrPara).find(([, value]) => value && value.key === 'NO_CONNECT')
      : null;
    const want = item.noConnect !== false;
    if (want && existing) {
      skipped.push({ ...item, pinId, reason:'already-nc', attrId: existing[0] });
      continue;
    }
    if (!want && !existing) {
      skipped.push({ ...item, pinId, reason:'already-clear' });
      continue;
    }
    if (want) {
      const attrId = nextId();
      const x = obj.head.x;
      const y = obj.head.y;
      const attr = {
        parentId: pinId,
        key: 'NO_CONNECT',
        value: '1',
        keyVisible: false,
        valueVisible: false,
        x, y, rotation: 0, locked: false,
        guideLine: [x, y, x + 1, y, x, y - 1],
        color: null, fillColor: null, fillStyle: null,
        fontFamily: null, fontSize: null,
        strikeout: null, underline: null, italic: null, fontWeight: null,
        vAlign: null, hAlign: null,
        gId: attrId,
      };
      ej.setObj(pinId, { attrPara: { [attrId]: attr } }, { pureUpdate: true });
      applied.push({ ...item, pinId, attrId, action:'set' });
    } else {
      ej.deleteObj(existing[0]);
      applied.push({ ...item, pinId, attrId: existing[0], action:'clear' });
    }
  }
  hooks.saveBatch();
  return { ok:true, applied, skipped, maxId: ej.getMaxId() };
})()`);

if (payload.out) await fs.writeFile(payload.out, JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify(result));
ws.close();
if (!result?.ok) process.exit(1);
