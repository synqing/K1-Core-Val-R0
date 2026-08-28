#!/usr/bin/env node
// View-safe? No: this CREATES a schematic component via the host API in the live top frame.
// Used only when MCP add_schematic_component times out without landing a part.
const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const deviceUuid = process.argv[2];
const x = Number(process.argv[3]);
const y = Number(process.argv[4]);
const libraryUuid = process.argv[5] || deviceUuid;
const addIntoBom = process.argv[6] !== 'no';
const addIntoPcb = process.argv[7] !== 'no';
if (!deviceUuid || !Number.isFinite(x) || !Number.isFinite(y)) {
  console.error('usage: cdp-create-component.mjs <deviceUuid> <x> <y> [libraryUuid] [bom yes|no] [pcb yes|no]');
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

await send('Runtime.enable');
await send('Page.enable');
const tree = await send('Page.getFrameTree');
const frames = [];
(function walk(n) { if (n?.frame) frames.push(n.frame); for (const c of n.childFrames || []) walk(c); })(tree.result?.frameTree || tree.result);
await new Promise(r => setTimeout(r, 800));
const ctxs = [];
// Re-enable to collect contexts if the first enable raced.
const editorFrame = frames.find(f => String(f.url || '').includes('pro.easyeda.com/editor')) || frames[0];
const fired = await send('Runtime.evaluate', {
  expression: `(() => {
    const R = window._EXTAPI_ROOT_;
    if (!R?.sch_PrimitiveComponent?.create) return { ok:false, reason:'sch_PrimitiveComponent.create absent', keys: R ? Object.keys(R).slice(0,20) : null };
    void R.sch_PrimitiveComponent.create(
      { libraryUuid: ${JSON.stringify(libraryUuid)}, uuid: ${JSON.stringify(deviceUuid)} },
      ${x}, ${y}, undefined, 0, false, ${addIntoBom}, ${addIntoPcb}
    );
    return { ok:true, fired:true, x:${x}, y:${y}, hasCreate:true };
  })()`,
  returnByValue: true,
  awaitPromise: false,
});
const value = fired.result?.result?.value ?? { ok: false, raw: fired };
if (!value.ok) {
  console.log(JSON.stringify({ ok: false, value, exception: fired.result?.exceptionDetails }, null, 2));
  ws.close();
  process.exit(1);
}
console.log(JSON.stringify({ ok: true, value }));
ws.close();
