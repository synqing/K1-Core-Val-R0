#!/usr/bin/env node
// Capture EasyEDA chrome only if live MAIN 64325d0e is focused.
import { writeFile } from "node:fs/promises";

const CDP_BASE = process.env.EASYEDA_CDP_BASE || "http://127.0.0.1:9223";
const PROJECT = "64325d0e55e0435abd018defb0089a9b";
const PAGE = "1435cb46f39e48c8a8aadbb84ca81603";
const outPath = process.argv[2];
if (!outPath?.startsWith("/")) {
  console.error("usage: capture_main_png.mjs /abs/out.png");
  process.exit(2);
}

const targets = await (await fetch(`${CDP_BASE}/json/list`, { signal: AbortSignal.timeout(3000) })).json();
const page = targets.find((t) => t.type === "page" && String(t.url).includes("pro.easyeda.com"));
if (!page) throw new Error("No EasyEDA page target");

const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    pending.get(m.id)(m);
    pending.delete(m.id);
  }
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

const evalPage = async (expression, awaitPromise = true) => {
  const reply = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise });
  if (reply.result?.exceptionDetails) {
    throw new Error(reply.result.exceptionDetails.exception?.description || reply.result.exceptionDetails.text);
  }
  return reply.result?.result?.value;
};

const ident = await evalPage(`(async () => {
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const doc = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  return { project: info.uuid, name: info.name || info.friendlyName, doc: doc && doc.uuid, title: document.title };
})()`);
if (ident.project !== PROJECT || ident.doc !== PAGE) {
  throw new Error(`identity mismatch ${JSON.stringify(ident)}`);
}

const shot = await send("Page.captureScreenshot", { format: "png", fromSurface: true, captureBeyondViewport: false });
if (shot.error || !shot.result?.data) throw new Error(shot.error?.message || "no screenshot data");
const buf = Buffer.from(shot.result.data, "base64");
await writeFile(outPath, buf);
console.log(JSON.stringify({ ok: true, path: outPath, bytes: buf.length, title: ident.title, project: ident.project }));
ws.close();
