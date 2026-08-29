(async () => {
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  await eda.sch_SelectControl.doSelectPrimitives(["b118f78741a245ce", "2639a4b072b190b5"]);
  const selected = await eda.sch_SelectControl.getAllSelectedPrimitives_PrimitiveId();
  const rulers = [...document.querySelectorAll("canvas.rulerh")].map((c) => {
    const r = c.getBoundingClientRect();
    return { w: r.width, h: r.height, x: r.x, y: r.y };
  });
  const buttons = {};
  for (const el of document.querySelectorAll("[title]")) {
    const t = el.getAttribute("title") || "";
    if (/Fit Selection|Zoom In|Fit All/i.test(t)) {
      const r = el.getBoundingClientRect();
      buttons[t] = { x: r.x, y: r.y, w: r.width, h: r.height };
    }
  }
  return { uuid: info.uuid, selected, rulers, buttons };
})()
