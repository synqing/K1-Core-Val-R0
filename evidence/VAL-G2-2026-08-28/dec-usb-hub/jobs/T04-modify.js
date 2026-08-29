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
    { id: '92edd0bd8901c171', designator: 'U20-USB', name: 'USB2422T-I/MJ' },
    { id: '736247481f2dd650', designator: 'Y3-USB', name: 'X322524MSB4SI' },
    { id: '6c4b8e5918c0e1f0', designator: 'R77-USB', name: '12k' },
    { id: 'a60d36245cbf4e86', designator: 'R78-USB', name: '100k' },
    { id: 'd7ed808dd32d71fa', designator: 'R79-USB', name: '100k' },
    { id: 'f6a62bb1e7d23ff6', designator: 'R80-USB', name: '4.7k' },
    { id: '109c559e17398f80', designator: 'R87-USB', name: '10k' },
    { id: 'fc944770c8a600b3', designator: 'R88-USB', name: '10k' },
    { id: '859dc25a82d72494', designator: 'R89-USB', name: '10k' },
    { id: '0a971b6f27ac9f41', designator: 'R90-USB', name: '10k' },
    { id: 'd04486ae5c7116a8', designator: 'R91-USB', name: '10k' },
    { id: 'c483828709b8b49b', designator: 'C100-USB', name: '1uF' },
    { id: 'd51d670fb0acdc36', designator: 'C101-USB', name: '100nF' },
    { id: '6718c810f2448d6c', designator: 'C102-USB', name: '12pF' },
    { id: 'd7f20978650e2f1d', designator: 'C103-USB', name: '12pF' },
    { id: '930c9f07728120be', designator: 'C104-USB', name: '100nF' },
    { id: '3fddf470f1772050', designator: 'C105-USB', name: '1uF' },
    { id: 'd4fba08559bea7f9', designator: 'C106-USB', name: '100nF' },
    { id: 'c70e548c3d1f4881', designator: 'C107-USB', name: '100nF' },
  ];
  const before = [];
  const after = [];
  for (const job of jobs) {
    const c = await eda.sch_PrimitiveComponent.get(job.id);
    const st = Object.assign({}, c.getState ? c.getState() : c);
    before.push({ id: job.id, designator: st.designator, x: st.x, y: st.y });
    await eda.sch_PrimitiveComponent.modify(job.id, {
      designator: job.designator,
      name: job.name,
      addIntoPcb: false,
    });
  }
  await eda.sch_Document.save();
  for (const job of jobs) {
    const c = await eda.sch_PrimitiveComponent.get(job.id);
    const st = c.getState ? c.getState() : c;
    after.push({
      id: job.id,
      designator: st.designator,
      name: st.name,
      x: st.x,
      y: st.y,
      addIntoPcb: st.addIntoPcb,
    });
  }
  const source = await eda.sys_FileManager.getDocumentSource();
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    components: (ids || []).length,
    wires: (wires || []).length,
    before,
    after,
  };
})()
