(async () => {
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const drc = eda.sch_Drc || {};
  const keys = Object.keys(drc);
  const proto = Object.getOwnPropertyNames(Object.getPrototypeOf(drc) || {});
  let last = null;
  try { last = typeof drc.getLastResult === "function" ? await drc.getLastResult() : null; } catch (e) { last = String(e); }
  let list = null;
  try { list = typeof drc.getErrorList === "function" ? await drc.getErrorList() : null; } catch (e) { list = String(e); }
  const check = await drc.check(true, false, true);
  return {
    keys,
    proto,
    lastType: last && typeof last,
    lastSample: last && JSON.stringify(last).slice(0, 500),
    listType: list && typeof list,
    listSample: list && JSON.stringify(list).slice(0, 500),
    check,
  };
})()
