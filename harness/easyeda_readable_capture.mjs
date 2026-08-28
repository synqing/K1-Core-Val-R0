#!/usr/bin/env node
// Readable, delta-proven capture of the CANONICAL K1-Core-Val-R0 schematic.
//
// =========================================================================================
// WHY THE OBVIOUS ROUTE DOES NOT WORK  (measured; full record in
// evidence/VAL-G2-2026-08-28/canonical-core-val-r0/EVIDENCE-CAPTURE-RECEIPT.md)
//
// Every _EXTAPI_ROOT_ method is `rpcCall(topic, payload)` over the _MSG_BUS2_EXTAPI_ bus. A
// topic with NO RESPONDER yields a promise that never settles, which from the caller is
// indistinguishable from a slow call — that is why "fire it and hope" looked plausible for
// so long. The bus registry settles it: `bus.pulled` is the set of topics a frame can
// service, and zoomToRegion / zoomTo / zoomToAllPrimitives / zoomToSelectedPrimitives /
// SCH_Primitive.getPrimitivesBBox are in NO frame's responder set. They are not mis-argued;
// nothing answers them. (getCurrentRenderedAreaImage does have a responder, does settle, and
// returns undefined.)
//
// The context binding was also backwards: the sch iframe frame_<PAGE>@<PROJECT> can only
// PUSH requests; the TOP frame's bus ANSWERS. getSplitScreenTree settles in the top frame
// and never in the sch frame. This tool binds the top frame.
//
// =========================================================================================
// WHAT THIS TOOL USES INSTEAD
//
//   VIEW    The editor's OWN toolbar view controls, discovered by title from the DOM at
//           runtime and clicked with synthetic input: "Fit Selection View",
//           "Fit Area Selection View", "Fit All in Window", "Zoom In", "Zoom Out".
//           These are the same commands the dead RPCs were trying to reach.
//   ANCHOR  sch_SelectControl.doSelectPrimitives(ids) evaluated in the TOP frame — but it
//           RETURNS TRUE WHILE SELECTING NOTHING roughly two runs in three on this host, so
//           every selection is confirmed by readback through
//           getAllSelectedPrimitives_PrimitiveId() and retried until the readback agrees.
//           A confirmed selection also LOCATES a primitive on screen: diff the frame before
//           and after selecting and take the bbox of what changed.
//   SCALE   sch_PrimitiveComponent.getAll() returns true schematic coordinates, so two
//           located components give a MEASURED px-per-schematic-unit. Readability is gated
//           on that number, not on a feeling.
//
// Nothing here mutates the document: selection, zoom and fit are view operations, and no
// create/modify/delete/save path is ever called.
//
// =========================================================================================
// THE REFUSAL IS THE POINT. Success requires all three witnesses:
//   (a) the final pixels differ from the pixels before this run acted,
//   (b) the MEASURED final scale >= --min-scale px per schematic unit,
//   (c) the requested target is inside the drawing viewport in the final frame.
// Any failure prints a receipt with the hashes and exits non-zero. A capture this tool
// refuses is not evidence.
//
// Usage:
//   node harness/easyeda_readable_capture.mjs <out.png> select <id[,id...]> [opts]
//   node harness/easyeda_readable_capture.mjs <out.png> region <l> <r> <t> <b> [opts]
// Both modes converge on one flow: Fit All in Window -> calibrate -> (select mode: locate the
// target and pad its bbox into a region) -> Fit Area Selection View + drag -> measure -> gate.
// Options:
//   --min-scale <px/unit>  readability floor, default 1.0 (100-unit part pitch -> 100 px)
//   --pad <units>          schematic padding around a located target, default 200
//   --context <n>          Zoom Out clicks after the area fit, default 1
//   --trace                print the step trace on success as well as on failure
//   --no-mark              skip writing the selection-marked sibling PNG

import { writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { inflateSync } from 'node:zlib';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = process.env.EASYEDA_PROJECT || '64325d0e55e0435abd018defb0089a9b';
const PAGE = process.env.EASYEDA_PAGE || '1435cb46f39e48c8a8aadbb84ca81603';
const TAB = `${PAGE}@${PROJECT}`;
const SETTLE_MS = Number(process.env.EASYEDA_SETTLE_MS || 800);

const sleep = ms => new Promise(r => setTimeout(r, ms));
const sha16 = b => createHash('sha256').update(b).digest('hex').slice(0, 16);

const argv = process.argv.slice(2);
const optIdx = n => argv.indexOf(`--${n}`);
const opt = (n, d) => { const i = optIdx(n); return i < 0 ? d : argv[i + 1]; };
const flag = n => optIdx(n) >= 0;
const positional = argv.filter((a, i) => !a.startsWith('--') && !String(argv[i - 1] || '').startsWith('--'));
const [outPath, mode, ...rest] = positional;
if (!outPath || !['select', 'region'].includes(mode)) {
  console.error('usage: <out.png> select <id,...> [opts]  |  <out.png> region <l> <r> <t> <b> [opts]');
  process.exit(2);
}
const MIN_SCALE = Number(opt('min-scale', 1.0));
const PAD_UNITS = Number(opt('pad', 200));
const CONTEXT_CLICKS = Number(opt('context', 1));
const MARK = !flag('no-mark');
const SHOW_TRACE = flag('trace');
const DEBUG = Boolean(process.env.CAPTURE_DEBUG);

const trace = [];
// Progress goes to stderr so a long run can be watched live; the receipt stays on stdout.
const dbg = (...a) => { if (DEBUG) { trace.push({ dbg: a }); process.stderr.write(`[${new Date().toISOString().slice(11, 19)}] ${a.map(String).join(' ')}\n`); } };
let ws = null;
const die = obj => { try { ws && ws.close(); } catch {} console.log(JSON.stringify({ ...obj, trace }, null, 2)); process.exit(1); };

// ------------------------------------------------------------------ PNG (8-bit RGB/RGBA)
// Anything else is refused rather than silently mis-decoded: a decoder that guesses is a
// witness that cannot be trusted.
function decodePNG(buf) {
  if (buf.subarray(0, 8).toString('binary') !== '\x89PNG\r\n\x1a\n') throw new Error('not a PNG');
  let off = 8, w = 0, h = 0, bitDepth = 0, colorType = 0, interlace = 0;
  const idat = [];
  while (off < buf.length) {
    const len = buf.readUInt32BE(off);
    const type = buf.toString('ascii', off + 4, off + 8);
    const data = buf.subarray(off + 8, off + 8 + len);
    if (type === 'IHDR') { w = data.readUInt32BE(0); h = data.readUInt32BE(4); bitDepth = data[8]; colorType = data[9]; interlace = data[12]; }
    else if (type === 'IDAT') idat.push(data);
    else if (type === 'IEND') break;
    off += 12 + len;
  }
  if (bitDepth !== 8 || ![2, 6].includes(colorType) || interlace !== 0)
    throw new Error(`unsupported PNG (depth ${bitDepth}, color ${colorType}, interlace ${interlace})`);
  const bpp = colorType === 6 ? 4 : 3, stride = w * bpp;
  const raw = inflateSync(Buffer.concat(idat));
  const out = Buffer.alloc(w * h * bpp);
  let p = 0;
  for (let y = 0; y < h; y++) {
    const filter = raw[p++];
    const line = raw.subarray(p, p + stride); p += stride;
    const cur = out.subarray(y * stride, (y + 1) * stride);
    const prev = y ? out.subarray((y - 1) * stride, y * stride) : null;
    for (let i = 0; i < stride; i++) {
      const a = i >= bpp ? cur[i - bpp] : 0, b = prev ? prev[i] : 0, c = prev && i >= bpp ? prev[i - bpp] : 0;
      let v = line[i];
      if (filter === 1) v += a;
      else if (filter === 2) v += b;
      else if (filter === 3) v += (a + b) >> 1;
      else if (filter === 4) {
        const pp = a + b - c, pa = Math.abs(pp - a), pb = Math.abs(pp - b), pc = Math.abs(pp - c);
        v += (pa <= pb && pa <= pc) ? a : (pb <= pc ? b : c);
      } else if (filter !== 0) throw new Error(`bad PNG filter ${filter}`);
      cur[i] = v & 0xff;
    }
  }
  return { w, h, bpp, data: out };
}

// The canvas repaints deterministically — a capture with nothing changed is byte-identical to
// its predecessor (proved with a transient-overlay control) — so the threshold can be low.
// It is not zero: minPixels still rejects a stray pixel or two as "located".
function diffBBox(A, B, rect, { tol = 10, minPixels = 4 } = {}) {
  if (A.w !== B.w || A.h !== B.h) throw new Error('frame size changed mid-run');
  const { w, bpp, data: a } = A, b = B.data;
  let x0 = 1e9, y0 = 1e9, x1 = -1, y1 = -1, n = 0;
  for (let y = rect.top; y < rect.bottom; y++) {
    let i = (y * w + rect.left) * bpp;
    for (let x = rect.left; x < rect.right; x++, i += bpp) {
      const d = Math.max(Math.abs(a[i] - b[i]), Math.abs(a[i + 1] - b[i + 1]), Math.abs(a[i + 2] - b[i + 2]));
      if (d > tol) { n++; if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
    }
  }
  if (n < minPixels) return null;
  return { left: x0, right: x1, top: y0, bottom: y1, pixels: n, cx: (x0 + x1) / 2, cy: (y0 + y1) / 2 };
}

// ------------------------------------------------------------------ CDP session
const targets = await (await fetch(`${CDP_BASE}/json/list`, { signal: AbortSignal.timeout(4000) })).json()
  .catch(e => die({ ok: false, stage: 'attach', reason: String(e) }));
const target = targets.find(t => t.type === 'page' && String(t.url).includes(PROJECT));
if (!target) die({ ok: false, stage: 'attach', reason: `no CDP page target for project ${PROJECT}` });

ws = new WebSocket(target.webSocketDebuggerUrl);
let msgId = 0; const pending = new Map(); const ctxs = [];
ws.onmessage = ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  if (m.method === 'Runtime.executionContextCreated') ctxs.push(m.params.context);
};
await new Promise(r => { ws.onopen = r; });
const send = (method, params = {}) => new Promise(res => {
  const i = ++msgId; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params }));
});
await send('Runtime.enable');
await send('Page.enable');
const tree = await send('Page.getFrameTree');
const rootFrameId = (tree.result?.frameTree || tree.result)?.frame?.id;
await sleep(1600);

