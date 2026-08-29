(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const zeros = [];
  for (const id of ids || []) {
    const g = await eda.sch_PrimitiveComponent.get(id);
    const name = String((g && g.name) || '');
    const des = String((g && g.designator) || '');
    if (/^0\s*[ΩohmR]/i.test(name) || name === '0' || name === '0R' || name === '0Ω' || /RUSB_.*PWR1/.test(des)) {
      zeros.push({
        id, des, name,
        x: g.x, y: g.y,
        supplierId: g.supplierId,
        component: g.component,
      });
    }
  }
  return { proj: info.uuid, zeros };
})()
