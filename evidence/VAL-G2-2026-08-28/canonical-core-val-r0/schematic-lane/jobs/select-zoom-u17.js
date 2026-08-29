(async () => {
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== "64325d0e55e0435abd018defb0089a9b") return { stop: true };
  const SC = eda.dmt_SelectControl;
  const proto = Object.getOwnPropertyNames(Object.getPrototypeOf(SC) || {});
  let sel = null, selErr = null;
  try {
    sel = await SC.select(["b118f78741a245ce", "2639a4b072b190b5"]);
  } catch (e) {
    selErr = String(e && e.message || e);
    try { sel = await SC.select("b118f78741a245ce"); } catch (e2) { selErr += " | " + String(e2 && e2.message || e2); }
  }
  const EC = eda.dmt_EditorControl;
  try {
    await Promise.race([
      EC.zoomToSelectedPrimitives(),
      new Promise((r) => setTimeout(r, 2000)),
    ]);
  } catch (e) { /* ignore */ }
  return { proto: proto.slice(0, 30), sel, selErr };
})()
