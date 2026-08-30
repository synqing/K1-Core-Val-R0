#!/usr/bin/env node
// One-shot Captain-authorised recovery: restore HOLD P1 from post-ilm-saved-source.
// Refuses canonical. Does not edit the payload.
import { readFileSync, writeFileSync } from 'node:fs';

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const HOLD = '55ed9ee948734a0e903f37744b51f3b8';
const LIVE = '64325d0e55e0435abd018defb0089a9b';
const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
const EXPECTED_BEFORE = process.env.EXPECTED_BEFORE_HASH || '2588333:60753d61';
const EXPECTED_BODY = '9a3187266066a617ac48c826389dbb7104b3423721e4d02d0f1f891d7786f9e3';
const SOURCE_PATH = new URL('../anchors/post-ilm-saved-source.source.txt', import.meta.url);
const OUT = new URL('./g22-hold-recover-post-ilm-result.json', import.meta.url);
const source = readFileSync(SOURCE_PATH, 'utf8');
if (source.length !== 3165690 || !source.includes('"U20-USB"') || !source.includes('"U1-PWR1"')) {
  throw new Error(`restore payload rejected: len=${source.length}`);
}

const { createHash } = await import('node:crypto');
const skipDochead = (text) => {
  const nl = text.indexOf('\n');
  if (nl > 0 && text.slice(0, nl).includes('"DOCHEAD"')) return text.slice(nl + 1);
  return text;
};
if (createHash('sha256').update(skipDochead(source)).digest('hex') !==
    'ccf3ec9546330a204b56773a71eba14ca534d6f35944a0ff81652ac965064423') {
  throw new Error('restore payload non-DOCHEAD digest mismatch');
}

const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const page = targets.find((t) => t.type === 'page' && String(t.url).includes(HOLD));
if (!page) throw new Error('no HOLD CDP page');
if (String(page.url).includes(LIVE)) throw new Error('LIVE');

const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) pending.get(m.id)(m);
};
await new Promise((r) => { ws.onopen = r; });
const send = (method, params) => new Promise((res) => {
  const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params }));
});

const fnv = (s) => {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
  return `${s.length}:${(h >>> 0).toString(16).padStart(8, '0')}`;
};

const opts = {
  source,
  project: HOLD,
  page: PAGE,
  live: LIVE,
  expectedBefore: EXPECTED_BEFORE,
  expectedBody: EXPECTED_BODY,
  requestedHash: fnv(source),
};
const fired = await send('Runtime.evaluate', {
  expression: `(${async (__opts) => {
    const eda = globalThis._EXTAPI_ROOT_
      || (Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda) || {}).eda;
    const hash = (s) => {
      let h = 2166136261;
      for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
      return `${s.length}:${(h >>> 0).toString(16).padStart(8, '0')}`;
    };
    const skip = (text) => {
      const nl = text.indexOf('\n');
      if (nl > 0 && text.slice(0, nl).includes('"DOCHEAD"')) return text.slice(nl + 1);
      return text;
    };
    const sha = async (text) => {
      const buf = new TextEncoder().encode(text);
      const d = await crypto.subtle.digest('SHA-256', buf);
      return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, '0')).join('');
    };
    const current = await eda.dmt_Project.getCurrentProjectInfo();
    if (!current || current.uuid !== __opts.project) {
      return { ok: false, reason: 'NOT_HOLD', uuid: current && current.uuid };
    }
    if (current.uuid === __opts.live) return { ok: false, reason: 'LIVE' };
    const doc = await eda.dmt_SelectControl.getCurrentDocumentInfo();
    if (!doc || doc.uuid !== __opts.page) {
      return { ok: false, reason: 'WRONG_PAGE', document: doc && doc.uuid };
    }
    const before = String(await eda.sys_FileManager.getDocumentSource() || '');
    const beforeHash = hash(before);
    const beforeBody = await sha(skip(before));
    if (beforeHash !== __opts.expectedBefore && beforeBody !== __opts.expectedBody) {
      return { ok: false, reason: 'BEFORE_HASH', beforeHash, beforeBody, expected: __opts.expectedBefore };
    }
    if (before.includes('"U20-USB"') && before.length > 3000000) {
      return { ok: false, reason: 'ALREADY_GOOD', beforeHash };
    }
    const updated = await eda.sys_FileManager.setDocumentSource(__opts.source);
    await new Promise((r) => setTimeout(r, 4000));
    const afterSet = String(await eda.sys_FileManager.getDocumentSource() || '');
    const afterSetHash = hash(afterSet);
    const landed = afterSet.includes('"U20-USB"') && afterSet.includes('"U25-USB"')
      && afterSet.includes('"Y3-USB"') && afterSet.length > 3000000;
    if (!landed) {
      return {
        ok: false, reason: 'SET_DID_NOT_LAND', updated, beforeHash, afterSetHash,
        afterLen: afterSet.length, u20: afterSet.includes('"U20-USB"'),
      };
    }
    let saved = null;
    try { saved = await eda.sch_Document.save(); }
    catch (e) { saved = { err: String((e && e.message) || e).slice(0, 180) }; }
    await new Promise((r) => setTimeout(r, 4000));
    const afterSave = String(await eda.sys_FileManager.getDocumentSource() || '');
    return {
      ok: afterSave.includes('"U20-USB"') && afterSave.length > 3000000,
      primitive: 'sys_FileManager.setDocumentSource',
      updated,
      saved,
      friendlyName: current.friendlyName,
      beforeHash,
      beforeBody,
      requestedHash: __opts.requestedHash,
      afterSetHash,
      afterSaveHash: hash(afterSave),
      afterLen: afterSave.length,
      u20: afterSave.includes('"U20-USB"'),
      u25: afterSave.includes('"U25-USB"'),
      y3: afterSave.includes('"Y3-USB"'),
      j12: afterSave.includes('"J12-USB"'),
    };
  }})(${JSON.stringify(opts)})`,
  returnByValue: true,
  awaitPromise: true,
  timeout: 180000,
});
if (fired.result?.exceptionDetails) {
  const payload = {
    ok: false,
    exception: String(fired.result.exceptionDetails.exception?.description
      || fired.result.exceptionDetails.text).slice(0, 800),
  };
  writeFileSync(OUT, JSON.stringify(payload, null, 2));
  console.log(JSON.stringify(payload, null, 2));
  ws.close();
  process.exit(1);
}
const value = fired.result?.result?.value ?? fired.result;
writeFileSync(OUT, JSON.stringify(value, null, 2));
console.log(JSON.stringify(value, null, 2));
ws.close();
if (!value || value.ok !== true) process.exit(2);
