#!/usr/bin/env node
import { writeFile } from "node:fs/promises";

const CDP_BASE = process.env.EASYEDA_CDP_BASE || "http://127.0.0.1:9223";
const outPath = process.argv[2];
const x = Number(process.argv[3]);
const y = Number(process.argv[4]);
if (!outPath?.startsWith("/") || !Number.isFinite(x) || !Number.isFinite(y)) {
  console.error("usage: click_and_shot.mjs /abs.png x y");
  process.exit(2);
}

const targets = await (await fetch(`${CDP_BASE}/json/list`, { signal: AbortSignal.timeout(3000) })).json();
const page = targets.find((t) => t.type === "page" && String(t.url).includes("pro.easyeda.com"));
if (!page) throw new Error("No EasyEDA page");
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
await send("Input.dispatchMouseEvent", { type: "mouseMoved", x, y, button: "none" });
await send("Input.dispatchMouseEvent", { type: "mousePressed", x, y, button: "left", clickCount: 1 });
await send("Input.dispatchMouseEvent", { type: "mouseReleased", x, y, button: "left", clickCount: 1 });
await new Promise((r) => setTimeout(r, 1500));
const shot = await send("Page.captureScreenshot", { format: "png", fromSurface: true, captureBeyondViewport: false });
if (shot.error || !shot.result?.data) throw new Error(shot.error?.message || "no screenshot");
await writeFile(outPath, Buffer.from(shot.result.data, "base64"));
console.log(JSON.stringify({ ok: true, path: outPath, x, y }));
ws.close();
