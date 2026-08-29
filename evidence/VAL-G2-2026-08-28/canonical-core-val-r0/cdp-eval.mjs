#!/usr/bin/env node
// Evaluate JS in the EasyEDA top frame. Arg: expression or @file.
const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = process.env.EASYEDA_PROJECT || '64325d0e55e0435abd018defb0089a9b';
const fs = await import('node:fs');
const expr = process.argv[2]?.startsWith('@')
  ? fs.readFileSync(process.argv[2].slice(1), 'utf8')
  : process.argv[2];
if (!expr) {
  console.error('usage: cdp-eval.mjs <expression|@file>');
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
const fired = await send('Runtime.evaluate', {
  expression: expr,
  returnByValue: true,
  awaitPromise: true,
});
if (fired.result?.exceptionDetails) {
  console.log(JSON.stringify({ ok: false, exception: fired.result.exceptionDetails }, null, 2));
  ws.close();
  process.exit(1);
}
console.log(JSON.stringify(fired.result?.result?.value ?? fired.result, null, 2));
ws.close();
