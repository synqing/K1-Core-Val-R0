(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const OLD = '157288a558df8730';
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
  function parentsOf(recs, name) {
    const ids = [];
    for (const r of recs) {
      if (r && r.key === 'NET' && r.value === name && !ids.includes(r.parentId)) ids.push(r.parentId);
    }
    return ids;
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
    await eda.sch_PrimitiveWire.delete(OLD);
    deleted = { id: OLD, ok: true };
  } catch (e) {
    deleted = { id: OLD, ok: false, err: String(e && e.message || e).slice(0, 160) };
  }
  let created = null;
  try {
    const w = await eda.sch_PrimitiveWire.create(
      [1460, 1010, 1478, 1010, 1478, 850, 1580, 850, 1580, 1200, 1620, 1200],
      'TAP_REF',
    );
    const st = w && (w.getState ? w.getState() : w);
    created = { ok: true, id: st && (st.primitiveId || st.id), net: st && st.net, line: st && st.line };
  } catch (e) {
    created = { ok: false, err: String(e && e.message || e).slice(0, 160) };
  }
  await eda.sch_Document.save();
  const src = await eda.sys_FileManager.getDocumentSource();
  const recs = parse(src);
  const tapV = parentsOf(recs, 'TAP_VBUS');
  const tapR = parentsOf(recs, 'TAP_REF');
  const sharedNames = [];
  const by = {};
  for (const r of recs) {
    if (r && r.key === 'NET') {
      by[r.parentId] = by[r.parentId] || new Set();
      by[r.parentId].add(r.value);
    }
  }
  for (const [id, names] of Object.entries(by)) {
    if (names.size > 1 && (names.has('TAP_REF') || names.has('TAP_VBUS'))) {
      sharedNames.push({ id, names: [...names] });
    }
  }
  const wires = [];
  for (const id of [...new Set([...tapV, ...tapR])]) {
    const prim = await eda.sch_PrimitiveWire.get(id).catch(() => null);
    const st = prim && (prim.getState ? prim.getState() : prim);
    wires.push({ id, net: st && st.net, line: st && st.line, bar: hasBar(st && st.line), n: st && st.line && st.line.length });
  }
  return {
    proj: info.uuid,
    deleted,
    created,
    tapV,
    tapR,
    shared: tapV.filter((id) => tapR.includes(id)),
    sharedNames,
    wires,
  };
})()