let CTX = null;
for (const c of ctxs) {
  if (c.auxData?.frameId !== rootFrameId) continue;
  const r = await send('Runtime.evaluate', { contextId: c.id, expression: 'typeof window._EXTAPI_ROOT_', returnByValue: true });
  if (r.result?.result?.value === 'object') { CTX = c.id; break; }
}
if (CTX === null) die({ ok: false, stage: 'attach', reason: 'no top-frame context exposes _EXTAPI_ROOT_' });

const evaluate = async expression => {
  const r = await send('Runtime.evaluate', { contextId: CTX, expression, returnByValue: true, awaitPromise: false });
  if (r.result?.exceptionDetails)
    return { __throw: (r.result.exceptionDetails.exception?.description || r.result.exceptionDetails.text || '').slice(0, 300) };
  return r.result?.result?.value;
};

// Fire with awaitPromise:false and read the result back from a window global: an unanswered
// RPC would otherwise hang the CDP call until timeout.
let callSeq = 0;
async function hostCall(expr, { timeoutMs = 12000 } = {}) {
  const g = `__cap${callSeq++}`;
  await evaluate(`(() => { const R = window._EXTAPI_ROOT_; window.${g} = undefined;
    try { const p = (${expr});
      if (p && typeof p.then === 'function') p.then(v => { window.${g} = { ok:true, v: v === undefined ? null : v }; },
                                                    e => { window.${g} = { ok:false, e: String((e&&e.message)||e) }; });
      else window.${g} = { ok:true, v:p, sync:true };
    } catch (e) { window.${g} = { ok:false, e: String((e&&e.message)||e) }; }
    return 1; })()`);
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const v = await evaluate(`window.${g} ?? null`);
    if (v) { await evaluate(`delete window.${g}`); return v; }
    await sleep(150);
  }
  await evaluate(`delete window.${g}`);
  return { ok: false, unanswered: true, note: 'RPC topic has no responder in this build' };
}

const captureRaw = async () => {
  const s = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
  if (!s.result?.data) throw new Error(s.error?.message || 'captureScreenshot returned no data');
  return Buffer.from(s.result.data, 'base64');
};
const captureImg = async () => decodePNG(await captureRaw());

// ------------------------------------------------------------------ viewport + toolbar
// The drawing viewport is derived from BOTH rulers, never from the window height. A panel
// opening at the bottom (the DRC results pane does exactly this) shrinks the canvas, and a
// viewport rect that assumed "window minus a status bar" then searched for highlights in a
// region the drawing no longer occupies — every probe came back empty.
const geom = await evaluate(`(() => {
  const pick = sel => [...document.querySelectorAll(sel)].map(c => c.getBoundingClientRect())
    .filter(r => r.width > 4 && r.height > 4);
  const rulers = [...document.querySelectorAll('canvas.rulerh')]
    .filter(c => c.getBoundingClientRect().width > 100);
  if (!rulers.length) return null;
  const ruler = rulers.reduce((m, c) => c.getBoundingClientRect().width < m.getBoundingClientRect().width ? c : m);
  const h = ruler.getBoundingClientRect();
  // Walk up to the container that actually holds the drawing surface; its height tracks any
  // bottom panel (DRC results) opening or closing.
  let el = ruler.parentElement, box = null;
  while (el) { const r = el.getBoundingClientRect(); if (r.height > 200 && r.width > 300) { box = r; break; } el = el.parentElement; }
  if (!box) return null;
  return { left: Math.round(h.x), top: Math.round(h.y + h.height), right: Math.round(h.x + h.width),
           bottom: Math.round(box.y + box.height), dpr: devicePixelRatio };
})()`);
if (!geom) die({ ok: false, stage: 'geometry', reason: 'could not find both drawing-area rulers' });
if (geom.dpr !== 1) die({ ok: false, stage: 'geometry', reason: `devicePixelRatio ${geom.dpr} != 1; CSS-to-pixel mapping unproven` });
const RECT = { left: geom.left + 4, top: geom.top + 4, right: geom.right - 4, bottom: geom.bottom - 4 };
if (RECT.right - RECT.left < 300 || RECT.bottom - RECT.top < 200)
  die({ ok: false, stage: 'geometry', reason: 'drawing viewport is too small to capture readable evidence', RECT });
const RECT_W = RECT.right - RECT.left, RECT_H = RECT.bottom - RECT.top;
const CENTRE = { x: RECT.left + RECT_W / 2, y: RECT.top + RECT_H / 2 };
const inRect = (x, y) => x >= RECT.left && x <= RECT.right && y >= RECT.top && y <= RECT.bottom;

