(async () => {
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const names = Object.keys(eda).filter((k) => /zoom|view|camera|select|canvas|render/i.test(k));
  const detail = {};
  for (const n of names) {
    const api = eda[n];
    const proto = api && typeof api === "object" ? Object.getOwnPropertyNames(Object.getPrototypeOf(api) || {}) : [];
    detail[n] = proto.filter((p) => p !== "constructor").slice(0, 20);
  }
  const sch = Object.keys(eda).filter((k) => k.startsWith("sch_")).slice(0, 40);
  return { names, detail, sch };
})()
