#!/usr/bin/env node
const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PCB = '59bef7e87cff4cd580561703b62d8c19';
const ACTIVATE = process.argv.includes('--activate');

const targets = await (await fetch(CDP_BASE + '/json/list')).json();
const page = targets.find(t => t.type === 'page' && String(t.url).includes(PROJECT));
if (!page) throw new Error('no CDP page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
ws.onmessage = ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) pending.get(m.id)(m);
};
await new Promise(r => { ws.onopen = r; });
const send = (method, params = {}) => new Promise(res => {
  const i = ++id;
  pending.set(i, res);
  ws.send(JSON.stringify({ id: i, method, params }));
});
await send('Runtime.enable');
const fired = await send('Runtime.evaluate', {
  expression: `(async () => {
    const R = window._EXTAPI_ROOT_;
    if (${ACTIVATE ? 'true' : 'false'}) {
      try { await R.dmt_EditorControl.activateDocument('${PCB}@${PROJECT}'); } catch (e) {}
      await new Promise(r => setTimeout(r, 400));
    }
    const inspect = (c) => {
      if (!c) return { missing: true };
      const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
      return {
        des: c.getState_Designator && c.getState_Designator(),
        id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
        sid: c.getState_SupplierId && c.getState_SupplierId(),
        mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
        model: other['3D Model'],
        title: other['3D Model Title'],
        xf: other['3D Model Transform'],
      };
    };
    const comps = await R.pcb_PrimitiveComponent.getAll();
    return {
      u1: inspect(comps.find(c => c.getState_Designator && c.getState_Designator() === 'U1')),
      u6: inspect(comps.find(c => c.getState_Designator && c.getState_Designator() === 'U6-RTC')),
      d1: inspect(comps.find(c => c.getState_Designator && c.getState_Designator() === 'D1-PWR1')),
    };
  })()`,
  returnByValue: true,
  awaitPromise: true,
});
if (fired.result?.exceptionDetails) {
  console.log(JSON.stringify({ ok: false, exception: fired.result.exceptionDetails }, null, 2));
  ws.close();
  process.exit(1);
}
console.log(JSON.stringify(fired.result?.result?.value, null, 2));
ws.close();
