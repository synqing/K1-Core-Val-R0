(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const keys = Object.keys(eda).filter((k) => /drc|Drc|DRC/i.test(k));
  let api = null;
  try { api = Object.keys(eda.sch_Drc || {}); } catch (e) { api = String(e && e.message || e); }
  let check = null;
  try {
    const r = await eda.sch_Drc.check(true, true, true);
    check = Array.isArray(r) ? { n: r.length, sample: r.slice(0, 3) } : r;
  } catch (e) {
    check = { err: String(e && e.message || e).slice(0, 200) };
  }
  return { proj: info.uuid, keys, api, check };
})()
