#!/usr/bin/env node
// Review-project CDP helper. Targets K1-Core-Val-R0-G2.1-BULK-CANDIDATE only.
// Never default to live 64325d0e55e0435abd018defb0089a9b.

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = process.env.EASYEDA_PROJECT || 'dcd7e3cab2a24b9aa6e531d2b62e1b6f';
const PAGE = process.env.EASYEDA_PAGE || '1435cb46f39e48c8a8aadbb84ca81603';
const [action, value = ''] = process.argv.slice(2);
const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const reviewPage = targets.find(t => t.type === 'page' && String(t.url).includes(PROJECT));
const editorPage = targets.find(t => t.type === 'page' && String(t.url).includes('pro.easyeda.com/editor'));
const page = reviewPage || editorPage;
if (!page) throw new Error('no EasyEDA editor page target found');
const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
ws.onmessage = event => {
  const msg = JSON.parse(event.data);
  if (msg.id && pending.has(msg.id)) {
    pending.get(msg.id)(msg);
    pending.delete(msg.id);
  }
};
await new Promise(resolve => { ws.onopen = resolve; });
const send = (method, params = {}) => new Promise(resolve => {
  const messageId = ++id;
  pending.set(messageId, resolve);
  ws.send(JSON.stringify({ id: messageId, method, params }));
});
const evaluate = async expression => {
  const reply = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (reply.error || reply.result?.exceptionDetails)
    throw new Error(reply.error?.message || reply.result.exceptionDetails.text);
  return reply.result?.result?.value;
};

