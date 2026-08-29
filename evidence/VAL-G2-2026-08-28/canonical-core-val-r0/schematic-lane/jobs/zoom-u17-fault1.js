(async () => {
  const PROJECT = "64325d0e55e0435abd018defb0089a9b";
  const PAGE = "1435cb46f39e48c8a8aadbb84ca81603";
  const TAB = PAGE + "@" + PROJECT;
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const doc = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  if (info.uuid !== PROJECT || doc.uuid !== PAGE) return { ok: false, info: info.uuid, doc: doc.uuid };
  const EC = eda.dmt_EditorControl;
  try {
    void EC.zoomToRegion(2160, 2420, 3620, 3840, TAB);
  } catch (e) {
    return { ok: false, err: String(e && e.message || e) };
  }
  return { ok: true, title: document.title };
})()
