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
  const known = {
    u20: '92edd0bd8901c171',
    y3: '736247481f2dd650',
    r77: '6c4b8e5918c0e1f0',
    c104: '930c9f07728120be',
    c105: '3fddf470f1772050',
    c106: 'd4fba08559bea7f9',
  };
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const island = [];
  const autos = [];
  const usbRefs = [];
  for (const id of ids || []) {
    try {
      const c = await eda.sch_PrimitiveComponent.get(id);
      const st = c && (c.getState ? c.getState() : c);
      const des = String((st && st.designator) || '');
      const name = String((st && (st.name || st.deviceName)) || '');
      const x = st && st.x;
      const y = st && st.y;
      const row = { id, des, name, x, y };
      if ((x >= 150 && x <= 900 && y >= 650 && y <= 1200) || des.includes('-USB') || des === 'U?' || des === 'R?' || des === 'C?' || des === 'X?') {
        island.push(row);
      }
      if (/^[URCX]\?$/.test(des)) autos.push(row);
      if (des.includes('USB') || /U2[0-5]/.test(des) || des === 'D3') usbRefs.push(row);
    } catch (e) { /* skip */ }
  }
  const source = await eda.sys_FileManager.getDocumentSource();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  return {
    proj: info.uuid,
    sourceHash: sourceHash(source),
    components: (ids || []).length,
    wires: (wires || []).length,
    islandCount: island.length,
    island,
    autos,
    usbRefs,
    knownStill: Object.fromEntries(await Promise.all(Object.entries(known).map(async ([k, id]) => [k, (ids || []).includes(id)]))),
  };
})()
