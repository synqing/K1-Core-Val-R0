#!/usr/bin/env node
// Target the canonical K1-Core-Val-R0 project when multiple EasyEDA windows exist.

const CDP_BASE = process.env.EASYEDA_CDP_BASE || 'http://127.0.0.1:9223';
const PROJECT = '64325d0e55e0435abd018defb0089a9b';
const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
const [action, value = ''] = process.argv.slice(2);
const targets = await (await fetch(`${CDP_BASE}/json/list`)).json();
const canonicalPage = targets.find(t => t.type === 'page' && String(t.url).includes(PROJECT));
const page = canonicalPage || targets.find(t => t.type === 'page' && String(t.url).includes('pro.easyeda.com/editor'));
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
  console.log(JSON.stringify({ok:true,menu,reconnect}));
} else if (action === 'top-elements') {
  const result = await evaluate(`(() => [...document.querySelectorAll('body *')]
    .filter(x => x.offsetParent !== null)
    .map(x => { const r=x.getBoundingClientRect(); return {tag:x.tagName,className:String(x.className||''),text:(x.textContent||'').trim().slice(0,80),x:r.left+r.width/2,y:r.top+r.height/2,w:r.width,h:r.height}; })
    .filter(x => x.y < 45 && x.w > 5 && x.h > 5 && x.w < 300))()`);
  console.log(JSON.stringify(result, null, 2));
} else if (action === 'bridge-runtime-keys') {
  const result = await evaluate(`(() => ({
    windowKeys:Object.keys(window).filter(k=>/ext|mcp|bridge/i.test(k)),
    spaces:Object.entries(window._EXTAPI_SCRIPT_SPACES_||{}).map(([k,v])=>({key:k,keys:Object.keys(v||{}).filter(x=>/eda|mcp|bridge|connect|activate/i.test(x))})),
    rootPresent:!!window._EXTAPI_ROOT_
  }))()`);
  console.log(JSON.stringify(result, null, 2));
} else if (action === 'auth-state') {
  const result = await evaluate(`(() => ({
    cookieNames:document.cookie.split(';').map(x=>x.split('=')[0].trim()).filter(Boolean),
    localStorageKeys:Object.keys(localStorage),
    sessionStorageKeys:Object.keys(sessionStorage),
    hasLoginText:[...document.querySelectorAll('body *')].some(x=>x.offsetParent!==null&&(x.textContent||'').trim()==='Login'),
    hasSpectrasynqText:[...document.querySelectorAll('body *')].some(x=>x.offsetParent!==null&&(x.textContent||'').trim()==='spectrasynq')
  }))()`);
  console.log(JSON.stringify(result, null, 2));
} else if (action === 'screenshot') {
  if (!value) throw new Error('screenshot action requires an output path');
  const shot = await send('Page.captureScreenshot', {format:'png',fromSurface:true,captureBeyondViewport:false});
  if (shot.error || !shot.result?.data) throw new Error(shot.error?.message || 'captureScreenshot returned no data');
  const {writeFile} = await import('node:fs/promises');
  await writeFile(value, Buffer.from(shot.result.data, 'base64'));
  console.log(JSON.stringify({ok:true,path:value,bytes:Buffer.byteLength(shot.result.data,'base64')}));
} else if (action === 'screenshot-box1') {
  if (!value) throw new Error('screenshot-box1 action requires an output path');
  const shot = await send('Page.captureScreenshot', {
    format:'png', fromSurface:true, captureBeyondViewport:false,
    clip:{x:360,y:70,width:340,height:320,scale:3}
  });
  if (shot.error || !shot.result?.data) throw new Error(shot.error?.message || 'captureScreenshot returned no data');
  const {writeFile} = await import('node:fs/promises');
  await writeFile(value, Buffer.from(shot.result.data, 'base64'));
  console.log(JSON.stringify({ok:true,path:value,bytes:Buffer.byteLength(shot.result.data,'base64')}));
} else if (action === 'screenshot-box1-wide') {
  if (!value) throw new Error('screenshot-box1-wide action requires an output path');
  const shot = await send('Page.captureScreenshot', {
    format:'png', fromSurface:true, captureBeyondViewport:false,
    clip:{x:330,y:55,width:520,height:340,scale:4}
  });
  if (shot.error || !shot.result?.data) throw new Error(shot.error?.message || 'captureScreenshot returned no data');
  const {writeFile} = await import('node:fs/promises');
  await writeFile(value, Buffer.from(shot.result.data, 'base64'));
  console.log(JSON.stringify({ok:true,path:value,bytes:Buffer.byteLength(shot.result.data,'base64')}));
} else if (action === 'screenshot-container') {
  const separator=value.indexOf(':');
  const container=Number(value.slice(0,separator));
  const output=value.slice(separator+1);
  if (!Number.isInteger(container) || container<1 || container>10 || !output)
    throw new Error('screenshot-container requires N:path');
  const column=(container-1)%5;
  const row=container<=5?0:1;
  const shot = await send('Page.captureScreenshot', {
    format:'png', fromSurface:true, captureBeyondViewport:false,
    clip:{x:350+column*210,y:70+row*270,width:230,height:300,scale:4}
  });
  if (shot.error || !shot.result?.data) throw new Error(shot.error?.message || 'captureScreenshot returned no data');
  const {writeFile} = await import('node:fs/promises');
  await writeFile(output, Buffer.from(shot.result.data, 'base64'));
  console.log(JSON.stringify({ok:true,container,path:output,bytes:Buffer.byteLength(shot.result.data,'base64')}));
} else if (action === 'screenshot-clip') {
  const separator=value.indexOf(':');
  const values=value.slice(0,separator).split(',').map(Number);
  const output=value.slice(separator+1);
  if (values.length!==5 || values.some(v=>!Number.isFinite(v)) || !output)
    throw new Error('screenshot-clip requires x,y,width,height,scale:path');
  const [x,y,width,height,scale]=values;
  const shot = await send('Page.captureScreenshot', {
    format:'png', fromSurface:true, captureBeyondViewport:false,
    clip:{x,y,width,height,scale}
  });
  if (shot.error || !shot.result?.data) throw new Error(shot.error?.message || 'captureScreenshot returned no data');
  const {writeFile} = await import('node:fs/promises');
  await writeFile(output, Buffer.from(shot.result.data, 'base64'));
  console.log(JSON.stringify({ok:true,clip:{x,y,width,height,scale},path:output,bytes:Buffer.byteLength(shot.result.data,'base64')}));
} else if (action === 'pan-canvas') {
  const values=value.split(',').map(Number);
  if (values.length!==4 || values.some(v=>!Number.isFinite(v)))
    throw new Error('pan-canvas requires startX,startY,endX,endY');
  const [startX,startY,endX,endY]=values;
  await send('Input.dispatchMouseEvent', {type:'mousePressed',x:startX,y:startY,button:'middle',buttons:4,clickCount:1});
  const steps=12;
  for (let index=1; index<=steps; index++) {
    const x=startX+(endX-startX)*index/steps;
    const y=startY+(endY-startY)*index/steps;
    await send('Input.dispatchMouseEvent', {type:'mouseMoved',x,y,button:'middle',buttons:4});
  }
  await send('Input.dispatchMouseEvent', {type:'mouseReleased',x:endX,y:endY,button:'middle',buttons:0,clickCount:1});
  console.log(JSON.stringify({ok:true,startX,startY,endX,endY}));
} else if (action === 'wheel-canvas') {
  const values=value.split(',').map(Number);
  if (values.length!==3 || values.some(v=>!Number.isFinite(v)))
    throw new Error('wheel-canvas requires x,y,deltaY');
  const [x,y,deltaY]=values;
  await send('Input.dispatchMouseEvent', {type:'mouseMoved',x,y});
  await send('Input.dispatchMouseEvent', {type:'mouseWheel',x,y,deltaX:0,deltaY});
  console.log(JSON.stringify({ok:true,x,y,deltaY}));
} else if (action === 'escape') {
  await send('Input.dispatchKeyEvent', {type:'keyDown',key:'Escape',code:'Escape'});
  await send('Input.dispatchKeyEvent', {type:'keyUp',key:'Escape',code:'Escape'});
  console.log(JSON.stringify({ok:true,key:'Escape'}));
} else if (action === 'boxes-exact-text') {
  const result = await evaluate(`(() => [...document.querySelectorAll('body *')]
    .filter(x => (x.textContent || '').trim() === ${JSON.stringify(value)})
    .map(x => { const r=x.getBoundingClientRect(); return {tag:x.tagName,className:x.className,visible:x.offsetParent!==null,x:r.left+r.width/2,y:r.top+r.height/2,w:r.width,h:r.height}; }))()`);
  console.log(JSON.stringify(result, null, 2));
} else if (action === 'html-exact-text') {
  const result = await evaluate(`(() => [...document.querySelectorAll('body *')]
    .filter(x => x.offsetParent !== null && (x.textContent || '').trim() === ${JSON.stringify(value)})
    .filter(x => { const r=x.getBoundingClientRect(); return r.width > 2 && r.height > 2; })
    .map(x => ({self:x.outerHTML.slice(0,1200),parent:x.parentElement?.outerHTML.slice(0,1800)})))()`);
  console.log(JSON.stringify(result, null, 2));
} else if (action === 'navigate-canonical') {
  const response = await send('Page.navigate', {url:`https://pro.easyeda.com/editor?cll=warn#id=${PROJECT},tab=*${PAGE}@${PROJECT}`});
  if (response.error) throw new Error(response.error.message);
  console.log(JSON.stringify({ok:true,projectUuid:PROJECT,frameId:response.result?.frameId}));
} else if (action === 'visible-text') {
  const result = await evaluate(`(() => [...document.querySelectorAll('body *')]
    .filter(e => e.offsetParent !== null && e.children.length === 0)
    .map(e => (e.textContent || '').trim()).filter(Boolean)
    .filter((v, i, a) => a.indexOf(v) === i))()`);
  console.log(JSON.stringify(result, null, 2));
} else if (action === 'click-exact-text') {
  const result = await evaluate(`(() => {
    const target = ${JSON.stringify(value)};
    const e = [...document.querySelectorAll('body *')]
      .filter(x => x.offsetParent !== null && (x.textContent || '').trim() === target)
      .filter(x => { const r=x.getBoundingClientRect(); return r.width > 2 && r.height > 2; })
      .sort((a,b) => a.getBoundingClientRect().width - b.getBoundingClientRect().width)[0];
    if (!e) return {ok:false,target};
    const r = e.getBoundingClientRect();
    return {ok:true,target,x:r.left+r.width/2,y:r.top+r.height/2};
  })()`);
  if (!result?.ok) throw new Error(`visible exact text not found: ${value}`);
  await send('Input.dispatchMouseEvent', {type:'mousePressed',x:result.x,y:result.y,button:'left',clickCount:1});
  await send('Input.dispatchMouseEvent', {type:'mouseReleased',x:result.x,y:result.y,button:'left',clickCount:1});
  console.log(JSON.stringify(result));
} else if (action === 'open-recent-project') {
  const result = await evaluate(`(() => {
    const e=[...document.querySelectorAll('[class*=prj_name]')]
      .find(x => x.offsetParent !== null && (x.textContent || '').trim() === ${JSON.stringify(value)});
    if (!e) return {ok:false}; const r=e.getBoundingClientRect();
    return {ok:true,x:r.left+r.width/2,y:r.top+r.height/2};
  })()`);
  if (!result?.ok) throw new Error(`recent project not found: ${value}`);
  await send('Input.dispatchMouseEvent', {type:'mousePressed',x:result.x,y:result.y,button:'left',clickCount:2});
  await send('Input.dispatchMouseEvent', {type:'mouseReleased',x:result.x,y:result.y,button:'left',clickCount:2});
  console.log(JSON.stringify(result));
} else if (action === 'expand-schematic') {
  const result = await evaluate(`(() => {
    const node=document.querySelector('[node-id="cffcdb562c1b48d1a5214cfc263b6c90"][node-type="6"]');
    const e=node?.querySelector('[class*=tree-hit]');
    if (!e) return {ok:false}; const r=e.getBoundingClientRect();
    e.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true,view:window}));
    return {ok:true,x:r.left+r.width/2,y:r.top+r.height/2};
  })()`);
  if (!result?.ok) throw new Error('canonical schematic tree expander not found');
  console.log(JSON.stringify(result));
} else if (action === 'open-schematic') {
  const result = await evaluate(`(() => {
    const e=document.querySelector('[node-id="cffcdb562c1b48d1a5214cfc263b6c90"][node-type="6"] [data-test="Schematic1"]');
    if (!e) return {ok:false}; const r=e.getBoundingClientRect();
    return {ok:true,x:r.left+r.width/2,y:r.top+r.height/2};
  })()`);
  if (!result?.ok) throw new Error('canonical schematic title not found');
  await send('Input.dispatchMouseEvent', {type:'mousePressed',x:result.x,y:result.y,button:'left',clickCount:2});
  await send('Input.dispatchMouseEvent', {type:'mouseReleased',x:result.x,y:result.y,button:'left',clickCount:2});
  console.log(JSON.stringify(result));
} else if (action === 'open-canonical-page-api') {
  const result = await evaluate(`(async () => {
    const eda=globalThis._EXTAPI_ROOT_;
    if (!eda?.dmt_Project?.openProject || !eda?.dmt_EditorControl?.openDocument)
      return {ok:false,reason:'required EasyEDA API mounts unavailable'};
    const projectOpened=await eda.dmt_Project.openProject(${JSON.stringify(PROJECT)});
    const tabId=await eda.dmt_EditorControl.openDocument(${JSON.stringify(PAGE)});
    const activated=typeof tabId==='string' && eda.dmt_EditorControl.activateDocument
      ? await eda.dmt_EditorControl.activateDocument(tabId) : undefined;
    return {ok:true,projectOpened,tabId,activated};
  })()`);
  if (!result?.ok) throw new Error(result?.reason || 'canonical page API open failed');
  console.log(JSON.stringify(result));
} else if (action === 'apply-source-and-save') {
  if (!value) throw new Error('apply-source-and-save requires a guarded payload path');
  const {readFile} = await import('node:fs/promises');
  const payload = JSON.parse(await readFile(value, 'utf8'));
  const result = await evaluate(`(async () => {
    const eda=globalThis._EXTAPI_ROOT_;
    const source=${JSON.stringify(payload.source)};
    const expected=${JSON.stringify(payload.expectedSourceHash)};
    const expectedDocument=${JSON.stringify(payload.expectedDocumentUuid)};
    const hash=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return s.length+':'+(h>>>0).toString(16).padStart(8,'0');};
    const documentInfo=await eda.dmt_SelectControl.getCurrentDocumentInfo();
    if (documentInfo?.uuid!==expectedDocument || documentInfo?.documentType!==1)
      return {ok:false,reason:'document identity mismatch',documentInfo};
    const before=(await eda.sys_FileManager.getDocumentSource())||'';
    const beforeHash=hash(before);
    if (beforeHash!==expected) return {ok:false,reason:'source hash mismatch',beforeHash,expected};
    const updated=await eda.sys_FileManager.setDocumentSource(source);
    const saved=await eda.sch_Document.save();
    const after=(await eda.sys_FileManager.getDocumentSource())||'';
    return {ok:updated!==false&&saved!==false,updated,saved,beforeHash,requestedHash:hash(source),afterHash:hash(after),characters:after.length};
  })()`);
  if (!result?.ok) throw new Error(JSON.stringify(result));
  console.log(JSON.stringify(result));
} else if (action === 'move-exact-schematic-text') {
  if (!value) throw new Error('move-exact-schematic-text requires a payload path');
  const {readFile,writeFile} = await import('node:fs/promises');
  const payload = JSON.parse(await readFile(value, 'utf8'));
  const result = await evaluate(`(async () => {
    const eda=globalThis._EXTAPI_ROOT_;
    const expectedDocument=${JSON.stringify(payload.expectedDocumentUuid)};
    const oldContent=${JSON.stringify(payload.oldContent)};
    const newContent=${JSON.stringify(payload.newContent)};
    const newX=${JSON.stringify(payload.x)};
    const newY=${JSON.stringify(payload.y)};
    const hash=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return s.length+':'+(h>>>0).toString(16).padStart(8,'0');};
    const documentInfo=await eda.dmt_SelectControl.getCurrentDocumentInfo();
    if (documentInfo?.uuid!==expectedDocument || documentInfo?.documentType!==1)
      return {ok:false,reason:'document identity mismatch',documentInfo};
    const before=(await eda.sys_FileManager.getDocumentSource())||'';
    const rows=before.split(/\\r?\\n/).filter(Boolean).map(line=>JSON.parse(line));
    const matches=rows.filter(row=>row[0]==='TEXT' && row.length>5 && row[5]===oldContent);
    if (matches.length!==1) return {ok:false,reason:'exact text match count',count:matches.length};
    matches[0][2]=newX; matches[0][3]=newY; matches[0][5]=newContent;
    const requested=rows.map(row=>JSON.stringify(row)).join('\\n');
    const updated=await eda.sys_FileManager.setDocumentSource(requested);
    const saved=await eda.sch_Document.save();
    const after=(await eda.sys_FileManager.getDocumentSource())||'';
    const afterRows=after.split(/\\r?\\n/).filter(Boolean).map(line=>JSON.parse(line));
    const moved=afterRows.filter(row=>row[0]==='TEXT' && row.length>5 && row[5]===newContent);
    const persisted=moved.length===1 && moved[0][2]===newX && moved[0][3]===newY;
    return {ok:updated!==false&&saved!==false&&persisted,updated,saved,persisted,
      beforeSource:before,beforeHash:hash(before),requestedHash:hash(requested),afterHash:hash(after),
      moved:moved.map(row=>({id:row[1],x:row[2],y:row[3],content:row[5]}))};
  })()`);
  if (!result?.ok) throw new Error(JSON.stringify({...result,beforeSource:undefined}));
  const beforeSource=result.beforeSource;
  const census=Object.fromEntries(['COMPONENT','WIRE','TEXT','RECT'].map(kind=>[
    kind.toLowerCase()+'s', beforeSource.split(`["${kind}"`).length-1
  ]));
  await writeFile(payload.snapshotPath, JSON.stringify({
    source:beforeSource, source_hash:result.beforeHash, census,
    project_uuid:PROJECT, document_uuid:PAGE
  }, null, 2)+'\n');
  delete result.beforeSource;
  console.log(JSON.stringify(result));
} else {
  throw new Error('usage: easyeda_cdp_project_ui.mjs reconnect-bridge | bridge-runtime-keys | auth-state | screenshot <path> | screenshot-box1 <path> | escape | top-elements | boxes-exact-text <text> | html-exact-text <text> | navigate-canonical | visible-text | click-exact-text <text>');
}
ws.close();