// The view controls are found by their own tooltips, not by hardcoded pixel positions.
const BUTTONS = await evaluate(`(() => {
  const want = ['Zoom In','Zoom Out','Fit All in Window','Fit Selection View','Fit Area Selection View'];
  const out = {};
  for (const el of document.querySelectorAll('[title]')) {
    const t = el.getAttribute('title') || '';
    const hit = want.find(w => t.startsWith(w));
    if (!hit || out[hit]) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 6 || r.height < 6) continue;
    out[hit] = { x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2), title: t };
  }
  return out;
})()`);
for (const need of ['Zoom In', 'Zoom Out', 'Fit All in Window', 'Fit Selection View'])
  if (!BUTTONS?.[need]) die({ ok: false, stage: 'toolbar', reason: `view control "${need}" not found in the DOM`, found: BUTTONS });
trace.push({ step: 'toolbar', controls: Object.fromEntries(Object.entries(BUTTONS).map(([k, v]) => [k, [v.x, v.y]])) });

async function clickAt(x, y) {
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y, button: 'none' });
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
  await sleep(900);
}
const clickButton = async name => { const b = BUTTONS[name]; if (!b) return false; await clickAt(b.x, b.y); return true; };
// A rubber band has to be DRAGGED, not teleported: with no delay between the synthetic
// moves the editor never tracked the band and the area fit did nothing at all (measured:
// scale 0.2092 before, 0.2091 after). Steps and pauses are what make it a drag.
async function dragOnCanvas(x0, y0, x1, y1) {
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: x0, y: y0, button: 'none' });
  await sleep(250);
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: x0, y: y0, button: 'left', clickCount: 1 });
  await sleep(250);
  const steps = 14;
  for (let i = 1; i <= steps; i++) {
    await send('Input.dispatchMouseEvent', { type: 'mouseMoved', button: 'left', buttons: 1,
      x: Math.round(x0 + (x1 - x0) * i / steps), y: Math.round(y0 + (y1 - y0) * i / steps) });
    await sleep(70);
  }
  await sleep(250);
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: Math.round(x1), y: Math.round(y1), button: 'left', clickCount: 1 });
  await sleep(1400);
}

// ------------------------------------------------------------------ selection (readback-gated)
await hostCall(`R.dmt_EditorControl.activateDocument(${JSON.stringify(TAB)})`);
// Leave any modal tool (a previous run's area-select rubber band, a placement tool) before
// driving the view: a live tool mode changes what clicks and drags mean.
for (let i = 0; i < 3; i++) {
  await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
  await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
  await sleep(200);
}

// doSelectPrimitives RETURNS TRUE WHILE SELECTING NOTHING. The return code is discarded; the
// selection is confirmed by readback and retried until the readback agrees.
async function selectIds(ids) {
  for (let attempt = 0; attempt < 5; attempt++) {
    if (!ids.length) await hostCall(`R.sch_SelectControl.clearSelected ? R.sch_SelectControl.clearSelected() : R.sch_SelectControl.doSelectPrimitives([])`);
    else await hostCall(`R.sch_SelectControl.doSelectPrimitives(${JSON.stringify(ids)})`, { timeoutMs: 20000 });
    const rb = await hostCall(`R.sch_SelectControl.getAllSelectedPrimitives_PrimitiveId()`);
    const got = Array.isArray(rb.v) ? rb.v : null;
    if (got && (ids.length ? got.length > 0 : got.length === 0)) return { ok: true, got, attempts: attempt + 1 };
    await sleep(300);
  }
  return { ok: false, got: null };
}

async function locateOnce(ids, settle) {
  await selectIds([]); await sleep(settle);
  const a = await captureImg();
  const sel = await selectIds(ids); await sleep(settle);
  const bRaw = await captureRaw();
  return { box: diffBBox(a, decodePNG(bRaw), RECT), selectOk: sel.ok, selected: sel.got, marked: bRaw };
}
// A null result is retried once with a longer settle, so "no delta" means "not on screen",
// never "the editor had not repainted yet".
async function locate(ids) {
  const first = await locateOnce(ids, SETTLE_MS);
  return first.box ? first : locateOnce(ids, SETTLE_MS * 2.5);
}

// Anchors come from WIRES, not components. sch_PrimitiveComponent enumerates a DIFFERENT id
// namespace ("$1I72") which doSelectPrimitives accepts and then silently ignores — it returns
// true and selects nothing, every time, for every component. sch_PrimitiveWire returns real
// primitive ids ("e968") that select correctly AND carries the geometry, so one call gives
// both halves of an anchor. Note the wire API reports y with the OPPOSITE SIGN to the
// component API and to the ids used elsewhere in this programme; it is negated here so the
// tool's schematic coordinates match the rest of the evidence trail.
const wiresRes = await hostCall(`R.sch_PrimitiveWire.getAll().then(v => v.map(w => ({
  id: w.primitiveId, line: (w.line && w.line[0]) || null })))`, { timeoutMs: 30000 });
