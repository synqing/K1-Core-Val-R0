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
  const targets = [
    { id: 'e98285', must: 'R73' },
    { id: 'e98324', must: 'R74' },
    { id: 'e98207', must: 'R71' },
    { id: 'e98246', must: 'R72' },
  ];
  const before = [];
  for (const t of targets) {
    const prim = await eda.sch_PrimitiveComponent.get(t.id).catch(() => null);
    const st = prim && (prim.getState ? prim.getState() : prim);
    const name = st ? String(st.designator || st.name || '') : '';
    before.push({ id: t.id, name, present: !!st, x: st && st.x, y: st && st.y });
    if (st && !name.includes(t.must)) return { stop: true, reason: 'ID_MISMATCH', id: t.id, name };
    if (st) await eda.sch_PrimitiveComponent.delete(t.id);
  }
  await eda.sch_Document.save();
  const after = [];
  for (const t of targets) {
    const prim = await eda.sch_PrimitiveComponent.get(t.id).catch(() => null);
    after.push({ id: t.id, present: !!prim });
  }
  const tuneDp = await eda.sch_PrimitiveComponent.get('f5380a109ca65eb9').catch(() => null);
  const tuneDm = await eda.sch_PrimitiveComponent.get('e105d8e42924191c').catch(() => null);
  const source = await eda.sys_FileManager.getDocumentSource();
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
    tuneKept: { dp: !!tuneDp, dm: !!tuneDm },
    sourceHas: {
      R73: source.includes('R73-ESP'),
      R74: source.includes('R74-ESP'),
      R71: source.includes('R71-ESP'),
      R72: source.includes('R72-ESP'),
    },
    comps,
    wires,
  };
})()
