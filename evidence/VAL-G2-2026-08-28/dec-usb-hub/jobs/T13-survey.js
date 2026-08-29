(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  async function pinsOf(id) {
    const pins = await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(id);
    return (pins || []).map((p) => {
      const st = p.getState ? p.getState() : p;
      return {
        n: String((p.getState_PinNumber && p.getState_PinNumber()) || (st && st.pinNumber) || ''),
        name: (p.getState_PinName && p.getState_PinName()) || (st && st.pinName) || '',
        x: (p.getState_X && p.getState_X()) || (st && st.x),
        y: (p.getState_Y && p.getState_Y()) || (st && st.y),
      };
    });
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const u20 = await pinsOf('92edd0bd8901c171');
  const r94 = await eda.sch_PrimitiveComponent.get('b027c9ae9b996415');
  const r95 = await eda.sch_PrimitiveComponent.get('24561118da702cc5');
  return {
    proj: info.uuid,
    u20dn: u20.filter((p) => ['2', '3', '4', '5', '19', '20'].includes(p.n)),
    r94: { des: r94.designator, name: r94.name, x: r94.x, y: r94.y, pins: await pinsOf('b027c9ae9b996415') },
    r95: { des: r95.designator, name: r95.name, x: r95.x, y: r95.y, pins: await pinsOf('24561118da702cc5') },
  };
})()
