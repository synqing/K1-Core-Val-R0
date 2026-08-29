(async () => {
  const PROJECT = "64325d0e55e0435abd018defb0089a9b";
  const PAGE = "1435cb46f39e48c8a8aadbb84ca81603";
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const doc = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  if (info.uuid !== PROJECT || doc.uuid !== PAGE) return { ok: false };
  const EC = eda.dmt_EditorControl;
  try {
    await Promise.race([
      EC.zoomTo("b118f78741a245ce"),
      new Promise((r) => setTimeout(r, 2500)),
    ]);
  } catch (e) { /* zoomTo may hang or reject; continue */ }
  const blob = await EC.getCurrentRenderedAreaImage();
  const ab = await blob.arrayBuffer();
  const bytes = new Uint8Array(ab);
  let binary = "";
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
  }
  return { ok: true, bytes: bytes.length, type: blob.type, b64: btoa(binary) };
})()
