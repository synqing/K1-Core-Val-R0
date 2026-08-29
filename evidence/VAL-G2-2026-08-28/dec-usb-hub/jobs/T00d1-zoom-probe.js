(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const TAB = PAGE + '@' + HUB;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const EC = eda.dmt_EditorControl;
  const proto = Object.getOwnPropertyNames(Object.getPrototypeOf(EC));
  const zoomSigs = proto.filter((n) => /zoom/i.test(n));
  const c = await eda.sch_PrimitiveComponent.get('e339');
  const st = c.getState ? c.getState() : c;
  let pins = [];
  try {
    const pinObjs = await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId('e339');
    pins = (pinObjs || []).slice(0, 4).map((p) => {
      const s = p.getState ? p.getState() : p;
      return { n: s.pinNumber || s.number, x: s.x, y: s.y };
    });
  } catch (e) { pins = [{ err: String(e && e.message || e) }]; }
  let bbox = null;
  for (const fn of ['getBoundingBox', 'getBBox', 'getBounds']) {
    try { if (c[fn]) bbox = { fn, v: await c[fn]() }; } catch (e) { bbox = { fn, err: String(e && e.message || e) }; }
  }
  return {
    proj: info.uuid,
    zoomSigs,
    des: st.designator,
    x: st.x,
    y: st.y,
    pins,
    bbox,
    zoomToLen: EC.zoomTo && EC.zoomTo.length,
    zoomToRegionLen: EC.zoomToRegion && EC.zoomToRegion.length,
  };
})()
