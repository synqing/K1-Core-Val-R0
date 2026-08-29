(async () => {
  const PROJECT = "64325d0e55e0435abd018defb0089a9b";
  const PAGE = "1435cb46f39e48c8a8aadbb84ca81603";
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const doc = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  if (info.uuid !== PROJECT || doc.uuid !== PAGE) return { stop: true, project: info.uuid, doc: doc.uuid };

  const drop = new Set([
    "2315,3695,2370,3695",
    "2370,3695,2315,3695",
    "2370,3695,2370,3705",
    "2370,3705,2370,3695",
  ]);
  const w = await eda.sch_PrimitiveWire.get("e82471");
  const line = Array.from(w.line);
  const nested = [];
  for (let i = 0; i < line.length; i += 4) {
    const q = [line[i], line[i + 1], line[i + 2], line[i + 3]];
    if (!drop.has(q.join(","))) nested.push(q);
  }
  let r1 = null, e1 = null;
  try { r1 = await eda.sch_PrimitiveWire.modify("e82471", { line: nested }); } catch (e) { e1 = String(e && e.message || e); }
  const w2 = await eda.sch_PrimitiveWire.get("e82471");
  const n2 = (w2.line || []).length;
  const still = [];
  const line2 = Array.from(w2.line || []);
  const isFlat = n2 > 50;
  if (isFlat) {
    for (let i = 0; i < line2.length; i += 4) {
      const q = [line2[i], line2[i + 1], line2[i + 2], line2[i + 3]];
      if (drop.has(q.join(","))) still.push(q);
    }
  }
  return { nestedCount: nested.length, e1, r1id: r1 && r1.primitiveId, nBefore: line.length, nAfter: n2, still, line2head: line2.slice(0, 8) };
})()
