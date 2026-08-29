(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const BAD = 'e34ae57efe3e3790';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  let primState = null;
  let primErr = null;
  let primKeys = [];
  try {
    const prim = await eda.sch_PrimitiveWire.get(BAD);
    primState = prim && (prim.getState ? prim.getState() : prim);
    primKeys = primState && typeof primState === 'object' ? Object.keys(primState) : [];
    if (prim) {
      const extra = {};
      for (const name of ['getState_Points', 'getState_Line', 'getState_Path', 'getPoints', 'getLine']) {
        if (typeof prim[name] === 'function') {
          try { extra[name] = prim[name](); } catch (e) { extra[name] = String(e && e.message || e).slice(0, 80); }
        }
      }
      primState = { state: primState, extra };
    }
  } catch (e) {
    primErr = String(e && e.message || e).slice(0, 200);
  }
  const src = await eda.sys_FileManager.getDocumentSource();
  const hits = [];
  let idx = 0;
  while ((idx = src.indexOf(BAD, idx)) !== -1 && hits.length < 8) {
    hits.push(src.slice(Math.max(0, idx - 80), Math.min(src.length, idx + 400)));
    idx += BAD.length;
  }
  const bar = src.includes('1460') && src.includes('"x":1460') ? 'has-1460' : 'scan';
  const barHits = [];
  const re = /1460,\s*1010|1580,\s*1010|"x":1460.*"y":1010/;
  let m;
  const src2 = src;
  if (src2.includes('1460,1010') || src2.includes('1460, 1010')) barHits.push('plain-1460-1010');
  if (src2.includes('[1460,1010,1580,1010]') || src2.includes('[1460, 1010, 1580, 1010]')) barHits.push('array-bar');
  return {
    proj: info.uuid,
    primErr,
    primKeys,
    primState,
    sourceHits: hits,
    barHits,
    sourceLen: src.length,
  };
})()
