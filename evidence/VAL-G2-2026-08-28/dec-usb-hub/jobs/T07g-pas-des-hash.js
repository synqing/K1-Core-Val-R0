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
  const ids = [
    ['C120-USB', '004d113915448a0a'],
    ['C121-USB', '2859c2b57ac86be4'],
    ['C122-USB', '3a63da66b1222580'],
    ['R81-USB', '22c6a17a7dbbd174'],
    ['R82-USB', 'dac528b1bfdc76ab'],
    ['R83-USB', '252b7a11c6b4da53'],
    ['R84-USB', '6b258885a490d64b'],
    ['R85-USB', '5cf017917b429da4'],
    ['R86-USB', 'd18377ecee6c9362'],
  ];
  const parts = [];
  for (const [want, id] of ids) {
    const c = await eda.sch_PrimitiveComponent.get(id);
    const st = c && (c.getState ? c.getState() : c);
    parts.push({
      id,
      want,
      designator: st && st.designator,
      supplierId: st && st.supplierId,
      x: st && st.x,
      y: st && st.y,
      addIntoPcb: st && st.addIntoPcb,
    });
  }
  await eda.sch_Document.save();
  const source = await eda.sys_FileManager.getDocumentSource();
  const comps = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    components: (comps || []).length,
    wires: (wires || []).length,
    parts,
  };
})()
