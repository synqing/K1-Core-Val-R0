#!/usr/bin/env node
import { readFileSync, writeFileSync } from "node:fs";

const CDP_BASE = process.env.EASYEDA_CDP_BASE || "http://127.0.0.1:9223";
const exprPath = process.argv[2];
const outPath = process.argv[3];
if (!exprPath || !outPath) {
  console.error("usage: run_eval_png.mjs <expr.js> <out.png>");
  process.exit(2);
}
const expression = readFileSync(exprPath, "utf8");
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
const reply = await send("Runtime.evaluate", {
  expression,
  returnByValue: true,
  awaitPromise: true,
  timeout: 60000,
});
if (reply.result?.exceptionDetails) {
  throw new Error(reply.result.exceptionDetails.exception?.description || reply.result.exceptionDetails.text);
}
const value = reply.result?.result?.value;
if (!value?.ok || !value.b64) throw new Error("no image: " + JSON.stringify({ ok: value?.ok, bytes: value?.bytes, type: value?.type }));
writeFileSync(outPath, Buffer.from(value.b64, "base64"));
console.log(JSON.stringify({ ok: true, path: outPath, bytes: value.bytes, type: value.type }));
ws.close();
