(async () => {
  const PROJECT = "64325d0e55e0435abd018defb0089a9b";
  const PAGE = "1435cb46f39e48c8a8aadbb84ca81603";
  const PCB = "59bef7e87cff4cd580561703b62d8c19";
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== PROJECT) {
    return { stop: true, reason: "identity", project: info.uuid };
  }
  const before = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  let opened = null;
  let openErr = null;
  try {
    opened = await eda.dmt_EditorControl.openDocument(PAGE);
  } catch (e) {
    openErr = String(e && e.message || e);
  }
  await new Promise((r) => setTimeout(r, 400));
  const after = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  return {
    project: info.uuid,
    before: before && { uuid: before.uuid, type: before.documentType },
    opened,
    openErr,
    after: after && { uuid: after.uuid, type: after.documentType },
    restoredLater: false,
    wantRestoreTo: PCB,
  };
})()
