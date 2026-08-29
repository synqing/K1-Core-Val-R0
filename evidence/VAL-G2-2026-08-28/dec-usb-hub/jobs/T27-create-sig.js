(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const TARGET = '54d2a25bce4b44c3af878e8b91af3554';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== TARGET) return { stop: true, uuid: current && current.uuid };
  const c2 = await eda.sch_PrimitiveComponent.get('e108');
  const rcc1 = await eda.sch_PrimitiveComponent.get('e37');
  return {
    create: String(eda.sch_PrimitiveComponent.create).slice(0, 500),
    modify: String(eda.sch_PrimitiveComponent.modify).slice(0, 400),
    createWire: String(eda.sch_PrimitiveWire.create).slice(0, 300),
    c2Keys: c2 && Object.keys(c2).slice(0, 40),
    c2: c2 && {
      id: c2.id || c2.primitiveId,
      x: c2.x, y: c2.y,
      device: c2.deviceUuid || c2.device,
      name: c2.name,
      designator: c2.designator,
    },
    rcc1: rcc1 && { id: rcc1.id, x: rcc1.x, y: rcc1.y, device: rcc1.deviceUuid || rcc1.device },
  };
})()
