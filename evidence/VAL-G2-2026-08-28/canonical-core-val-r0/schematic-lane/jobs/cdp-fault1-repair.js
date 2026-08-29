(async () => {
  const PROJECT = "64325d0e55e0435abd018defb0089a9b";
  const PAGE = "1435cb46f39e48c8a8aadbb84ca81603";
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const doc = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  if (info.uuid !== PROJECT || doc.uuid !== PAGE) {
    return { stop: true, reason: "identity", project: info.uuid, doc: doc.uuid };
  }

  const drop = new Set([
    "2315,3695,2370,3695",
    "2370,3695,2315,3695",
    "2370,3695,2370,3705",
    "2370,3705,2370,3695",
  ]);

  const w = await eda.sch_PrimitiveWire.get("e82471");
  const line = Array.from(w.line);
  const pruned = [];
  const dropped = [];
  for (let i = 0; i < line.length; i += 4) {
    const q = [line[i], line[i + 1], line[i + 2], line[i + 3]];
    const key = q.join(",");
    if (drop.has(key)) dropped.push(q);
    else pruned.push(...q);
  }

  let modifyResult = null;
  let modifyErr = null;
  try {
    modifyResult = await eda.sch_PrimitiveWire.modify("e82471", { line: pruned });
  } catch (e) {
    modifyErr = String(e && e.message || e);
  }

  const w2 = await eda.sch_PrimitiveWire.get("e82471");
  const still = [];
  const line2 = Array.from(w2.line || []);
  for (let i = 0; i < line2.length; i += 4) {
    const q = [line2[i], line2[i + 1], line2[i + 2], line2[i + 3]];
    if (drop.has(q.join(","))) still.push(q);
  }

  let del = null;
  let delErr = null;
  try {
    del = await eda.sch_PrimitiveAttribute.delete("448ea2106b22ac53");
  } catch (e) {
    delErr = String(e && e.message || e);
  }

  let created = null;
  let createErr = null;
  try {
    created = await eda.sch_PrimitiveWire.create([2315, 3695, 2340, 3695], "LED_FAULT_L_N");
  } catch (e) {
    createErr = String(e && e.message || e);
  }

  let saved = null;
  try {
    saved = await eda.sch_Document.save();
  } catch (e) {
    saved = String(e && e.message || e);
  }

  return {
    dropped,
    pruneBefore: line.length,
    pruneAfter: (w2.line || []).length,
    still,
    modifyType: modifyResult == null ? typeof modifyResult : (modifyResult && modifyResult.primitiveId) || Object.keys(modifyResult || {}).slice(0, 8),
    modifyErr,
    del,
    delErr,
    created: created && (created.primitiveId || created.id || Object.keys(created).slice(0, 8)),
    createErr,
    saved,
    w2net: w2.net,
  };
})()
