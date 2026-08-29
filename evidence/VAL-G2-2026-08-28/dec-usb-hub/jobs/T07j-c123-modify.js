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
  const jobs = [
    { id: 'e8e13777e6daf227', designator: 'C123-USB', name: '100nF' },
    { id: '175450abf83b4c89', designator: 'C124-USB', name: '100nF' },
    { id: 'ffd3d3994031db72', designator: 'C125-USB', name: '100nF' },
  ];
  const after = [];
  for (const job of jobs) {
    await eda.sch_PrimitiveComponent.modify(job.id, {
      designator: job.designator,
      name: job.name,
      addIntoPcb: false,
    });
    const c = await eda.sch_PrimitiveComponent.get(job.id);
    const st = c && (c.getState ? c.getState() : c);
    after.push({
      id: job.id,
      designator: st && st.designator,
      name: st && st.name,
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
    after,
  };
})()
