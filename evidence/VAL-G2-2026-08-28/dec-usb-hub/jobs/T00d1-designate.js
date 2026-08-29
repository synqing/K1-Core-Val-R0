(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const OLD = 'e339';
  const NEW = 'ea47c20de228fa3a';
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
  const oldC = await eda.sch_PrimitiveComponent.get(OLD);
  const newC = await eda.sch_PrimitiveComponent.get(NEW);
  const oldBefore = oldC.getState ? oldC.getState() : oldC;
  const newBefore = newC.getState ? newC.getState() : newC;
  if (String(oldBefore.designator) !== 'J1-PWR1') {
    return { stop: true, reason: 'OLD_NOT_J1_PWR1', have: oldBefore.designator };
  }
  oldC.setState_Designator('J1-USB4105-RETIRED');
  await eda.sch_Document.save();
  const oldAfter = oldC.getState ? oldC.getState() : await eda.sch_PrimitiveComponent.get(OLD).then((c) => c.getState ? c.getState() : c);
  const newAfter = (await eda.sch_PrimitiveComponent.get(NEW));
  const newSt = newAfter.getState ? newAfter.getState() : newAfter;
  const source = await eda.sys_FileManager.getDocumentSource();
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    components: (ids || []).length,
    wires: (wires || []).length,
    old: { id: OLD, before: oldBefore.designator, after: oldAfter.designator, name: oldAfter.name, x: oldAfter.x, y: oldAfter.y },
    neu: { id: NEW, designator: newSt.designator, name: newSt.name, x: newSt.x, y: newSt.y },
  };
})()
