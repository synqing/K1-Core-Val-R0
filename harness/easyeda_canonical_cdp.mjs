// Shared read-only CDP attachment for the CANONICAL K1-Core-Val-R0 schematic page.
//
// Encodes the three measured traps so no caller has to rediscover them:
//   1. Host promises returned by _EXTAPI_ROOT_ methods DO NOT SETTLE. Every evaluate must
//      use awaitPromise:false. To read an async result, stash it on a window global from a
//      .then() callback and POLL for it (see pollGlobal).
//   2. The canonical schematic renders in frame_<PAGE>@<PROJECT>, whose execution context
//      arrives asynchronously. Bind contextId explicitly or the eval silently runs in the
//      top frame and does nothing.
//   3. A call that returns without throwing is NOT evidence. Callers must compare a
//      before/after witness.
//
// This module MUTATES NOTHING. It only enables domains, evaluates, and screenshots.

import { createHash } from 'node:crypto';

export const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
export const PROJECT = process.env.EASYEDA_PROJECT || '64325d0e55e0435abd018defb0089a9b';
export const PAGE = process.env.EASYEDA_PAGE || '1435cb46f39e48c8a8aadbb84ca81603';
export const TAB = `${PAGE}@${PROJECT}`;
const CTX_WAIT_MS = Number(process.env.EASYEDA_CTX_WAIT_MS || 1800);

export const sha16 = buf => createHash('sha256').update(buf).digest('hex').slice(0, 16);
export const sleep = ms => new Promise(r => setTimeout(r, ms));

export async function attach() {
  const targets = await (await fetch(`${CDP_BASE}/json/list`, { signal: AbortSignal.timeout(3000) })).json();
  const target = targets.find(t => t.type === 'page' && String(t.url).includes(PROJECT));
  if (!target) throw new Error(`no CDP page target for canonical project ${PROJECT}`);

  const ws = new WebSocket(target.webSocketDebuggerUrl);
  let id = 0;
  const pending = new Map();
  const ctxs = [];
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
    if (m.method === 'Runtime.executionContextCreated') ctxs.push(m.params.context);
  };
  await new Promise(r => { ws.onopen = r; });
  const send = (method, params = {}) => new Promise(res => {
    const i = ++id; pending.set(i, res);
    ws.send(JSON.stringify({ id: i, method, params }));
  });

  await send('Runtime.enable');
  await send('Page.enable');
  const tree = await send('Page.getFrameTree');
  const frames = [];
  (function walk(n) { if (n?.frame) frames.push(n.frame); for (const c of n.childFrames || []) walk(c); })(
    tree.result?.frameTree || tree.result);
  await sleep(CTX_WAIT_MS);

  const canonFrame = frames.find(f => String(f.name || '').includes(PAGE));
  if (!canonFrame) throw new Error(`canonical schematic frame not found (frame_${TAB})`);
  const ctx = ctxs.find(c => c.auxData?.frameId === canonFrame.id);
  if (!ctx) throw new Error('canonical frame execution context never arrived — raise EASYEDA_CTX_WAIT_MS');

  // awaitPromise:false is mandatory — host promises do not settle.
  const evaluate = async (expression, { contextId = ctx.id } = {}) => {
    const r = await send('Runtime.evaluate',
      { contextId, expression, returnByValue: true, awaitPromise: false });
    if (r.result?.exceptionDetails) {
      return { __throw: r.result.exceptionDetails.exception?.description || r.result.exceptionDetails.text };
    }
    return r.result?.result?.value;
  };

  // Fire an async host call whose promise never settles for CDP, then poll a window global
  // that its own .then() writes. This is the only way to read an async host result.
  const pollGlobal = async (name, { timeoutMs = 8000, everyMs = 250 } = {}) => {
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
      const v = await evaluate(`(() => { const g = window[${JSON.stringify(name)}];
        return g === undefined ? null : g; })()`);
      if (v !== null && v !== undefined) return v;
      await sleep(everyMs);
    }
    return { __timeout: true, global: name, timeoutMs };
  };

  const capture = async (clip) => {
    const params = { format: 'png', fromSurface: true, captureBeyondViewport: false };
    if (clip) params.clip = { ...clip, scale: clip.scale ?? 1 };
    const s = await send('Page.captureScreenshot', params);
    if (s.error || !s.result?.data) throw new Error(s.error?.message || 'captureScreenshot returned no data');
    return Buffer.from(s.result.data, 'base64');
  };

  return { send, evaluate, pollGlobal, capture, ctxId: ctx.id, frameId: canonFrame.id,
    close: () => ws.close() };
}

export function pngDims(buf) {
  if (buf.subarray(0, 8).toString('binary') !== '\x89PNG\r\n\x1a\n') throw new Error('not a PNG');
  return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
}
