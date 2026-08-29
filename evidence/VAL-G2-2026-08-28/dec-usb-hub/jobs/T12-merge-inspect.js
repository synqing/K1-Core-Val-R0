(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  function parse(source) {
    const recs = [];
    for (const chunk of source.split('\n')) {
      const parts = chunk.split('||');
      if (parts.length < 2) continue;
      try {
        const head = JSON.parse(parts[0].replace(/^\|/, ''));
        const body = JSON.parse(parts[1].replace(/\|$/, ''));
        recs.push({ ...head, ...body });
      } catch (e) { /* skip */ }
    }
    return recs;
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const source = await eda.sys_FileManager.getDocumentSource();
  const recs = parse(source);
  const nets = recs.filter((r) => r.key === 'NET');
  const pick = (n) => nets.filter((r) => r.value === n).map((r) => ({ parentId: r.parentId, x: r.x, y: r.y }));
  const wireRecs = recs.filter((r) => r.parentId === 'b9520eddf98cb22f' || r.id === 'b9520eddf98cb22f');
  const capWire = recs.filter((r) => r.parentId === 'd712353198394ad0' || r.id === 'd712353198394ad0');
  const byParent = {};
  for (const n of nets) {
    if (Math.abs(Math.abs(Number(n.y)) - 4040) <= 5 && Number(n.x) >= 2160 && Number(n.x) <= 2300) {
      (byParent[n.parentId] ||= []).push({ net: n.value, x: n.x, y: n.y });
    }
  }
  let wireState = null;
  try {
    const w = await eda.sch_PrimitiveWire.get('b9520eddf98cb22f');
    wireState = w && (w.getState ? w.getState() : w);
  } catch (e) {
    wireState = { err: String(e) };
  }
  return {
    proj: info.uuid,
    FLEXSPI_D1: pick('FLEXSPI_D1'),
    FLEXSPI_D0: pick('FLEXSPI_D0'),
    USB_OTG1_ID: pick('USB_OTG1_ID'),
    USB_OTG1_VBUS: pick('USB_OTG1_VBUS'),
    ballRow4040: byParent,
    mergedWireRecs: wireRecs.slice(0, 40),
    capWireRecs: capWire.slice(0, 20),
    wireState: wireState && {
      net: wireState.net,
      line: wireState.line,
      id: wireState.id || wireState.primitiveId,
    },
  };
})()