if (!wiresRes.ok || !Array.isArray(wiresRes.v)) die({ ok: false, stage: 'anchors', got: wiresRes });
const ANCHORS = wiresRes.v
  .filter(w => w.id && Array.isArray(w.line) && w.line.length >= 4 && w.line.every(Number.isFinite))
  .map(w => ({ id: w.id, x: (w.line[0] + w.line[2]) / 2, y: -(w.line[1] + w.line[3]) / 2,
    len: Math.abs(w.line[2] - w.line[0]) + Math.abs(w.line[3] - w.line[1]) }))
  .filter(w => w.len >= 20);
if (ANCHORS.length < 2) die({ ok: false, stage: 'anchors', reason: `only ${ANCHORS.length} usable wire anchors` });
trace.push({ step: 'anchors', wires: wiresRes.v.length, usable: ANCHORS.length });

// ------------------------------------------------------------------ transform
const apply = (t, p) => ({ x: t.ox + t.sx * p.x, y: t.oy + t.sy * p.y });
const invert = (t, s) => ({ x: (s.x - t.ox) / t.sx, y: (s.y - t.oy) / t.sy });

// Anchors are probed ONE AT A TIME: a bulk selection was measured to report success while
// selecting nothing, so it is not trusted as a search primitive.
// An anchor must produce a highlight that is both substantial and COMPACT. A handful of
// changed pixels can be repaint noise, and a sheet-spanning delta means the selection pulled
// in more than the wire (selecting a wire can select its whole net group) — in either case
// the centroid is not that wire's position and must not be used as an anchor.
// The span limit is VIEWPORT-RELATIVE, not absolute. Its job is to reject a delta that covers the
// whole sheet (selecting a wire can pull in its entire net group), not to reject a large highlight:
// once zoomed in, a single ordinary wire legitimately spans several hundred pixels, and a fixed
// 420 px ceiling started throwing away every valid anchor at exactly the zoom we need.
const ANCHOR_MIN_PIXELS = 12;
const ANCHOR_MAX_SPAN_PX = () => 0.7 * Math.min(RECT_W, RECT_H);
function anchorUsable(box) {
  if (!box) return false;
  const lim = ANCHOR_MAX_SPAN_PX();
  return box.pixels >= ANCHOR_MIN_PIXELS
    && (box.right - box.left) <= lim && (box.bottom - box.top) <= lim;
}
async function findVisible(candidates, label, limit = 26) {
  for (const [i, c] of candidates.slice(0, limit).entries()) {
    const l = await locate([c.id]);
    const ok = anchorUsable(l.box);
    dbg('probe', label, i, c.id, 'sel=' + l.selectOk, 'px=' + (l.box ? l.box.pixels : 0),
      'span=' + (l.box ? `${l.box.right - l.box.left}x${l.box.bottom - l.box.top}` : '-'), ok ? 'USE' : 'skip');
    if (ok) return { comp: c, box: l.box };
  }
  return null;
}
const byNearest = seed => (p, q) => (seed
  ? Math.hypot(p.x - seed.x, p.y - seed.y) - Math.hypot(q.x - seed.x, q.y - seed.y)
  : q.len - p.len);

