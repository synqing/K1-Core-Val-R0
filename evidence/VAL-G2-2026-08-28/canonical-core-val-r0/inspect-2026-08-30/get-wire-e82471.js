(async () => {
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const w = await eda.sch_PrimitiveWire.get("e82471");
  const keys = w && typeof w === "object" ? Object.keys(w) : [];
  const line = w && (w.line || w.points || w.path || w.geometry);
  const net = w && (w.net || w.netName);
  return {
    uuid: info.uuid,
    keys,
    net,
    lineType: Array.isArray(line) ? "array" : typeof line,
    lineLen: Array.isArray(line) ? line.length : null,
    lineSample: Array.isArray(line) ? line.slice(0, 8) : line,
    rawSample: w && JSON.stringify(w).slice(0, 1500),
  };
})()
