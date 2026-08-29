(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const hits = [];
  for (const id of ids || []) {
    const g = await eda.sch_PrimitiveComponent.get(id);
    const des = String((g && g.designator) || '');
    if (/R94|R95|J12|XOR|USB_REC/.test(des) || des === 'R94-USB' || des === 'R95-USB' || des === 'J12-USB') {
      hits.push({ id, des, name: g.name, x: g.x, y: g.y });
    }
  }
  return { proj: info.uuid, hits, count: (ids || []).length };
})()
