(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const id = 'ea47c20de228fa3a';
  const st = await eda.sch_PrimitiveComponent.getState(id);
  let bbox = null;
  try { bbox = await eda.sch_PrimitiveComponent.getBoundingBox?.(id); } catch (e) { bbox = { err: String(e && e.message || e) }; }
  let j1 = await eda.sch_PrimitiveComponent.getState('e339');
  return {
    proj: info.uuid,
    new: { id, keys: Object.keys(st || {}), x: st.x, y: st.y, w: st.width, h: st.height, rot: st.rotation, name: st.name, designator: st.designator, addIntoPcb: st.addIntoPcb },
    bbox,
    j1: { id: 'e339', x: j1.x, y: j1.y, name: j1.name, designator: j1.designator },
  };
})()
