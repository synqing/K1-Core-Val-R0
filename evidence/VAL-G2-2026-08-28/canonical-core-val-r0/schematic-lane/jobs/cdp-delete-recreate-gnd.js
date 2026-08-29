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
  if (!w || !w.line) return { stop: true, reason: "missing e82471" };
  const line = Array.from(w.line);
  const keep = [];
  for (let i = 0; i < line.length; i += 4) {
    const q = [line[i], line[i + 1], line[i + 2], line[i + 3]];
    if (!drop.has(q.join(","))) keep.push(q);
  }
  const beforeIds = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  const deleted = await eda.sch_PrimitiveWire.delete("e82471");
  const gone = !(await eda.sch_PrimitiveWire.get("e82471"));
  if (!deleted || !gone) {
    return { stop: true, reason: "delete refused", deleted, gone, keep: keep.length };
  }

  const created = [];
  const createErr = [];
  const first = await eda.sch_PrimitiveWire.create(keep[0], "GND");
  created.push({ i: 0, id: first && (first.primitiveId || first.id), type: first && first.primitiveType });
  for (let i = 1; i < keep.length; i++) {
    try {
      const c = await eda.sch_PrimitiveWire.create(keep[i], "GND");
      created.push({ i, id: c && (c.primitiveId || c.id) });
    } catch (e) {
      createErr.push({ i, err: String(e && e.message || e) });
    }
  }
  let fault = null;
  let faultErr = null;
  try {
    fault = await eda.sch_PrimitiveWire.create([2315, 3695, 2340, 3695], "LED_FAULT_L_N");
  } catch (e) {
    faultErr = String(e && e.message || e);
  }
  const saved = await eda.sch_Document.save();
  const afterIds = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  const added = afterIds.filter((id) => !beforeIds.includes(id));
  const stillOld = afterIds.includes("e82471");
  const faultObj = fault && (await eda.sch_PrimitiveWire.get(fault.primitiveId || fault.id).catch(() => null));
  return {
    deleted,
    gone,
    keep: keep.length,
    createdIds: created.map((c) => c.id),
    createErr,
    faultId: fault && (fault.primitiveId || fault.id),
    faultNet: faultObj && faultObj.net,
    faultLine: faultObj && faultObj.line,
    faultErr,
    saved,
    stillOld,
    added,
    afterCount: afterIds.length,
    beforeCount: beforeIds.length,
  };
})()
