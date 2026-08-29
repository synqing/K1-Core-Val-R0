const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const HUB = '41c8e6523576456582ea35958b3684ed';
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
await new Promise((r) => setTimeout(r, 2000));
const tree = await send('Page.getFrameTree');
const frames = [];
(function walk(n) {
  if (n?.frame) frames.push({ id: n.frame.id, name: n.frame.name, url: String(n.frame.url || '').slice(0, 120) });
  for (const c of n.childFrames || []) walk(c);
})(tree.result?.frameTree || tree.result);
console.log(JSON.stringify(frames, null, 2));
ws.close();
