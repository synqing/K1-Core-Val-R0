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
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  const targets = [
    { id: 'e8421', must: 'R21' },
    { id: 'e8460', must: 'R22' },
  ];
  const before = [];
  for (const t of targets) {
    const prim = await eda.sch_PrimitiveComponent.get(t.id).catch(() => null);
    const st = prim && (prim.getState ? prim.getState() : prim);
    const name = st ? String(st.designator || st.name || '') : '';
    before.push({ id: t.id, name, present: !!st });
    if (st && !name.includes(t.must)) return { stop: true, reason: 'ID_MISMATCH', id: t.id, name };
    if (st) await eda.sch_PrimitiveComponent.delete(t.id);
  }
  const leftoverWires = ['e9016', 'e9022'];
  const wireDeletes = [];
  for (const id of leftoverWires) {
    try {
      await eda.sch_PrimitiveWire.delete(id);
      wireDeletes.push({ id, ok: true });
    } catch (e) {
      wireDeletes.push({ id, ok: false, err: String(e && e.message || e) });
    }
  }
  await eda.sch_Document.save();
  const after = [];
  for (const t of targets) {
    const prim = await eda.sch_PrimitiveComponent.get(t.id).catch(() => null);
    after.push({ id: t.id, present: !!prim });
  }
  const source = await eda.sys_FileManager.getDocumentSource();
  const nets = parse(source).filter((r) => r.key === 'NET');
  const pick = (n) => nets.filter((r) => r.value === n).map((r) => ({ parentId: r.parentId, x: r.x, y: r.y }));
  let comps = 0;
  let wires = 0;
  for (const chunk of source.split('\n')) {
    if (chunk.includes('"type":"COMPONENT"')) comps += 1;
    if (chunk.includes('"type":"WIRE"')) wires += 1;
  }
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    before,
    after,
    wireDeletes,
    sourceHas: { R21: source.includes('R21-ESP'), R22: source.includes('R22-ESP') },
    USB_CC1: pick('USB_CC1'),
    USB_CC2: pick('USB_CC2'),
    comps,
    wires,
  };
})()
