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
  function rows(pins) {
    return (pins || []).map((p) => {
      const st = p.getState ? p.getState() : p;
      return {
        n: String((p.getState_PinNumber && p.getState_PinNumber()) || (st && st.pinNumber) || ''),
        name: String((p.getState_PinName && p.getState_PinName()) || (st && st.pinName) || ''),
        nc: !!(p.getState_NoConnected && p.getState_NoConnected()) || !!(st && st.noConnected),
      };
    });
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  await eda.sch_Document.save();
  const j1 = rows(await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId('ea47c20de228fa3a'));
  const u20 = rows(await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId('92edd0bd8901c171'));
  const u6 = rows(await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId('e3673'));
  const j1nc = ['A2', 'A3', 'A8', 'A10', 'A11', 'B2', 'B3', 'B8', 'B10', 'B11'];
  const source = await eda.sys_FileManager.getDocumentSource();
  let comps = 0;
  let wires = 0;
  for (const chunk of source.split('\n')) {
    if (chunk.includes('"type":"COMPONENT"')) comps += 1;
    if (chunk.includes('"type":"WIRE"')) wires += 1;
  }
  const ssNets = ['USB_SS', 'SSTX', 'SSRX', 'TX1+', 'TX1-', 'RX2+', 'RX2-', 'TX2+', 'TX2-', 'RX1+', 'RX1-'];
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    j1: j1.filter((p) => j1nc.includes(p.n)),
    u20_6: u20.find((p) => p.n === '6'),
    u6: u6.filter((p) => ['N12', 'N7', 'P6', 'P7'].includes(p.n)),
    ssNetHits: Object.fromEntries(ssNets.map((n) => [n, source.includes('"value":"' + n + '"')])),
    comps,
    wires,
  };
})()
