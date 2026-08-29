(async () => {
  const PROJECT = "64325d0e55e0435abd018defb0089a9b";
  const PAGE = "1435cb46f39e48c8a8aadbb84ca81603";
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const doc = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  if (info.uuid !== PROJECT || doc.uuid !== PAGE) return { ok: false, info: info.uuid, doc: doc.uuid };
  const EC = eda.dmt_EditorControl;
  let zoom = null;
  try {
    zoom = EC.zoomTo("b118f78741a245ce");
  } catch (e) {
    zoom = String(e && e.message || e);
  }
  await new Promise((r) => setTimeout(r, 1500));
  let img = null;
  let imgErr = null;
  try {
    img = await EC.getCurrentRenderedAreaImage();
  } catch (e) {
    imgErr = String(e && e.message || e);
  }
  const describe = (v) => {
    if (v == null) return { t: String(v) };
    if (typeof v === "string") return { t: "string", n: v.length, head: v.slice(0, 40) };
    if (typeof v === "object") return { t: v.constructor && v.constructor.name, keys: Object.keys(v).slice(0, 20), sample: JSON.stringify(v).slice(0, 200) };
    return { t: typeof v };
  };
  return { ok: true, zoom: describe(zoom), imgErr, img: describe(img) };
})()
