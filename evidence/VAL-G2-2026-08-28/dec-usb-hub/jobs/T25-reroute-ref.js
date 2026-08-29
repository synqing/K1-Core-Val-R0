(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
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
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  const OLD_REF = '660538283721f8ed';
  let deleted = null;
  try {
    await eda.sch_PrimitiveWire.delete(OLD_REF);
    deleted = { id: OLD_REF, ok: true };
  } catch (e) {
    deleted = { id: OLD_REF, ok: false, err: String(e && e.message || e).slice(0, 160) };
  }
  let created = null;
  try {
    const w = await eda.sch_PrimitiveWire.create(
      [1460, 1010, 1470, 1010, 1470, 1260, 1580, 1260, 1580, 1200, 1620, 1200],
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
  const parents = tapParents(recs);
  const wires = [];
  for (const id of [...new Set([...parents.TAP_VBUS, ...parents.TAP_REF])]) {
    const prim = await eda.sch_PrimitiveWire.get(id).catch(() => null);
    const st = prim && (prim.getState ? prim.getState() : prim);
    wires.push({ id, net: st && st.net, line: st && st.line, bar: hasBar(st && st.line) });
  }
  let vbus = null;
  try {
    const prim = await eda.sch_PrimitiveWire.get('54b8d6c7efc61c4c');
    const st = prim && (prim.getState ? prim.getState() : prim);
    vbus = { present: !!st, net: st && st.net };
  } catch (e) {
    vbus = { present: false, err: String(e && e.message || e).slice(0, 80) };
  }
  return {
    proj: info.uuid,
    saved: true,
    hash: sourceHash(src),
    deleted,
    created,
    parents,
    shared: parents.TAP_VBUS.filter((id) => parents.TAP_REF.includes(id)),
    wires,
    vbusUntouched: vbus,
  };
})()
