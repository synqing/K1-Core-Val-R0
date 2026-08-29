(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const TAB = PAGE + '@' + HUB;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const sel = eda.sch_SelectControl || {};
  const methods = Object.keys(sel);
  const proto = Object.getOwnPropertyNames(Object.getPrototypeOf(sel) || {});
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const has = { e72: (ids || []).includes('e72'), e108: (ids || []).includes('e108') };
  const attempts = [];
  for (const args of [
    [['e72', 'e108'], TAB],
    [['e72', 'e108']],
    ['e72', TAB],
  ]) {
    try {
      const r = await eda.sch_SelectControl.doSelectPrimitives.apply(eda.sch_SelectControl, args);
      attempts.push({ args: JSON.stringify(args).slice(0, 80), ok: true, r: r && typeof r });
    } catch (e) {
      attempts.push({ args: JSON.stringify(args).slice(0, 80), ok: false, err: String(e && e.message || e).slice(0, 80) });
    }
  }
  return { proj: info.uuid, methods, proto: proto.filter((n) => /select|zoom/i.test(n)), has, attempts, idCount: (ids || []).length };
})()
