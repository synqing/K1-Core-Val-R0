import { readFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const HUB = '41c8e6523576456582ea35958b3684ed';
const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
const expr = readFileSync(new URL('./T00-open-schematic.js', import.meta.url), 'utf8');

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const page = targets.find((t) => t.type === 'page' && String(t.url).includes(HUB));
if (!page) throw new Error('no hub page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) pending.get(m.id)(m);
};
await new Promise((r) => { ws.onopen = r; });
const send = (method, params = {}) => new Promise((res) => {
  const i = ++id; pending.set(i, res);
  ws.send(JSON.stringify({ id: i, method, params }));
});

await send('Page.enable');
const opened = await send('Runtime.evaluate', {
  expression: expr,
  returnByValue: true,
  awaitPromise: true,
  timeout: 60000,
});
console.log('open', JSON.stringify(opened.result?.result?.value || opened.result?.exceptionDetails || opened, null, 2));

for (let i = 0; i < 12; i++) {
  await new Promise((r) => setTimeout(r, 1000));
  const tree = await send('Page.getFrameTree');
  const frames = [];
  (function walk(n) {
    if (n?.frame) frames.push({ name: n.frame.name || '', url: String(n.frame.url || '').slice(0, 160) });
    for (const c of n.childFrames || []) walk(c);
  })(tree.result?.frameTree || tree.result);
  const hit = frames.find((f) => String(f.name).includes(PAGE));
  console.log(`t+${i + 1}s frames=${frames.length} hit=${Boolean(hit)} names=${JSON.stringify(frames.map((f) => f.name))}`);
  if (hit) {
    ws.close();
    process.exit(0);
  }
}
ws.close();
process.exit(2);
