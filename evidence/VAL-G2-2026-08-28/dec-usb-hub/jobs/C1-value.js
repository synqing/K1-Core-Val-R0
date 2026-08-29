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
  const before = await eda.sch_PrimitiveComponent.get('e72');
  const bs = before.getState ? before.getState() : before;
  await eda.sch_PrimitiveComponent.modify('e72', {
    designator: 'C1-PWR1',
    name: '1uF',
    addIntoPcb: false,
  });
  await eda.sch_Document.save();
  const after = await eda.sch_PrimitiveComponent.get('e72');
  const as = after.getState ? after.getState() : after;
  const source = await eda.sys_FileManager.getDocumentSource();
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    before: { designator: bs.designator, name: bs.name, x: bs.x, y: bs.y, supplierId: bs.supplierId },
    after: { designator: as.designator, name: as.name, x: as.x, y: as.y, supplierId: as.supplierId },
    components: ((await eda.sch_PrimitiveComponent.getAllPrimitiveId()) || []).length,
    wires: ((await eda.sch_PrimitiveWire.getAllPrimitiveId()) || []).length,
    still22: /C1-PWR1[\s\S]{0,80}22uF/.test(source),
    has1u: source.includes('1uF'),
  };
})()
