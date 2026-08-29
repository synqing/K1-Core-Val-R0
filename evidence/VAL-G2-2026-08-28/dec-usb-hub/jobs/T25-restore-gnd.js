(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const MEGA = 'cc9e090de2555cfb';
  const GND_SEGS = [[1520,400,1640,400],[1640,600,1640,400],[1640,600,1620,600],[1620,600,1620,1140],[1595,1140,1620,1140],[1595,1140,1595,800],[1470,1140,1595,1140],[1470,800,1470,1140],[1470,800,1440,800],[1440,1140,1470,1140],[1440,1100,1440,1140],[1360,1140,1440,1140],[1360,1140,1360,600],[1465,600,1360,600],[1240,1140,1360,1140],[1240,1000,1240,1140],[1160,1140,1240,1140],[1160,1140,1160,1000],[1140,1140,1160,1140],[1140,810,1140,1140],[1120,1140,1140,1140],[1120,1140,1120,1000],[810,1140,1120,1140],[810,1140,810,710],[750,710,810,710],[780,1140,810,1140],[760,1140,780,1140],[780,1140,780,1100],[780,980,780,1100],[1640,1140,1620,1140],[1640,1140,1640,630],[1500,630,1640,630],[1640,1140,1660,1140],[1660,1200,1660,1140],[1660,1140,1710,1140],[1710,1140,1710,1030],[1710,1030,1910,1030],[1910,480,1910,1030],[1910,480,170,480],[170,750,170,480],[170,750,230,750],[1710,1030,1710,1010],[1710,1000,1710,1010],[1820,1140,1710,1140],[1820,1140,1820,1200],[1870,1140,1820,1140],[1870,1140,1885,1140],[1885,1140,1885,550],[1810,550,1885,550],[1810,550,1810,600],[1710,600,1810,600],[1890,1140,1885,1140],[1870,1140,1870,1000],[1870,600,1870,1000],[1535,600,1620,600]];
  function sourceHash(source) {
    let hash = 2166136261;
    for (let i = 0; i < source.length; i += 1) {
      hash ^= source.charCodeAt(i);
    }
    return source.length + ':' + (hash >>> 0).toString(16).padStart(8, '0');
  }
  function parse(source) {
    const recs = [];
    for (const chunk of source.split('\n')) {
      const parts = chunk.split('||');
      if (parts.length < 2) continue;
      try {
        const head = JSON.parse(parts[0].replace(/^\|/, ''));
        const body = JSON.parse(parts[1].replace(/\|$/, ''));
        recs.push({ ...head, ...body });
      } catch (e) { /* skip */ }
    }
    return recs;
  }
  function tapParents(recs) {
    const out = { TAP_VBUS: [], TAP_REF: [], GND_mega: [] };
    for (const r of recs) {
      if (r && r.key === 'NET' && (r.value === 'TAP_VBUS' || r.value === 'TAP_REF')) {
        if (!out[r.value].includes(r.parentId)) out[r.value].push(r.parentId);
      }
    }
    return out;
  }
  function hasBar(line) {
    if (!Array.isArray(line)) return false;
    for (let i = 0; i + 3 < line.length; i += 2) {
      const x1 = line[i], y1 = line[i + 1], x2 = line[i + 2], y2 = line[i + 3];
      if (y1 === 1010 && y2 === 1010 && Math.min(x1, x2) <= 1460 && Math.max(x1, x2) >= 1580) return true;
    }
    return false;
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  let deleted = null;
  try {
    await eda.sch_PrimitiveWire.delete(MEGA);
    deleted = { id: MEGA, ok: true };
  } catch (e) {
    deleted = { id: MEGA, ok: false, err: String(e && e.message || e).slice(0, 160) };
  }
  const gndCreated = [];
  let gndFail = 0;
  for (const seg of GND_SEGS) {
    try {
      const w = await eda.sch_PrimitiveWire.create(seg, 'GND');
      const st = w && (w.getState ? w.getState() : w);
      gndCreated.push(st && (st.primitiveId || st.id));
    } catch (e) {
      gndFail += 1;
    }
  }
  let tapRef = null;
  try {
    const w = await eda.sch_PrimitiveWire.create(
      [1460, 1010, 1478, 1010, 1478, 970, 1580, 970, 1580, 1200, 1620, 1200],
      'TAP_REF',
    );
    const st = w && (w.getState ? w.getState() : w);
    tapRef = { ok: true, id: st && (st.primitiveId || st.id), net: st && st.net, line: st && st.line };
  } catch (e) {
    tapRef = { ok: false, err: String(e && e.message || e).slice(0, 160) };
  }
  await eda.sch_Document.save();
  const src = await eda.sys_FileManager.getDocumentSource();
  const recs = parse(src);
  const parents = tapParents(recs);
  const megaNets = recs.filter((r) => r.parentId === MEGA || r.id === MEGA).map((r) => r.key === 'NET' ? r.value : r.type);
  const wires = [];
  for (const id of [...new Set([...parents.TAP_VBUS, ...parents.TAP_REF])]) {
    const prim = await eda.sch_PrimitiveWire.get(id).catch(() => null);
    const st = prim && (prim.getState ? prim.getState() : prim);
    wires.push({ id, net: st && st.net, line: st && st.line, bar: hasBar(st && st.line), lineLen: st && st.line && st.line.length });
  }
  let vbus = null;
  try {
    const prim = await eda.sch_PrimitiveWire.get('54b8d6c7efc61c4c');
    const st = prim && (prim.getState ? prim.getState() : prim);
    vbus = { present: !!st, net: st && st.net };
  } catch (e) {
    vbus = { present: false };
  }
  const sharedTapGnd = [];
  const netByParent = {};
  for (const r of recs) {
    if (r && r.key === 'NET') {
      netByParent[r.parentId] = netByParent[r.parentId] || new Set();
      netByParent[r.parentId].add(r.value);
    }
  }
  for (const [id, names] of Object.entries(netByParent)) {
    if (names.has('TAP_REF') && (names.has('GND') || names.has('TAP_VBUS'))) {
      sharedTapGnd.push({ id, names: [...names] });
    }
    if (names.has('TAP_VBUS') && names.has('TAP_REF')) {
      sharedTapGnd.push({ id, names: [...names] });
    }
  }
  return {
    proj: info.uuid,
    saved: true,
    hash: sourceHash(src),
    deleted,
    gndCreated: [...new Set(gndCreated)].length,
    gndAttempts: GND_SEGS.length,
    gndFail,
    tapRef,
    parents,
    shared: parents.TAP_VBUS.filter((id) => parents.TAP_REF.includes(id)),
    sharedTapGnd,
    wires,
    vbus,
    megaGone: megaNets.length === 0,
  };
})()
