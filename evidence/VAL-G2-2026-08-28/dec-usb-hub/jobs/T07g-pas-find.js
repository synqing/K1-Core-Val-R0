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
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const known = new Set([
    '004d113915448a0a', '2859c2b57ac86be4', '22c6a17a7dbbd174',
    'dac528b1bfdc76ab', '252b7a11c6b4da53', '6b258885a490d64b',
    '5cf017917b429da4', 'd18377ecee6c9362',
    '4c311982f7a3bb0d', '125f3f5842b2d308', '8d95d838df2d5f43',
    'cace78f52f4c7139', 'fadfedaff2230f79', 'fb7c84f0a582bd9c',
    'daf3578c8ea5a570', '22002ec9ef576301', '16675eb0d11a5521',
  ]);
  const near = [];
  const unknown = [];
  for (const id of ids || []) {
    if (String(id).length < 12) continue;
    const c = await eda.sch_PrimitiveComponent.get(id);
    const st = c && (c.getState ? c.getState() : c);
    if (!st) continue;
    const rec = {
      id,
      designator: st.designator,
      supplierId: st.supplierId,
      value: st.otherProperty && st.otherProperty.Value,
      x: st.x,
      y: st.y,
      addIntoPcb: st.addIntoPcb,
    };
    if (st.x >= 1280 && st.x <= 1900 && st.y >= 350 && st.y <= 1400) near.push(rec);
    if (!known.has(id) && String(id).length >= 16) unknown.push(rec);
  }
  const source = await eda.sys_FileManager.getDocumentSource();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  return {
    proj: info.uuid,
    sourceHash: sourceHash(source),
    components: (ids || []).length,
    wires: (wires || []).length,
    near,
    unknown,
  };
})()
