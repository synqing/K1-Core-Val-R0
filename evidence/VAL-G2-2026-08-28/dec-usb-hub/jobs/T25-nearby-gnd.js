(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  const ids = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  const hits = [];
  for (const id of ids || []) {
    try {
      const prim = await eda.sch_PrimitiveWire.get(id);
      const st = prim && (prim.getState ? prim.getState() : prim);
      const line = (st && st.line) || [];
      const net = st && st.net;
      let relevant = false;
      for (let i = 0; i + 3 < line.length; i += 2) {
        const x1 = line[i], y1 = line[i + 1], x2 = line[i + 2], y2 = line[i + 3];
        const minx = Math.min(x1, x2), maxx = Math.max(x1, x2);
        const miny = Math.min(y1, y2), maxy = Math.max(y1, y2);
        if (maxx >= 1320 && minx <= 1680 && maxy >= 920 && miny <= 1240) relevant = true;
      }
      if (relevant) {
        hits.push({ id, net, line });
      }
    } catch (e) { /* skip */ }
  }
  return { proj: info.uuid, nearbyWires: hits.length, hits };
})()