// Both axes are solved independently and cross-checked: if |sx| and |sy| disagree the model
// is wrong, and the tool says so rather than reporting a scale it cannot defend.
//
// The second anchor is chosen to MAXIMISE separation on both axes, not to be the nearest one
// that clears a small threshold. A close pair was measured to produce a 2.5x scale error: the
// centroid of a highlight is only good to a pixel or two, so a five-pixel baseline is mostly
// noise. Separation is also re-checked in screen pixels afterwards, and a short baseline is
// rejected outright rather than reported as a scale.
const MIN_BASELINE_PX = 60;
// The TARGET must never be one of its own scale anchors. It is circular, and a short primitive
// gives a baseline of a few tens of pixels where the centroid is only good to a pixel or two.
const EXCLUDE_FROM_ANCHORS = new Set();
async function measureTransform(seed, prev) {
  const usable = ANCHORS.filter(c => !EXCLUDE_FROM_ANCHORS.has(c.id));
  const predicted = prev ? usable.filter(c => { const p = apply(prev, c); return inRect(p.x, p.y); }) : [];
  const pool = predicted.length >= 8 ? predicted : usable;
  const a = await findVisible([...pool].sort(byNearest(seed)), 'A');
  if (!a) return null;
  const partners = pool
    .filter(c => c.id !== a.comp.id && !EXCLUDE_FROM_ANCHORS.has(c.id))
    .map(c => ({ c, sep: Math.min(Math.abs(c.x - a.comp.x), Math.abs(c.y - a.comp.y)) }))
    .filter(o => o.sep > 0)
    .sort((p, q) => q.sep - p.sep)
    .map(o => o.c);
  let b = await findVisible(partners, 'B', 14);
  if (!b && pool !== ANCHORS) {
    // The prediction that built `pool` may be stale (a pan moves the view under it), so fall
    // back to an unfiltered search rather than concluding nothing is visible.
    const wide = ANCHORS.filter(c => c.id !== a.comp.id && !EXCLUDE_FROM_ANCHORS.has(c.id)).sort(byNearest(a.comp));
    b = await findVisible(wide, 'B-wide', 20);
  }
  if (!b) return null;
  const t = finish(a, b);
  if (!t || t.__bad) return t;
  // VERIFY, do not assume. Two points always fit a transform exactly, so a two-point fit can
  // never disagree with itself. A third, independent anchor is located and its predicted
  // position compared with where it actually is; a transform that fails this is discarded
  // rather than reported. This is the check that caught a 3x scale error.
  const third = ANCHORS
    .filter(c => c.id !== a.comp.id && c.id !== b.comp.id && !EXCLUDE_FROM_ANCHORS.has(c.id))
    .map(c => ({ c, p: apply(t, c) }))
    .filter(o => inRect(o.p.x, o.p.y)
      && Math.hypot(o.p.x - a.box.cx, o.p.y - a.box.cy) > 120
      && Math.hypot(o.p.x - b.box.cx, o.p.y - b.box.cy) > 120)
    .map(o => o.c);
  const c3 = await findVisible(third, 'V', 10);
  if (!c3) return { __bad: 'no third anchor available to verify the transform' };
  const pred = apply(t, c3.comp);
  const residual = Math.hypot(pred.x - c3.box.cx, pred.y - c3.box.cy);
  dbg('verify', c3.comp.id, 'residual=' + Math.round(residual));
  if (residual > 30) return { __bad: 'transform failed third-anchor verification', residual: Math.round(residual),
    anchors: [a.comp.id, b.comp.id, c3.comp.id] };
  return { ...t, verified_residual_px: Math.round(residual), verify_anchor: c3.comp.id };
  function finish(p, q) {
    const dpx = Math.abs(q.box.cx - p.box.cx), dpy = Math.abs(q.box.cy - p.box.cy);
    if (dpx < MIN_BASELINE_PX || dpy < MIN_BASELINE_PX)
      return { __bad: 'anchor baseline too short to measure a scale', dpx, dpy, anchors: [p.comp.id, q.comp.id] };
    const sx = (q.box.cx - p.box.cx) / (q.comp.x - p.comp.x);
    const sy = (q.box.cy - p.box.cy) / (q.comp.y - p.comp.y);
    if (!Number.isFinite(sx) || !Number.isFinite(sy) || !sx || !sy) return null;
    const agree = Math.abs(Math.abs(sx) - Math.abs(sy)) / Math.max(Math.abs(sx), Math.abs(sy));
    if (agree > 0.15) return { __bad: 'sx/sy disagree', sx, sy, agree };
    return { sx, sy, ox: p.box.cx - sx * p.comp.x, oy: p.box.cy - sy * p.comp.y,
      scale: (Math.abs(sx) + Math.abs(sy)) / 2, anchors: [p.comp.id, q.comp.id],
      baseline_px: [Math.round(dpx), Math.round(dpy)] };
  }
}

// ------------------------------------------------------------------ run
const first = await captureRaw();
const firstSha = sha16(first);

let targetIds = null, region = null, seed = null;
if (mode === 'select') {
  targetIds = String(rest[0] || '').split(',').map(s => s.trim()).filter(Boolean);
  if (!targetIds.length) die({ ok: false, stage: 'args', reason: 'select needs at least one primitive id' });
} else {
  const [l, r, t, b] = rest.map(Number);
  if (![l, r, t, b].every(Number.isFinite)) die({ ok: false, stage: 'args', reason: 'region needs four numeric bounds' });
  region = { l: Math.min(l, r), r: Math.max(l, r), t: Math.min(t, b), b: Math.max(t, b) };
}

// DO NOT calibrate at whole-sheet zoom. Measured: at Fit All a wire's selection highlight is
// a handful of scattered antialiased pixels spread over 200-360 px, so its centroid is noise
// and a transform built on it came out 3x wrong. Instead, let the EDITOR do the navigation —
// aim the view with the editor's own area-fit, using coordinates read from the live API.
// Recovery preamble. A bottom panel (the DRC results pane) both shrinks the canvas and stops
// the selection highlight from rendering at all — measured: with it open, deselecting a
// confirmed selection changed zero pixels; collapsing it and refocusing the document tab
// brought the highlight back. Both are view-only actions.
if (RECT.bottom - RECT.top < 700) {
  const drcTab = await evaluate(`(() => { for (const el of document.querySelectorAll('*')) {
    if (el.children.length === 0 && (el.textContent || '').trim() === 'DRC') {
      const r = el.getBoundingClientRect();
      if (r.width > 10 && r.height > 10 && r.y > innerHeight - 60) return { x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2) };
    } } return null; })()`);
  if (drcTab) { await clickAt(drcTab.x, drcTab.y); trace.push({ step: 'collapse-bottom-panel', at: drcTab }); }
}
const docTab = await evaluate(`(() => { for (const el of document.querySelectorAll('*')) {
  if (el.children.length === 0 && /Schematic/.test(el.textContent || '')) {
    const r = el.getBoundingClientRect();
    if (r.y < 100 && r.width > 40) return { x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2) };
  } } return null; })()`);
