(async () => {
  const PROJECT = "64325d0e55e0435abd018defb0089a9b";
  const PAGE = "1435cb46f39e48c8a8aadbb84ca81603";
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const doc = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  if (info.uuid !== PROJECT || doc.uuid !== PAGE) {
    return { stop: true, reason: "identity", project: info.uuid, doc: doc.uuid };
  }
  const selKeys = Object.keys(eda.sch_SelectControl || {});
  const utilsKeys = Object.keys(eda.sch_Utils || {}).slice(0, 40);
  const docKeys = Object.keys(eda.sch_Document || {}).filter((k) => /zoom|fit|view|center|select/i.test(k));
  let selected = null;
  let selErr = null;
  try {
    selected = await eda.sch_SelectControl.select(["e2199", "fa16d39836f56347"]);
  } catch (e) {
    selErr = String(e && e.message || e);
  }
  return { selKeys, utilsKeys, docKeys, selected, selErr };
})()