if (action === 'reconnect-bridge') {
  await send('Input.dispatchKeyEvent', {type:'keyDown',key:'Escape',code:'Escape'});
  await send('Input.dispatchKeyEvent', {type:'keyUp',key:'Escape',code:'Escape'});
  await new Promise(resolve => setTimeout(resolve, 100));
  const clickText = async target => {
    const result = await evaluate(`(() => {
      const target = ${JSON.stringify(target)};
      const e = [...document.querySelectorAll('body *')]
        .find(x => x.offsetParent !== null && (x.textContent || '').trim() === target);
      if (!e) return {ok:false,target};
      const r = e.getBoundingClientRect();
      e.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true,view:window}));
      return {ok:true,target,x:r.left+r.width/2,y:r.top+r.height/2};
    })()`);
    if (!result?.ok) throw new Error(`visible exact text not found: ${target}`);
    return result;
  };
  const more = await evaluate(`(() => {
    const e=document.querySelector('[class*=tool-bottom-menu-more]');
    if (!e || e.offsetParent===null) return {ok:false}; const r=e.getBoundingClientRect();
    e.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true,view:window}));
    return {ok:true,x:r.left+r.width/2,y:r.top+r.height/2};
  })()`);
  if (!more?.ok) {
    const direct = await evaluate(`(() => {
      const text = [...document.querySelectorAll('[class*=eda-menu-btn-top-text]')]
        .find(x => x.offsetParent !== null && (x.textContent || '').trim() === 'EasyEDA MCP Bridge');
      const e = text?.closest('[class*=eda-menu-btn]') || text;
      if (!e) return {ok:false}; const r=e.getBoundingClientRect();
      e.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true,view:window}));
      return {ok:true,x:r.left+r.width/2,y:r.top+r.height/2};
    })()`);
    if (!direct?.ok) throw new Error('EasyEDA MCP Bridge top menu not visible');
  }
  await new Promise(resolve => setTimeout(resolve, 120));
  const menu = more?.ok ? await evaluate(`(() => {
    const candidates = [...document.querySelectorAll('body *')]
      .filter(x => x.offsetParent !== null && (x.textContent || '').trim() === 'EasyEDA MCP Bridge')
      .sort((a,b) => a.getBoundingClientRect().width - b.getBoundingClientRect().width);
    const e = candidates[0];
    if (!e) return {ok:false}; const r=e.getBoundingClientRect();
    e.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true,view:window}));
    return {ok:true,x:r.left+r.width/2,y:r.top+r.height/2};
  })()`) : {ok:true,direct:true};
  if (!menu?.ok) throw new Error('visible EasyEDA MCP Bridge overflow item not found');
  await new Promise(resolve => setTimeout(resolve, 180));
  const reconnect = await clickText('Reconnect');
  console.log(JSON.stringify({ok:true, menu, reconnect, attachedByReviewUuid: Boolean(reviewPage)}));
} else if (action === 'attach-info') {
  console.log(JSON.stringify({
    ok: true,
    attachedUrl: page.url,
    attachedByReviewUuid: Boolean(reviewPage),
    projectUuid: PROJECT,
    pageUuid: PAGE,
  }));
} else if (action === 'navigate-start') {
  const url = 'https://pro.easyeda.com/';
  const response = await send('Page.navigate', { url });
  if (response.error) throw new Error(response.error.message);
  console.log(JSON.stringify({ ok: true, url, frameId: response.result?.frameId }));
} else if (action === 'navigate-review') {
  const url = `https://pro.easyeda.com/editor?cll=warn#id=${PROJECT},tab=*${PAGE}@${PROJECT}`;
  const response = await send('Page.navigate', { url });
  if (response.error) throw new Error(response.error.message);
  console.log(JSON.stringify({ ok: true, projectUuid: PROJECT, pageUuid: PAGE, frameId: response.result?.frameId, url }));
} else if (action === 'open-review-page-api') {
  const result = await evaluate(`(async () => {
    const eda = globalThis._EXTAPI_ROOT_;
    if (!eda?.dmt_Project?.openProject || !eda?.dmt_EditorControl?.openDocument)
      return {ok:false, reason:'required EasyEDA API mounts unavailable'};
    const projectOpened = await eda.dmt_Project.openProject(${JSON.stringify(PROJECT)});
    const tabId = await eda.dmt_EditorControl.openDocument(${JSON.stringify(PAGE)});
    const activated = typeof tabId === 'string' && eda.dmt_EditorControl.activateDocument
      ? await eda.dmt_EditorControl.activateDocument(tabId) : undefined;
    const projectInfo = await eda.dmt_Project.getCurrentProjectInfo?.();
    const documentInfo = await eda.dmt_SelectControl?.getCurrentDocumentInfo?.();
    return {ok:true, projectOpened, tabId, activated, projectInfo, documentInfo};
  })()`);
  if (!result?.ok) throw new Error(result?.reason || 'review page API open failed');
  console.log(JSON.stringify(result));
} else if (action === 'open-review-pcb-api') {
  const pcbUuid = value || '59bef7e87cff4cd580561703b62d8c19';
  const result = await evaluate(`(async () => {
    const eda = globalThis._EXTAPI_ROOT_;
    if (!eda?.dmt_Project?.openProject || !eda?.dmt_EditorControl?.openDocument)
      return {ok:false, reason:'required EasyEDA API mounts unavailable'};
    const projectOpened = await eda.dmt_Project.openProject(${JSON.stringify(PROJECT)});
    const tabId = await eda.dmt_EditorControl.openDocument(${JSON.stringify(pcbUuid)});
    const activated = typeof tabId === 'string' && eda.dmt_EditorControl.activateDocument
      ? await eda.dmt_EditorControl.activateDocument(tabId) : undefined;
    const projectInfo = await eda.dmt_Project.getCurrentProjectInfo?.();
    const documentInfo = await eda.dmt_SelectControl?.getCurrentDocumentInfo?.();
    return {ok:true, projectOpened, tabId, activated, projectInfo, documentInfo};
  })()`);
  if (!result?.ok) throw new Error(result?.reason || 'review PCB API open failed');
  console.log(JSON.stringify(result));
} else if (action === 'close-review-project-api') {
  const result = await evaluate(`(async () => {
    const eda = globalThis._EXTAPI_ROOT_;
    const closer = eda?.dmt_Project?.closeProject || eda?.dmt_Project?.closeCurrentProject;
    if (!closer) {
      const keys = Object.keys(eda?.dmt_Project || {});
      return {ok:false, reason:'no closeProject mount', keys};
    }
    const closed = await closer.call(eda.dmt_Project, ${JSON.stringify(PROJECT)});
    return {ok:true, closed};
  })()`);
  console.log(JSON.stringify(result));
} else if (action === 'project-api-keys') {
  const result = await evaluate(`(() => ({ok:true, keys:Object.keys(globalThis._EXTAPI_ROOT_?.dmt_Project||{}), editorKeys:Object.keys(globalThis._EXTAPI_ROOT_?.dmt_EditorControl||{}).filter(k=>/close|open|activate|project/i.test(k))}))()`);
  console.log(JSON.stringify(result));
} else if (action === 'identity') {
  const result = await evaluate(`(async () => {
    const eda = globalThis._EXTAPI_ROOT_;
    const projectInfo = await eda?.dmt_Project?.getCurrentProjectInfo?.();
    const documentInfo = await eda?.dmt_SelectControl?.getCurrentDocumentInfo?.();
    return {ok:true, projectInfo, documentInfo, href: location.href};
  })()`);
  console.log(JSON.stringify(result));
} else if (action === 'api-mounts') {
  const result = await evaluate(`(() => {
    const eda = globalThis._EXTAPI_ROOT_ || {};
    const pick = name => ({present:!!eda[name], keys:Object.keys(eda[name]||{}).sort()});
    return {
      ok:true,
      rootKeys:Object.keys(eda).sort(),
      sch_Drc:pick('sch_Drc'),
      sch_Document:pick('sch_Document'),
      sch_ManufactureData:pick('sch_ManufactureData'),
      sys_FileManager:pick('sys_FileManager'),
      sch_PrimitiveComponent:pick('sch_PrimitiveComponent'),
    };
  })()`);
  console.log(JSON.stringify(result, null, 2));
} else if (action === 'dump-source') {
  if (!value) throw new Error('dump-source requires an output path');
  const result = await evaluate(`(async () => {
    const eda = globalThis._EXTAPI_ROOT_;
    const documentInfo = await eda.dmt_SelectControl.getCurrentDocumentInfo();
    const projectInfo = await eda.dmt_Project.getCurrentProjectInfo();
    if (documentInfo?.uuid !== ${JSON.stringify(PAGE)} || documentInfo?.documentType !== 1)
      return {ok:false, reason:'document identity mismatch', documentInfo};
    if (projectInfo?.uuid !== ${JSON.stringify(PROJECT)})
      return {ok:false, reason:'project identity mismatch', projectInfo};
    const source = await eda.sys_FileManager.getDocumentSource();
    const hash = s => { let h=2166136261; for (let i=0;i<s.length;i++){ h^=s.charCodeAt(i); h=Math.imul(h,16777619);} return s.length+':'+(h>>>0).toString(16).padStart(8,'0'); };
    return {ok:true, documentInfo, projectUuid:projectInfo.uuid, characters:source.length, sourceHash:hash(source||''), source};
  })()`);
  if (!result?.ok) throw new Error(JSON.stringify(result));
  const { writeFile } = await import('node:fs/promises');
  const source = result.source;
  delete result.source;
  await writeFile(value, JSON.stringify({
    documentType: result.documentInfo.documentType,
    documentUuid: result.documentInfo.uuid,
    parentProjectUuid: result.documentInfo.parentProjectUuid,
    projectUuid: result.projectUuid,
    characters: result.characters,
    sourceHash: result.sourceHash,
    source,
  }, null, 2) + '\n');
  console.log(JSON.stringify({ ok: true, path: value, ...result }));
} else if (action === 'dump-netlist') {
  if (!value) throw new Error('dump-netlist requires an output path');
  const result = await evaluate(`(async () => {
    const eda = globalThis._EXTAPI_ROOT_;
    const documentInfo = await eda.dmt_SelectControl.getCurrentDocumentInfo();
    const projectInfo = await eda.dmt_Project.getCurrentProjectInfo();
    if (documentInfo?.uuid !== ${JSON.stringify(PAGE)} || projectInfo?.uuid !== ${JSON.stringify(PROJECT)})
      return {ok:false, reason:'identity mismatch', documentInfo, projectInfo};
    const api = eda.sch_ManufactureData;
    if (!api?.getNetlistFile) return {ok:false, reason:'getNetlistFile unavailable', keys:Object.keys(api||{})};
    const file = await api.getNetlistFile('review-netlist', 'EasyEDA');
    const text = file && typeof file.text === 'function' ? await file.text() : String(file);
    return {ok:true, bytes:text.length, name:file?.name, type:file?.type, text};
  })()`);
  if (!result?.ok) throw new Error(JSON.stringify(result));
  const { writeFile } = await import('node:fs/promises');
  await writeFile(value, result.text);
  console.log(JSON.stringify({ ok: true, path: value, bytes: result.bytes, name: result.name, type: result.type }));
} else if (action === 'dump-bom') {
  if (!value) throw new Error('dump-bom requires an output path');
  const result = await evaluate(`(async () => {
    const eda = globalThis._EXTAPI_ROOT_;
    const documentInfo = await eda.dmt_SelectControl.getCurrentDocumentInfo();
    const projectInfo = await eda.dmt_Project.getCurrentProjectInfo();
    if (documentInfo?.uuid !== ${JSON.stringify(PAGE)} || projectInfo?.uuid !== ${JSON.stringify(PROJECT)})
      return {ok:false, reason:'identity mismatch', documentInfo, projectInfo};
    const api = eda.sch_ManufactureData;
    const method = api?.getBomFile || api?.getBOMFile || api?.exportBom;
    if (!method) return {ok:false, reason:'BOM export unavailable', keys:Object.keys(api||{})};
    const file = await method.call(api, 'review-bom');
    const text = file && typeof file.text === 'function' ? await file.text() : String(file);
    return {ok:true, bytes:text.length, name:file?.name, type:file?.type, text};
  })()`);
  if (!result?.ok) throw new Error(JSON.stringify(result));
  const { writeFile } = await import('node:fs/promises');
  await writeFile(value, result.text);
  console.log(JSON.stringify({ ok: true, path: value, bytes: result.bytes, name: result.name }));
} else if (action === 'run-erc') {
  if (!value) throw new Error('run-erc requires an output json path');
  const result = await evaluate(`(async () => {
    const eda = globalThis._EXTAPI_ROOT_;
    const documentInfo = await eda.dmt_SelectControl.getCurrentDocumentInfo();
    const projectInfo = await eda.dmt_Project.getCurrentProjectInfo();
    if (documentInfo?.uuid !== ${JSON.stringify(PAGE)} || projectInfo?.uuid !== ${JSON.stringify(PROJECT)})
      return {ok:false, reason:'identity mismatch', documentInfo, projectInfo};
    const drc = eda.sch_Drc;
    if (!drc?.check) return {ok:false, reason:'sch_Drc.check unavailable', keys:Object.keys(drc||{})};
    let cleared = null;
    if (typeof drc.clear === 'function') cleared = await drc.clear();
    else if (typeof drc.clearErrors === 'function') cleared = await drc.clearErrors();
    const checkResult = await drc.check(true, false, true);
    const errors = Array.isArray(checkResult) ? checkResult : null;
    return {ok:true, cleared, passed: errors ? errors.length===0 : Boolean(checkResult), errorCount: errors ? errors.length : null, errors, rawType: typeof checkResult};
  })()`);
  if (!result?.ok) throw new Error(JSON.stringify(result));
  const { writeFile } = await import('node:fs/promises');
  await writeFile(value, JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify({ ok: true, path: value, passed: result.passed, errorCount: result.errorCount, cleared: result.cleared }));
} else if (action === 'fit-all') {
  const result = await evaluate(`(() => {
    const e = [...document.querySelectorAll('body *')].find(x =>
      x.offsetParent !== null && ((x.getAttribute('title') || '').trim() === 'Fit All in Window'
        || (x.textContent || '').trim() === 'Fit All in Window'));
    if (!e) return {ok:false, reason:'Fit All in Window control not found'};
    const r = e.getBoundingClientRect();
    e.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, view:window}));
    return {ok:true, x:r.left+r.width/2, y:r.top+r.height/2, title:e.getAttribute('title')||e.textContent};
  })()`);
  if (!result?.ok) throw new Error(result?.reason || 'fit-all failed');
  console.log(JSON.stringify(result));
} else if (action === 'screenshot') {
  if (!value) throw new Error('screenshot action requires an output path');
  const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
  if (shot.error || !shot.result?.data) throw new Error(shot.error?.message || 'captureScreenshot returned no data');
  const { writeFile } = await import('node:fs/promises');
  await writeFile(value, Buffer.from(shot.result.data, 'base64'));
  console.log(JSON.stringify({ ok: true, path: value, bytes: Buffer.byteLength(shot.result.data, 'base64'), attachedByReviewUuid: Boolean(reviewPage) }));
} else if (action === 'screenshot-clip') {
  const separator = value.indexOf(':');
  const values = value.slice(0, separator).split(',').map(Number);
  const output = value.slice(separator + 1);
  if (values.length !== 5 || values.some(v => !Number.isFinite(v)) || !output)
    throw new Error('screenshot-clip requires x,y,width,height,scale:path');
  const [x, y, width, height, scale] = values;
  const shot = await send('Page.captureScreenshot', {
    format: 'png', fromSurface: true, captureBeyondViewport: false,
    clip: { x, y, width, height, scale },
  });
  if (shot.error || !shot.result?.data) throw new Error(shot.error?.message || 'captureScreenshot returned no data');
  const { writeFile } = await import('node:fs/promises');
  await writeFile(output, Buffer.from(shot.result.data, 'base64'));
  console.log(JSON.stringify({ ok: true, clip: { x, y, width, height, scale }, path: output }));
} else if (action === 'visible-text') {
  const result = await evaluate(`(() => [...document.querySelectorAll('body *')]
    .filter(e => e.offsetParent !== null && e.children.length === 0)
    .map(e => (e.textContent || '').trim()).filter(Boolean)
    .filter((v, i, a) => a.indexOf(v) === i))()`);
  console.log(JSON.stringify(result, null, 2));
} else {
  throw new Error('usage: easyeda_cdp_review.mjs attach-info | navigate-review | open-review-page-api | open-review-pcb-api | close-review-project-api | identity | screenshot <path> | screenshot-clip x,y,w,h,s:path | visible-text');
}
ws.close();
