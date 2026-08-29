(async () => {
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  let result = null;
  let err = null;
  try {
    result = await eda.sch_Drc.check(true, false, true);
  } catch (e) {
    err = String(e && e.message || e);
  }
  const summarise = (item) => {
    if (item == null) return item;
    if (typeof item === "string") return item.slice(0, 400);
    if (typeof item !== "object") return String(item);
    const keys = Object.keys(item);
    const out = { keys: keys.slice(0, 20) };
    for (const k of ["type", "level", "severity", "message", "msg", "rule", "name", "net", "component", "primitiveId", "id", "text", "desc", "description", "errorType", "errorCode"]) {
      if (item[k] != null) out[k] = typeof item[k] === "string" ? item[k].slice(0, 400) : item[k];
    }
    return out;
  };
  const arr = Array.isArray(result) ? result : null;
  const types = {};
  if (arr) {
    for (const it of arr) {
      const t = (it && (it.type || it.level || it.severity || it.errorType)) || typeof it;
      types[String(t)] = (types[String(t)] || 0) + 1;
    }
  }
  return {
    uuid: info.uuid,
    err,
    isArray: Array.isArray(result),
    resultType: typeof result,
    resultKeys: result && typeof result === "object" && !Array.isArray(result) ? Object.keys(result).slice(0, 30) : null,
    length: arr ? arr.length : null,
    types,
    sample: arr ? arr.slice(0, 8).map(summarise) : summarise(result),
  };
})()