if (docTab) { await clickAt(docTab.x, docTab.y); trace.push({ step: 'focus-document-tab', at: docTab }); }

// The target's schematic coordinates are READ, not inferred from pixels:
// sch_PrimitiveWire.get for wires, sch_PrimitiveComponent.get for components. Wire y is
// reported with the opposite sign to component y and is normalised here.
async function geometryOf(id) {
  const w = await hostCall(`R.sch_PrimitiveWire.get(${JSON.stringify(id)})`);
  const wv = w.ok && w.v ? (Array.isArray(w.v) ? w.v[0] : w.v) : null;
  if (wv && Array.isArray(wv.line) && wv.line.length) {
    const xs = [], ys = [];
    for (const seg of wv.line) for (let i = 0; i + 1 < seg.length; i += 2) { xs.push(seg[i]); ys.push(-seg[i + 1]); }
    if (xs.length) return { l: Math.min(...xs), r: Math.max(...xs), t: Math.min(...ys), b: Math.max(...ys), kind: 'wire' };
  }
  const c = await hostCall(`R.sch_PrimitiveComponent.get(${JSON.stringify(id)})`);
  const co = c.ok && c.v ? (Array.isArray(c.v) ? c.v[0] : c.v) : null;
  if (co && Number.isFinite(co.x) && Number.isFinite(co.y))
    return { l: co.x, r: co.x, t: co.y, b: co.y, kind: 'component' };
  return null;
}

if (targetIds) {
  const sel = await selectIds(targetIds);
  if (!sel.ok) die({ ok: false, stage: 'select',
    reason: 'selection never confirmed by readback — the ids may not exist on this page',
    ids: targetIds, sha256_before_run: firstSha });
  trace.push({ step: 'selected', requested: targetIds, readback: sel.got, attempts: sel.attempts });
  for (const id of [...targetIds, ...(sel.got || [])]) EXCLUDE_FROM_ANCHORS.add(id);
  let g = null;
  for (const id of [...targetIds, ...(sel.got || [])]) {
    g = await geometryOf(id);
    if (g) { trace.push({ step: 'target-geometry', id, ...g }); break; }
  }
  if (!g) die({ ok: false, stage: 'geometry-of-target',
    reason: 'no live API returned coordinates for the requested ids, so the view cannot be aimed at them',
    ids: targetIds, readback: sel.got });
  region = { l: g.l - PAD_UNITS, r: g.r + PAD_UNITS, t: g.t - PAD_UNITS, b: g.b + PAD_UNITS };
}
seed = { x: (region.l + region.r) / 2, y: (region.t + region.b) / 2 };
trace.push({ step: 'region-resolved', region, seed });

// Navigate with the editor's own controls: fit the whole sheet, measure a VERIFIED transform
// there, then drag the "Fit Area Selection View" rubber band over the projected region.
await selectIds([]);
await clickButton('Fit All in Window');
const T0 = await measureTransform(seed, null);
if (!T0 || T0.__bad) die({ ok: false, stage: 'calibrate',
  reason: 'could not measure a verified schematic->screen transform at fit-all',
  detail: T0, sha256_before_run: firstSha, viewport: RECT });
trace.push({ step: 'calibrated-at-fit-all', scale: +T0.scale.toFixed(4), anchors: T0.anchors,
  verified_residual_px: T0.verified_residual_px });

{
  const p0 = apply(T0, { x: region.l, y: region.t }), p1 = apply(T0, { x: region.r, y: region.b });
  const x0 = Math.max(RECT.left + 2, Math.min(p0.x, p1.x)), x1 = Math.min(RECT.right - 2, Math.max(p0.x, p1.x));
  const y0 = Math.max(RECT.top + 2, Math.min(p0.y, p1.y)), y1 = Math.min(RECT.bottom - 2, Math.max(p0.y, p1.y));
  if (!(x1 - x0 > 6 && y1 - y0 > 6)) die({ ok: false, stage: 'region',
    reason: 'region does not project onto the drawing viewport at fit-all', region, projected: { x0, y0, x1, y1 } });
}

// CLIMB FIRST, MEASURE ONCE. Measuring between every Zoom In click made the climb fragile: a
// single failed anchor re-acquisition aborted the loop and left the scale far short, which is
// what produced repeated 0.2 px/unit refusals. Measurement is the GATE, not the controller.
// The number of clicks is computed from the fit-all scale and the measured per-click ratio
// (~1.2, decaying), then the achieved scale is measured once and gated. Nothing here can make
// an unreadable capture pass: if the climb undershoots, the scale witness still fails.
const CLICK_RATIO = 1.2;
let T = T0;
const needed = Math.ceil(Math.log((MIN_SCALE * 1.15) / T0.scale) / Math.log(CLICK_RATIO));
const clicks = Math.max(0, Math.min(30, needed));
trace.push({ step: 'zoom-climb', from_scale: +T0.scale.toFixed(4), clicks, assumed_ratio: CLICK_RATIO });
for (let i = 0; i < clicks; i++) await clickButton('Zoom In');

