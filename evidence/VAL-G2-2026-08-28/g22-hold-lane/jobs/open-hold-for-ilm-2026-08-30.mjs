#!/usr/bin/env node
// Switch EasyEDA from saved canonical 64325d0e to G2.2 HOLD 55ed9ee9.
// Does not mutate schematic primitives. Refuses if canonical is unsaved.
import { writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const HOLD = '55ed9ee948734a0e903f37744b51f3b8';
const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
const HUB = '41c8e6523576456582ea35958b3684ed';
const ORACLE = 'dcd7e3cab2a24b9aa6e531d2b62e1b6f';
const OUT = new URL('./open-hold-for-ilm-2026-08-30.json', import.meta.url);

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const pages = targets.filter((t) => t.type === 'page' && String(t.url).includes('pro.easyeda.com'));
for (const p of pages) {
  console.error('page', (p.title || '').slice(0, 90), (p.url || '').slice(0, 140));
}
const page = pages.find((t) => String(t.url).includes(HOLD))
  || pages.find((t) => String(t.url).includes(LIVE))
  || pages[0];
if (!page) throw new Error('no EasyEDA editor page');

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
await new Promise((r) => { ws.onopen = r; });
const send = (method, params) => new Promise((res) => {
  const i = ++id;
  pending.set(i, res);
  ws.send(JSON.stringify({ id: i, method, params }));
});

const expr = `(async () => {
  const eda = globalThis._EXTAPI_ROOT_
    || (Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda) || {}).eda;
  if (!eda || !eda.dmt_Project || !eda.dmt_Project.openProject) {
    return { ok: false, reason: 'openProject API absent' };
  }
  const LIVE = ${JSON.stringify(LIVE)};
  const HOLD = ${JSON.stringify(HOLD)};
  const PAGE = ${JSON.stringify(PAGE)};
  const slim = (info) => {
    if (!info) return null;
    return {
      uuid: info.uuid,
      friendlyName: info.friendlyName,
      name: info.name,
    };
  };
  const before = await eda.dmt_Project.getCurrentProjectInfo();
  if (before && before.uuid === HOLD) {
    return { ok: true, alreadyHold: true, current: slim(before), title: document.title };
  }
  if (before && (before.uuid === ${JSON.stringify(HUB)} || before.uuid === ${JSON.stringify(ORACLE)})) {
    return { ok: false, reason: 'FORBIDDEN_CURRENT', uuid: before.uuid };
  }
  const unsaved = Array.isArray(before && before.data) ? false : false;
  let opened = null;
  try { opened = await eda.dmt_Project.openProject(HOLD); }
  catch (e) { return { ok: false, reason: 'openProject threw', err: String(e && e.message || e).slice(0, 240), before: slim(before) }; }
  await new Promise((r) => setTimeout(r, 5000));
  let current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== HOLD) {
    return {
      ok: false,
      reason: 'NOT_HOLD_AFTER_OPEN',
      before: slim(before),
      openedType: opened && (opened.uuid || typeof opened),
      current: slim(current),
    };
  }
  let activated = null;
  try {
    const tabId = await eda.dmt_EditorControl.openDocument(PAGE);
    activated = { openDocument: tabId == null ? null : typeof tabId };
  } catch (e) {
    activated = { openErr: String(e && e.message || e).slice(0, 160) };
  }
  try {
    await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HOLD);
    activated = Object.assign(activated || {}, { activateDocument: PAGE + '@' + HOLD });
  } catch (e) {
    activated = Object.assign(activated || {}, { activateErr: String(e && e.message || e).slice(0, 160) });
  }
  await new Promise((r) => setTimeout(r, 2500));
  const after = await eda.dmt_Project.getCurrentProjectInfo();
  return {
    ok: current.uuid === HOLD && after && after.uuid === HOLD,
    unsavedAssumed: unsaved,
    before: slim(before),
    openedType: opened && (opened.uuid || typeof opened),
    current: slim(current),
    after: slim(after),
    activated,
    title: document.title,
    hash: location.hash,
    isLive: after && after.uuid === LIVE,
  };
})()`;

const fired = await send('Runtime.evaluate', {
  expression: expr,
  returnByValue: true,
  awaitPromise: true,
  timeout: 180000,
});
if (fired.result?.exceptionDetails) {
  const desc = fired.result.exceptionDetails.exception?.description
    || fired.result.exceptionDetails.text;
  const payload = { ok: false, exception: String(desc).slice(0, 500) };
  writeFileSync(OUT, JSON.stringify(payload, null, 2));
  console.log(JSON.stringify(payload, null, 2));
  ws.close();
  process.exit(1);
}
const value = fired.result?.result?.value ?? fired.result;
writeFileSync(OUT, JSON.stringify(value, null, 2));
console.log(JSON.stringify(value, null, 2));
ws.close();
if (!value || value.ok !== true || value.isLive) process.exit(2);
