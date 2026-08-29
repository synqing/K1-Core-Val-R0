(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const east = [];
  for (const id of ids || []) {
    const g = await eda.sch_PrimitiveComponent.get(id);
    if (!g) continue;
    if (g.x >= 1850 && g.x <= 2400 && g.y >= 500 && g.y <= 1400) {
      east.push({ id, des: g.designator, name: g.name, x: g.x, y: g.y });
    }
  }
  return { proj: info.uuid, east };
})()
