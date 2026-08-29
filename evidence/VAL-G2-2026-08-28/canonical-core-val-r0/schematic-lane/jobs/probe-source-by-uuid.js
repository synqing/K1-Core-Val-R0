(async () => {
  const PROJECT = "64325d0e55e0435abd018defb0089a9b";
  const PAGE = "1435cb46f39e48c8a8aadbb84ca81603";
  const PCB = "59bef7e87cff4cd580561703b62d8c19";
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const doc = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  const fm = eda.sys_FileManager || {};
  const fmKeys = Object.keys(fm).slice(0, 40);
  let byUuid = null;
  let byUuidErr = null;
  for (const name of ["getDocumentSource", "getSource", "readDocument", "getDocument"]) {
    if (typeof fm[name] !== "function") continue;
    try {
      byUuid = { name, arity: fm[name].length, resultType: typeof (await fm[name](PAGE)) };
    } catch (e) {
      byUuidErr = { name, err: String(e && e.message || e) };
    }
  }
  return {
    project: info.uuid,
    currentDoc: doc && doc.uuid,
    currentType: doc && doc.documentType,
    fmKeys,
    byUuid,
    byUuidErr,
    editorKeys: Object.keys(eda.dmt_EditorControl || {}).slice(0, 30),
  };
})()
