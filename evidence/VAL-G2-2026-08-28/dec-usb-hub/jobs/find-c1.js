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
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const hits = [];
  for (const id of ids || []) {
    let prim;
    try { prim = await eda.sch_PrimitiveComponent.getPrimitiveById(id); } catch (e) { continue; }
    const st = prim && prim.getState ? prim.getState() : prim;
    const des = (st && (st.designator || st.name)) || '';
    if (/C1-PWR1|C100-USB|C120-USB|C2-PWR1/.test(des) || des === 'C1') {
      hits.push({
        id,
        designator: st && st.designator,
        name: st && st.name,
        x: st && st.x,
        y: st && st.y,
        supplierId: st && st.supplierId,
        device: st && st.component,
      });
    }
  }
  return { proj: info.uuid, hits };
})()
