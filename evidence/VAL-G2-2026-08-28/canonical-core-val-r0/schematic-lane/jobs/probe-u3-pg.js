(async () => {
  const PROJECT = "64325d0e55e0435abd018defb0089a9b";
  const PAGE = "1435cb46f39e48c8a8aadbb84ca81603";
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const doc = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  if (info.uuid !== PROJECT || doc.uuid !== PAGE) {
    return { stop: true, reason: "identity", project: info.uuid, doc: doc.uuid };
  }
  const u3 = await eda.sch_PrimitiveComponent.get("e2199");
  let pins = null;
  let pinErr = null;
  try {
    pins = await eda.sch_PrimitiveComponent.getPins("e2199");
  } catch (e) {
    pinErr = String(e && e.message || e);
  }
  let pin5 = null;
  try {
    pin5 = await eda.sch_PrimitivePin.get("e2199", 5);
  } catch (e) {
    pin5 = { err: String(e && e.message || e) };
  }
  let r75 = null;
  try {
    r75 = await eda.sch_PrimitiveComponent.get("e146277");
  } catch (e) {
    r75 = { err: String(e && e.message || e) };
  }
  let buck = null;
  try {
    buck = await eda.sch_PrimitiveWire.get("e146317");
  } catch (e) {
    buck = { err: String(e && e.message || e) };
  }
  const unsaved = typeof eda.sch_Document.isUnsaved === "function"
    ? await eda.sch_Document.isUnsaved()
    : null;
  return {
    project: info.uuid,
    doc: doc.uuid,
    unsaved,
    u3: u3 && {
      primitiveId: u3.primitiveId || u3.id,
      x: u3.x,
      y: u3.y,
      identifier: u3.identifier,
      keys: Object.keys(u3).slice(0, 24),
    },
    pinErr,
    pinCount: Array.isArray(pins) ? pins.length : typeof pins,
    pinSample: Array.isArray(pins) ? pins.slice(0, 3) : pins && Object.keys(pins).slice(0, 12),
    pin5,
    r75: r75 && (r75.err || { x: r75.x, y: r75.y, keys: Object.keys(r75).slice(0, 16) }),
    buck: buck && (buck.err || { net: buck.net, line: Array.from(buck.line || []).slice(0, 24), keys: Object.keys(buck).slice(0, 16) }),
  };
})()
