(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const LIB = '0819f05c4eef4c71ace90d822a990e87';
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
  const known = [
    { role: 'C120', id: '004d113915448a0a' },
    { role: 'C121', id: '2859c2b57ac86be4' },
    { role: 'C122', id: '183389c21e797e51' },
    { role: 'R81', id: '22c6a17a7dbbd174' },
    { role: 'R82', id: 'dac528b1bfdc76ab' },
    { role: 'R83', id: '252b7a11c6b4da53' },
    { role: 'R84', id: '6b258885a490d64b' },
    { role: 'R85', id: '5cf017917b429da4' },
    { role: 'R86', id: 'd18377ecee6c9362' },
  ];
  const before = [];
  for (const p of known) {
    const c = await eda.sch_PrimitiveComponent.get(p.id);
    const st = c && (c.getState ? c.getState() : c);
    before.push({
      role: p.role,
      id: p.id,
      supplierId: st && st.supplierId,
      value: st && st.otherProperty && st.otherProperty.Value,
      x: st && st.x,
      y: st && st.y,
      addIntoPcb: st && st.addIntoPcb,
    });
  }
  const c122 = before.find((p) => p.role === 'C122');
  let replaced = false;
  let newC122 = null;
  if (c122 && c122.supplierId === 'C15850') {
    await eda.sch_PrimitiveComponent.delete(c122.id);
    const prim = await eda.sch_PrimitiveComponent.create(
      { libraryUuid: LIB, uuid: 'b925bfa4a5024275b18ec946b0b267bc' },
      1580,
      800,
      undefined,
      0,
      false,
      true,
      false,
    );
    const st = prim && (prim.getState ? prim.getState() : prim);
    newC122 = {
      id: st && (st.primitiveId || st.id || (prim && prim.primitiveId)),
      supplierId: st && st.supplierId,
      value: st && st.otherProperty && st.otherProperty.Value,
      x: st && st.x,
      y: st && st.y,
      addIntoPcb: st && st.addIntoPcb,
    };
    replaced = true;
  }
  await eda.sch_Document.save();
  const afterIds = [
    '004d113915448a0a',
    '2859c2b57ac86be4',
    newC122 && newC122.id ? newC122.id : '183389c21e797e51',
    '22c6a17a7dbbd174',
    'dac528b1bfdc76ab',
    '252b7a11c6b4da53',
    '6b258885a490d64b',
    '5cf017917b429da4',
    'd18377ecee6c9362',
  ];
  const after = [];
  for (const id of afterIds) {
    const c = await eda.sch_PrimitiveComponent.get(id);
    const st = c && (c.getState ? c.getState() : c);
    after.push({
      id,
      designator: st && st.designator,
      supplierId: st && st.supplierId,
      value: st && st.otherProperty && st.otherProperty.Value,
      x: st && st.x,
      y: st && st.y,
      addIntoPcb: st && st.addIntoPcb,
    });
  }
  const source = await eda.sys_FileManager.getDocumentSource();
  const comps = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  return {
    proj: info.uuid,
    friendly: info.friendlyName,
    saved: true,
    replaced,
    newC122,
    sourceHash: sourceHash(source),
    components: (comps || []).length,
    wires: (wires || []).length,
    before,
    after,
  };
})()
