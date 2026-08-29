(async () => {
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const w = await eda.sch_PrimitiveWire.get("e82471");
  const line = w.line;
  const segs = [];
  for (let i = 0; i < line.length; i += 4) {
    const q = [line[i], line[i + 1], line[i + 2], line[i + 3]];
    if (q.some((n) => n === 3695 || n === 3705 || n === 2315 || n === 2370)) segs.push(q);
  }
  return { n: line.length, segs, aroundPin: segs.filter((q) => q.includes(2315) || q.includes(3695)) };
})()
