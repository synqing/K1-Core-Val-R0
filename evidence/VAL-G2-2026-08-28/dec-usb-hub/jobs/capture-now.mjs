import { writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '41c8e6523576456582ea35958b3684ed';
const outPath = process.argv[2];
if (!outPath) process.exit(2);
const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const target = targets.find((t) => t.type === 'page' && String(t.url).includes(PROJECT));
if (!target) throw new Error('no hub page');
const ws = new WebSocket(target.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    pending.get(m.id)(m);
    pending.delete(m.id);
  }
};
await new Promise((r) => { ws.onopen = r; });
const send = (method, params = {}) => new Promise((res) => {
  const i = ++id;
  pending.set(i, res);
  ws.send(JSON.stringify({ id: i, method, params }));
});
await send('Page.enable');
const s = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
const buf = Buffer.from(s.result.data, 'base64');
const width = buf.readUInt32BE(16);
const height = buf.readUInt32BE(20);
await writeFile(outPath, buf);
console.log(JSON.stringify({
  ok: true,
  path: outPath,
  width,
  height,
  sha256: createHash('sha256').update(buf).digest('hex').slice(0, 16),
}));
ws.close();
