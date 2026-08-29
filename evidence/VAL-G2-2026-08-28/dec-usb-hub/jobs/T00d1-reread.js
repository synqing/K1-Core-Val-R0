(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid !== HUB || info.uuid === LIVE) return { stop: true, uuid: info && info.uuid };
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  const ids = ['e339', 'ea47c20de228fa3a', '92edd0bd8901c171'];
  const rows = [];
  for (const id of ids) {
    const c = await eda.sch_PrimitiveComponent.get(id);
    const st = c.getState ? c.getState() : c;
    rows.push({
      id,
      designator: st.designator,
      name: st.name,
      x: st.x,
      y: st.y,
      supplierId: st.supplierId,
      manufacturerId: st.manufacturerId,
    });
  }
  return { proj: info.uuid, rows };
})()
