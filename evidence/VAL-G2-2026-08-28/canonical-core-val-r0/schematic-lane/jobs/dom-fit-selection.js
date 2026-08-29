(async () => {
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== "64325d0e55e0435abd018defb0089a9b") return { stop: true };
  await eda.sch_SelectControl.doSelectPrimitives(["b118f78741a245ce", "2639a4b072b190b5"]);
  const selected = await eda.sch_SelectControl.getAllSelectedPrimitives_PrimitiveId();
  const btn = [...document.querySelectorAll("[title]")].find((el) => (el.getAttribute("title") || "") === "Fit Selection View");
  if (!btn) return { selected, clicked: false, reason: "no button" };
  const r = btn.getBoundingClientRect();
  btn.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true, view: window }));
  btn.click();
  return { selected, clicked: true, x: r.x, y: r.y, w: r.width, h: r.height };
})()
