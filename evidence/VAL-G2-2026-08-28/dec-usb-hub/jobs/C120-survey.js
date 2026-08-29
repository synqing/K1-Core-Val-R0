(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const id = '004d113915448a0a';
  const c = await eda.sch_PrimitiveComponent.get(id);
  const pins = [];
  for (const pid of (c.pinIds || c.pins || [])) {
    try {
      const p = await eda.sch_PrimitivePin.get(pid);
      pins.push({
        id: pid,
        pinNumber: p && p.pinNumber,
        name: p && p.name,
        x: p && p.x,
        y: p && p.y,
        net: p && p.net,
        connected: p && (p.connectedPrimitiveIds || p.connectedIds),
      });
    } catch (e) {
      pins.push({ id: pid, err: String(e && e.message || e).slice(0, 80) });
    }
  }
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const nearby = [];
  for (const cid of ids || []) {
    const g = await eda.sch_PrimitiveComponent.get(cid);
    if (!g) continue;
    const x = g.x, y = g.y;
    if (x >= 1100 && x <= 1600 && y >= 1100 && y <= 1500) {
      nearby.push({ id: cid, des: g.designator, name: g.name, x, y, net: g.net });
    }
  }
  return {
    proj: info.uuid,
    c120: { id, des: c.designator, name: c.name, x: c.x, y: c.y, net: c.net, pinIds: c.pinIds || c.pins },
    pins,
    nearby,
  };
})()
