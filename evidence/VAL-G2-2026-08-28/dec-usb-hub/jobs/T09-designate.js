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
    { id: 'b027c9ae9b996415', designator: 'R94-USB', name: '0Ω FIT' },
    { id: '24561118da702cc5', designator: 'R95-USB', name: '0Ω DNP' },
    { id: '9f86d15a53851abb', designator: 'J12-USB', name: 'HDR-1x4' },
  ];
  const out = [];
  for (const job of jobs) {
    const before = await eda.sch_PrimitiveComponent.get(job.id);
    await eda.sch_PrimitiveComponent.modify(job.id, {
      designator: job.designator,
      name: job.name,
      addIntoPcb: false,
    });
    const after = await eda.sch_PrimitiveComponent.get(job.id);
    out.push({
      id: job.id,
      before: { des: before.designator, name: before.name, x: before.x, y: before.y },
      after: { des: after.designator, name: after.name, x: after.x, y: after.y, addIntoPcb: after.addIntoPcb },
    });
  }
  await eda.sch_Document.save();
  const source = await eda.sys_FileManager.getDocumentSource();
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    components: (ids || []).length,
    wires: (wires || []).length,
    out,
  };
})()
