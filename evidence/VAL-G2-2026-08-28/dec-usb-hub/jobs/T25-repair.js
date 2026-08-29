(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const BAD = 'e34ae57efe3e3790';
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
    const out = { TAP_VBUS: [], TAP_REF: [] };
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
  async function addWire(line, net) {
    try {
      const w = await eda.sch_PrimitiveWire.create(line, net);
      const st = w && (w.getState ? w.getState() : w);
      return { ok: true, net, line, id: st && (st.primitiveId || st.id), mergedNet: st && st.net, mergedLine: st && st.line };
    } catch (e) {
      return { ok: false, net, line, err: String(e && e.message || e).slice(0, 160) };
    }
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  const beforeSrc = await eda.sys_FileManager.getDocumentSource();
  const beforeHash = sourceHash(beforeSrc);
  let deleted = null;
  try {
    await eda.sch_PrimitiveWire.delete(BAD);
    deleted = { id: BAD, ok: true };
  } catch (e) {
    deleted = { id: BAD, ok: false, err: String(e && e.message || e).slice(0, 160) };
  }
  const created = [];
  created.push(await addWire([1460, 990, 1330, 990, 1330, 1175, 1440, 1175, 1440, 1200], 'TAP_VBUS'));
  created.push(await addWire([1420, 1200, 1460, 1200], 'TAP_VBUS'));
  created.push(await addWire([1460, 1010, 1478, 1010, 1478, 970, 1580, 970, 1580, 1200, 1620, 1200], 'TAP_REF'));
  await eda.sch_Document.save();
  const afterSrc = await eda.sys_FileManager.getDocumentSource();
  const afterHash = sourceHash(afterSrc);
  const recs = parse(afterSrc);
  const parents = tapParents(recs);
  const shared = parents.TAP_VBUS.filter((id) => parents.TAP_REF.includes(id));
  const wireIds = [...new Set([...parents.TAP_VBUS, ...parents.TAP_REF])];
  const wires = [];
  for (const id of wireIds) {
    try {
      const prim = await eda.sch_PrimitiveWire.get(id);
      const st = prim && (prim.getState ? prim.getState() : prim);
      wires.push({ id, net: st && st.net, line: st && st.line, bar: hasBar(st && st.line) });
    } catch (e) {
      wires.push({ id, err: String(e && e.message || e).slice(0, 120) });
    }
  }
  const stillBad = recs.some((r) => r.id === BAD || r.parentId === BAD || r.lineGroup === BAD);
  return {
    proj: info.uuid,
    saved: true,
    beforeHash,
    afterHash,
    deleted,
    created,
    parents,
    shared,
    wires,
    stillBad,
    j6: await eda.sch_PrimitiveComponent.get('e98163').then((p) => {
      const st = p && (p.getState ? p.getState() : p);
      return { present: !!st, des: st && (st.designator || st.name) };
    }).catch(() => ({ present: false })),
  };
})()
