(async () => {
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const names = ["sch_PrimitiveWire", "sch_PrimitiveLine", "sch_PrimitiveAttribute", "sch_PrimitivePin"];
  const out = { uuid: info.uuid, apis: {} };
  for (const n of names) {
    const api = eda[n];
    if (!api) {
      out.apis[n] = { present: false };
      continue;
    }
    out.apis[n] = {
      present: true,
      own: Object.keys(api),
      proto: Object.getOwnPropertyNames(Object.getPrototypeOf(api) || {}).filter((k) => k !== "constructor"),
    };
  }
  return out;
})()
