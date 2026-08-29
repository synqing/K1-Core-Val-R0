#!/usr/bin/env node
const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
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
const evaluate = async (expression, awaitPromise = true) => {
  const reply = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise });
  if (reply.error || reply.result?.exceptionDetails) {
    throw new Error(JSON.stringify(reply.error || reply.result?.exceptionDetails));
  }
  return reply.result?.result?.value;
};
await send('Runtime.enable');
const info = await evaluate(`(async () => {
  const R = window._EXTAPI_ROOT_;
  const doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  const nodes = [...document.querySelectorAll('[title],button,[aria-label]')].filter(x => x.offsetParent !== null);
  const titles = nodes.map(x => ({
    title: x.getAttribute('title') || '',
    aria: x.getAttribute('aria-label') || '',
    tag: x.tagName,
    text: (x.innerText || '').slice(0, 40),
  })).filter(x => /fit|zoom|3d|preview|view|camera|orbit|top|front|iso/i.test(x.title + x.aria + x.text));
  const allTitles = nodes.map(x => x.getAttribute('title') || x.getAttribute('aria-label') || '').filter(Boolean);
  const apis = Object.keys(R).filter(k => /3d|preview|camera|view/i.test(k));
  return { doc, titles, allTitles, apis };
})()`);
console.log(JSON.stringify(info, null, 2));
ws.close();
