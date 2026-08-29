(async () => {
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const w = await eda.sch_PrimitiveWire.get("e82471");
  const lab = await eda.sch_PrimitiveAttribute.get("6c2d22961bad8b84");
  const line = w && w.line;
  const hasFaultSeg = Array.isArray(line) && line.join(",").includes("2370,3695,2315,3695");
  const hasVert = Array.isArray(line) && line.join(",").includes("2370,3695,2370,3705");
  return {
    uuid: info.uuid,
    wireNet: w && w.net,
    lineLen: Array.isArray(line) ? line.length : null,
    hasFaultSeg,
    hasVert,
    label: lab && { value: lab.value, key: lab.key, parent: lab.parentPrimitiveId },
  };
})()
