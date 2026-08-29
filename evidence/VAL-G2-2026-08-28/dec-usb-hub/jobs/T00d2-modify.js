(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const NEW = 'ea47c20de228fa3a';
  const OLD = 'e339';
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
  const neu = await eda.sch_PrimitiveComponent.get(NEW);
  const before = Object.assign({}, neu.getState ? neu.getState() : neu);
  if (String(before.x) !== '-485' || String(before.y) !== '3160') {
    return { stop: true, reason: 'MOVED', x: before.x, y: before.y };
  }
  await eda.sch_PrimitiveComponent.modify(NEW, {
    designator: 'J1-PWR1',
    name: 'GT-USB-7005A',
    manufacturerId: 'GT-USB-7005A',
    supplierId: 'C5250872',
    addIntoPcb: false,
  });
  await eda.sch_Document.save();
  const neu2 = await eda.sch_PrimitiveComponent.get(NEW);
  const old2 = await eda.sch_PrimitiveComponent.get(OLD);
  const ns = neu2.getState ? neu2.getState() : neu2;
  const os = old2.getState ? old2.getState() : old2;
  const source = await eda.sys_FileManager.getDocumentSource();
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  let pins = [];
  try {
    const pinObjs = await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(NEW);
    pins = (pinObjs || []).map((p) => {
      const st = p.getState ? p.getState() : p;
      return st.pinNumber || st.number;
    });
  } catch (e) { pins = []; }
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    components: (ids || []).length,
    wires: (wires || []).length,
    beforeDes: before.designator,
    afterDes: ns.designator,
    afterName: ns.name,
    afterMfr: ns.manufacturerId,
    afterSup: ns.supplierId,
    x: ns.x,
    y: ns.y,
    addIntoPcb: ns.addIntoPcb,
    oldDes: os.designator,
    pinCount: pins.length,
    pins,
  };
})()
