#!/usr/bin/env node
// Delete one schematic primitive via the live host API, then wait for getAll to drop it.
const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const primitiveId = process.argv[2];
if (!primitiveId) {
  console.error('usage: cdp-delete-component.mjs <primitiveId>');
  process.exit(2);
}

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const page = targets.find(t => t.type === 'page' && String(t.url).includes(PROJECT));
if (!page) throw new Error(`no CDP page for ${PROJECT}`);
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
const evaluate = async (expression, awaitPromise = false) => {
  const reply = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise });
  if (reply.error || reply.result?.exceptionDetails) {
    throw new Error(reply.error?.message || reply.result.exceptionDetails.text);
  }
  return reply.result?.result?.value;
};

await send('Runtime.enable');
await send('Page.enable');
const fired = await evaluate(`(() => {
  const R = window._EXTAPI_ROOT_;
  if (!R?.sch_PrimitiveComponent?.delete) return { ok:false, reason:'delete absent' };
  void R.sch_PrimitiveComponent.delete(${JSON.stringify(primitiveId)});
  return { ok:true, fired:true };
})()`, false);
if (!fired?.ok) {
  console.log(JSON.stringify({ ok: false, fired }, null, 2));
  ws.close();
  process.exit(1);
}
const polls = [];
for (let i = 0; i < 8; i++) {
  await new Promise(r => setTimeout(r, 400));
  const present = await evaluate(`(() => {
    const R = window._EXTAPI_ROOT_;
    const ids = R?.sch_PrimitiveComponent?.getAllPrimitiveId?.() || [];
    return { present: ids.includes(${JSON.stringify(primitiveId)}), count: ids.length };
  })()`, false);
  polls.push(present);
  if (present && present.present === false) {
    console.log(JSON.stringify({ ok: true, gone: true, polls }, null, 2));
    ws.close();
    process.exit(0);
  }
}
console.log(JSON.stringify({ ok: false, gone: false, polls }, null, 2));
ws.close();
process.exit(1);
