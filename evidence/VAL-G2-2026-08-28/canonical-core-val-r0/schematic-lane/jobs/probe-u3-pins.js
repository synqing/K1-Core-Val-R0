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
  const r75 = await eda.sch_PrimitiveComponent.get("e146277");
  let pinList = null;
  let pinListErr = null;
  try {
    pinList = await eda.sch_Component.getPins(u3.uniqueId || u3.primitiveId);
  } catch (e) {
    pinListErr = String(e && e.message || e);
  }
  const pinApis = Object.keys(eda).filter((k) => /pin|Pin/i.test(k)).slice(0, 40);
  const schKeys = Object.keys(eda).filter((k) => /^sch_/.test(k)).slice(0, 80);
  return {
    designator: u3.designator,
    name: u3.name,
    uniqueId: u3.uniqueId,
    net: u3.net,
    r75designator: r75.designator,
    r75name: r75.name,
    pinListErr,
    pinListType: pinList && pinList.constructor && pinList.constructor.name,
    pinListLen: Array.isArray(pinList) ? pinList.length : null,
    pinApis,
    schKeys,
    otherProperty: u3.otherProperty,
  };
})()