// Measure the achieved scale. If the framing is too tight for two anchors, widen a notch and
// retry rather than reporting a scale we cannot defend.
for (let i = 0; i < 6; i++) {
  const m = await measureTransform(seed, null);
  if (m && !m.__bad) { T = m; break; }
  trace.push({ step: 'measure-retry', attempt: i + 1, detail: m });
  await clickButton('Zoom Out');
}

if (!T || T.__bad) die({ ok: false, stage: 'measure',
  reason: 'could not measure the achieved scale — readability is unproven, so this is not evidence',
  detail: T, sha256_before_run: firstSha });
trace.push({ step: 'measured', scale: +T.scale.toFixed(4), anchors: T.anchors,
  verified_residual_px: T.verified_residual_px });

// Raise the scale until it clears the readability floor. The area fit alone was measured to
// under-zoom, so the floor is reached by the editor's own Zoom In, re-measuring every step:
// the loop stops on the MEASURED scale, never on a click count.
for (let i = 0; i < 30 && T.scale < MIN_SCALE; i++) {
  await clickButton('Zoom In');
  // Pass the last good transform: after zooming in, most anchors are off screen, and a
  // search that is not filtered by a prediction walks dozens of invisible candidates.
  const next = (await measureTransform(seed, T)) || (await measureTransform(seed, null));
  if (!next || next.__bad) { trace.push({ step: 'raise-scale-lost-calibration', attempt: i + 1, detail: next }); break; }
  const gain = next.scale / T.scale;
  T = next;
  trace.push({ step: 'raise-scale', attempt: i + 1, scale: +T.scale.toFixed(4), gain: +gain.toFixed(4) });
  if (gain < 1.02) { trace.push({ step: 'raise-scale-saturated', reason: 'Zoom In gained under 2% — the control has hit its limit' }); break; }
  const p = apply(T, seed);
  if (!inRect(p.x, p.y)) { trace.push({ step: 'raise-scale-stopped', reason: 'target left the viewport' }); break; }
}

let markedPng = null, finalBox = null;
if (targetIds) { const loc = await locate(targetIds); finalBox = loc.box; markedPng = loc.marked; }
await selectIds([]); await sleep(SETTLE_MS);
const finalPng = await captureRaw();
const finalSha = sha16(finalPng);
const centreScreen = apply(T, seed);

// FOURTH WITNESS — is the highlight on the thing that was asked for?
// Selecting a wire makes the editor select its parent NET GROUP, so the readback id legitimately
// differs from the requested id (e153914 -> e153912). An id-equality gate would refuse every wire
// target, including both lead repairs. So correctness is checked GEOMETRICALLY instead: project the
// requested primitive's OWN coordinates (read from sch_PrimitiveWire/Component.get, independent of
// the selection) and require them to land inside the highlight. A highlight on some other object
// fails this; a highlight on the wire's own net group passes it.
const HL_PAD = 40;
const highlight_on_target = !targetIds ? true : Boolean(finalBox
  && centreScreen.x >= finalBox.left - HL_PAD && centreScreen.x <= finalBox.right + HL_PAD
  && centreScreen.y >= finalBox.top - HL_PAD && centreScreen.y <= finalBox.bottom + HL_PAD);
const witness = {
  pixels_changed: finalSha !== firstSha,
  scale_ok: T.scale >= MIN_SCALE,
  target_in_view: targetIds ? Boolean(finalBox) : inRect(centreScreen.x, centreScreen.y),
  highlight_on_target,
};
const receipt = {
  mode, out: outPath, page_tab: TAB, context_id: CTX,
  view_controls_used: targetIds
    ? ['Fit Selection View', `Zoom Out x${CONTEXT_CLICKS}`]
    : ['Fit Selection View (nearest anchor)', 'Fit Area Selection View + drag'],
  target_seed: seed,
  measured_scale_px_per_unit: +T.scale.toFixed(4), min_scale: MIN_SCALE, scale_anchors: T.anchors,
  requested: mode === 'select' ? { ids: targetIds } : { region },
  final_target_screen_bbox: finalBox, viewport: RECT,
  sha256_before_run: firstSha, sha256_final: finalSha, witness,
};
if (!(witness.pixels_changed && witness.scale_ok && witness.target_in_view && witness.highlight_on_target))
  die({ ok: false, stage: 'witness', reason: 'a witness failed — this capture is NOT evidence', ...receipt });

const img = decodePNG(finalPng);
await writeFile(outPath, finalPng);
const markPath = MARK && markedPng ? outPath.replace(/\.png$/i, '') + '-marked.png' : null;
if (markPath) await writeFile(markPath, markedPng);
console.log(JSON.stringify({ ok: true, width: img.w, height: img.h, marked_path: markPath, ...receipt,
  ...(SHOW_TRACE ? { trace } : {}) }, null, 2));
ws.close();
