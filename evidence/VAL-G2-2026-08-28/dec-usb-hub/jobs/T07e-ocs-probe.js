(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  function sourceHash(source) {
    let hash = 2166136261;
    for (let i = 0; i < source.length; i += 1) {
      hash ^= source.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return source.length + ':' + (hash >>> 0).toString(16).padStart(8, '0');
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  const wireIds = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  const hits = [];
  for (const id of wireIds || []) {
    let st;
    try {
      const prim = await eda.sch_PrimitiveWire.getPrimitiveById(id);
      st = prim && prim.getState ? prim.getState() : prim;
    } catch (e) {
      continue;
    }
    const pts = (st && (st.points || st.path || st.line)) || [];
    const xs = [];
    const ys = [];
    const flat = [];
    if (Array.isArray(pts)) {
      for (const p of pts) {
        if (Array.isArray(p)) {
          xs.push(p[0]); ys.push(p[1]); flat.push(p[0], p[1]);
        } else if (p && typeof p === 'object') {
          xs.push(p.x); ys.push(p.y); flat.push(p.x, p.y);
        }
      }
    }
    if (!xs.length && st) {
      if (st.x1 != null) {
        xs.push(st.x1, st.x2); ys.push(st.y1, st.y2); flat.push(st.x1, st.y1, st.x2, st.y2);
      }
    }
    const minx = Math.min.apply(null, xs);
    const maxx = Math.max.apply(null, xs);
    const miny = Math.min.apply(null, ys);
    const maxy = Math.max.apply(null, ys);
    const near = maxx >= 100 && minx <= 1450 && maxy >= 720 && miny <= 920;
    if (near) {
      hits.push({
        id,
        net: st && (st.net || st.netName),
        flat,
        keys: st ? Object.keys(st).slice(0, 20) : [],
      });
    }
  }
  const source = await eda.sys_FileManager.getDocumentSource();
  const names = {};
  for (const net of ['USB_OCS1_N', 'USB_OCS2_N', 'RT_USB_VBUS', 'S3_USB_VBUS_VALID', 'USB_EN1', 'USB_EN2']) {
    let n = 0; let idx = 0;
    while ((idx = source.indexOf(net, idx)) !== -1) { n += 1; idx += net.length; }
    names[net] = n;
  }
  return {
    proj: info.uuid,
    sourceHash: sourceHash(source),
    wireCount: (wireIds || []).length,
    nearCount: hits.length,
    near: hits.slice(0, 80),
    names,
  };
})()
