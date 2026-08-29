(async () => {
  const PROJECT = "64325d0e55e0435abd018defb0089a9b";
  const PAGE = "1435cb46f39e48c8a8aadbb84ca81603";
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const doc = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  if (info.uuid !== PROJECT || doc.uuid !== PAGE) {
    return { stop: true, reason: "identity", project: info.uuid, doc: doc.uuid };
  }

  const before = {
    e146317: await eda.sch_PrimitiveWire.get("e146317"),
    e146320: await eda.sch_PrimitiveWire.get("e146320"),
    e2930: await eda.sch_PrimitiveWire.get("e2930"),
    e24643: await eda.sch_PrimitiveWire.get("e24643"),
  };

  let created = null;
  let createErr = null;
  try {
    created = await eda.sch_PrimitiveWire.create(
      [1560, 4565, 990, 4565, 990, 4480],
      "BUCK_PG"
    );
  } catch (e) {
    createErr = String(e && e.message || e);
  }

  let created2 = null;
  let create2Err = null;
  if (createErr || !created) {
    try {
      created2 = await eda.sch_PrimitiveWire.create([1560, 4565, 990, 4565], "BUCK_PG");
    } catch (e) {
      create2Err = String(e && e.message || e);
    }
  }

  let drop = null;
  let dropErr = null;
  const polylineId = created && (created.primitiveId || created.id);
  const horizId = created2 && (created2.primitiveId || created2.id);
  if (!polylineId && horizId) {
    try {
      drop = await eda.sch_PrimitiveWire.create([990, 4565, 990, 4480], "BUCK_PG");
    } catch (e) {
      dropErr = String(e && e.message || e);
    }
  }

  let saved = null;
  try {
    saved = await eda.sch_Document.save();
  } catch (e) {
    saved = String(e && e.message || e);
  }

  const after = {
    e146317: await eda.sch_PrimitiveWire.get("e146317"),
    e146320: await eda.sch_PrimitiveWire.get("e146320"),
  };

  const summarise = (w) => w && ({
    id: w.primitiveId,
    net: w.net,
    line: Array.from(w.line || []).slice(0, 32),
    lineLen: Array.from(w.line || []).length,
  });

  return {
    project: info.uuid,
    doc: doc.uuid,
    before: {
      e146317: summarise(before.e146317),
      e146320: summarise(before.e146320),
      e2930: summarise(before.e2930),
      e24643: summarise(before.e24643),
    },
    created,
    createErr,
    created2,
    create2Err,
    drop,
    dropErr,
    polylineId,
    horizId,
    saved,
    after: {
      e146317: summarise(after.e146317),
      e146320: summarise(after.e146320),
    },
  };
})()
