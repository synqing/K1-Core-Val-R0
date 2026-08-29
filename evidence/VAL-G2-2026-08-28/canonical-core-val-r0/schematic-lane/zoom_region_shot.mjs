#!/usr/bin/env node
import { writeFile } from "node:fs/promises";

const CDP_BASE = process.env.EASYEDA_CDP_BASE || "http://127.0.0.1:9223";
const PROJECT = "64325d0e55e0435abd018defb0089a9b";
const PAGE = "1435cb46f39e48c8a8aadbb84ca81603";
const TAB = `${PAGE}@${PROJECT}`;
const outPath = process.argv[2];
const left = Number(process.argv[3] ?? 2160);
const right = Number(process.argv[4] ?? 2420);
const top = Number(process.argv[5] ?? 3620);
const bottom = Number(process.argv[6] ?? 3840);
if (!outPath?.startsWith("/")) {
  console.error("usage: zoom_region_shot.mjs /abs.png [left right top bottom]");
  process.exit(2);
}

const targets = await (await fetch(`${CDP_BASE}/json/list`, { signal: AbortSignal.timeout(3000) })).json();
const page = targets.find((t) => t.type === "page" && String(t.url).includes("pro.easyeda.com"));
if (!page) throw new Error("No EasyEDA page");
const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
const ctxs = [];
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    pending.get(m.id)(m);
    pending.delete(m.id);
  }
  if (m.method === "Runtime.executionContextCreated") ctxs.push(m.params.context);
};
await new Promise((r) => {
  ws.onopen = r;
});
const send = (method, params = {}) =>
  new Promise((res) => {
    const i = ++id;
    pending.set(i, res);
    ws.send(JSON.stringify({ id: i, method, params }));
  });
await send("Runtime.enable");
await send("Page.enable");
const tree = await send("Page.getFrameTree");
const frames = [];
const walk = (n) => {
  if (n?.frame) frames.push({ id: n.frame.id, url: n.frame.url, name: n.frame.name });
  for (const c of n.childFrames || []) walk(c);
};
walk(tree.result?.frameTree || tree.result);
await new Promise((r) => setTimeout(r, 400));

const schFrame =
  frames.find((f) => String(f.name || "").includes(PAGE) || String(f.url || "").includes(PAGE)) ||
  frames.find((f) => /sch|schematic/i.test(`${f.name} ${f.url}`));
const schCtx =
  ctxs.find((c) => c.auxData?.frameId === schFrame?.id) ||
  ctxs.find((c) => JSON.stringify(c.auxData || {}).includes(PAGE));

const expression = `(() => {
  const root = window._EXTAPI_ROOT_;
  const EC = root && root.dmt_EditorControl;
  if (!EC) return { ok: false, reason: "no EC", hasRoot: Boolean(root), keys: root ? Object.keys(root).slice(0, 20) : [] };
  try {
    void EC.zoomToRegion(${left}, ${right}, ${top}, ${bottom}, ${JSON.stringify(TAB)});
  } catch (e) {
    return { ok: false, err: String(e && e.message || e) };
  }
  return { ok: true, fired: true };
})()`;

const evalParams = { expression, returnByValue: true, awaitPromise: false };
if (schCtx?.id) evalParams.contextId = schCtx.id;
const fired = await send("Runtime.evaluate", evalParams);
const value = fired.result?.result?.value || fired.result || fired;
await new Promise((r) => setTimeout(r, 2200));
const shot = await send("Page.captureScreenshot", { format: "png", fromSurface: true, captureBeyondViewport: false });
if (shot.error || !shot.result?.data) throw new Error(shot.error?.message || "no screenshot");
await writeFile(outPath, Buffer.from(shot.result.data, "base64"));
console.log(JSON.stringify({
  frames: frames.map((f) => ({ name: f.name, url: String(f.url).slice(0, 90) })),
  schFrame: schFrame ? { name: schFrame.name, url: String(schFrame.url).slice(0, 90) } : null,
  ctxCount: ctxs.length,
  schCtx: Boolean(schCtx),
  eval: value,
  path: outPath,
}, null, 2));
ws.close();
