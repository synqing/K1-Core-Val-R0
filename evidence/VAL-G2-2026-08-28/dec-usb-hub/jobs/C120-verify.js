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
  async function pinsOf(id) {
    const pins = await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(id);
    return (pins || []).map((p) => {
      const st = p.getState ? p.getState() : p;
      return {
        n: (p.getState_PinNumber && p.getState_PinNumber()) || (st && st.pinNumber),
        name: (p.getState_PinName && p.getState_PinName()) || (st && st.pinName),
        x: (p.getState_X && p.getState_X()) || (st && st.x),
        y: (p.getState_Y && p.getState_Y()) || (st && st.y),
        net: (p.getState_Net && p.getState_Net()) || (st && st.net),
      };
    });
  }
  const c120c = await eda.sch_PrimitiveComponent.get('004d113915448a0a');
  const c2c = await eda.sch_PrimitiveComponent.get('e108');
  const c1c = await eda.sch_PrimitiveComponent.get('e72');
  const source = await eda.sys_FileManager.getDocumentSource();
  const comps = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    components: (comps || []).length,
    wires: (wires || []).length,
    c120: { des: c120c.designator, name: c120c.name, x: c120c.x, y: c120c.y, pins: await pinsOf('004d113915448a0a') },
    c2: { des: c2c.designator, name: c2c.name, x: c2c.x, y: c2c.y, pins: await pinsOf('e108') },
    c1: { des: c1c.designator, name: c1c.name, x: c1c.x, y: c1c.y, pins: await pinsOf('e72') },
  };
})()
