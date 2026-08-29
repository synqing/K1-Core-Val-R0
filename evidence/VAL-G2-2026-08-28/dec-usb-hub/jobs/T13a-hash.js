(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  function sourceHash(source) {
    let hash = 2166136261;
    for (let i = 0; i < source.length; i += 1) {
      hash ^= source.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return source.length + ':' + (hash >>> 0).toString(16).padStart(8, '0');
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  await eda.sch_Document.save();
  const a = await eda.sch_PrimitiveComponent.get('f5380a109ca65eb9');
  const b = await eda.sch_PrimitiveComponent.get('e105d8e42924191c');
  const r73 = await eda.sch_PrimitiveComponent.get('e98285');
  const source = await eda.sys_FileManager.getDocumentSource();
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    components: ((await eda.sch_PrimitiveComponent.getAllPrimitiveId()) || []).length,
    wires: ((await eda.sch_PrimitiveWire.getAllPrimitiveId()) || []).length,
    a: { des: a.designator, name: a.name, x: a.x, y: a.y, pcb: a.addIntoPcb },
    b: { des: b.designator, name: b.name, x: b.x, y: b.y, pcb: b.addIntoPcb },
    r73: { des: r73.designator, x: r73.x, y: r73.y },
  };
})()
