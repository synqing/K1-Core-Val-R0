(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
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
  await eda.sch_Document.save();
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const placed = [];
  for (const id of ids || []) {
    const g = await eda.sch_PrimitiveComponent.get(id);
    if (!g) continue;
    if (g.x >= 2050 && g.x <= 2400 && g.y >= 750 && g.y <= 1100) {
      placed.push({
        id, des: g.designator, name: g.name, x: g.x, y: g.y,
        supplierId: g.supplierId, addIntoPcb: g.addIntoPcb,
        footprint: g.footprint && g.footprint.name,
        component: g.component && g.component.name,
      });
    }
  }
  const source = await eda.sys_FileManager.getDocumentSource();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    components: (ids || []).length,
    wires: (wires || []).length,
    placed,
    usbCHits: (source.match(/USB.?C|USB4105|Type-C/gi) || []).length,
  };
})()
