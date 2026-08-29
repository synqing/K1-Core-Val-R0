(async () => {
  const PROJECT = "64325d0e55e0435abd018defb0089a9b";
  const PAGE = "1435cb46f39e48c8a8aadbb84ca81603";
  const PCB = "59bef7e87cff4cd580561703b62d8c19";
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const doc = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  if (info.uuid !== PROJECT || doc.uuid !== PAGE) {
    return { stop: true, reason: "identity", project: info.uuid, doc: doc.uuid };
  }
  const u3 = await eda.sch_PrimitiveComponent.get("e2199");
  const pinApi = eda.sch_PrimitivePin;
  const pinKeys = pinApi ? Object.keys(pinApi).slice(0, 20) : null;
  let pins = null;
  let pinsErr = null;
  try {
    if (u3 && typeof u3.getPins === "function") pins = await u3.getPins();
    else if (pinApi && typeof pinApi.getByComponent === "function") pins = await pinApi.getByComponent("e2199");
  } catch (e) {
    pinsErr = String(e && e.message || e);
  }
  let net5 = null;
  try {
    net5 = await eda.sch_PrimitiveWire.get("383f2a4e69ce840d");
  } catch (e) {
    net5 = { err: String(e && e.message || e) };
  }
  let n3 = null;
  try {
    n3 = await eda.sch_PrimitiveWire.get("e24643");
  } catch (e) {
    n3 = { err: String(e && e.message || e) };
  }
  const summarise = (w) => w && !w.err && {
    id: w.primitiveId,
    net: w.net,
    line: Array.from(w.line || []),
  };
  return {
    designator: u3.designator,
    x: u3.x,
    y: u3.y,
    pinKeys,
    pinsErr,
    pinCount: Array.isArray(pins) ? pins.length : typeof pins,
    pinSample: Array.isArray(pins) ? pins.slice(0, 12).map((p) => ({
      n: p.pinNumber || p.number,
      name: p.pinName || p.name,
      x: p.x,
      y: p.y,
      net: p.net,
      nc: p.noConnected,
    })) : pins,
    buck: summarise(net5) || net5,
    v3: summarise(n3) || n3,
    u3net: u3.net,
  };
})()
