(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  async function pinsOf(id) {
    const pins = await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(id);
    return (pins || []).map((p) => {
      const st = p.getState ? p.getState() : p;
      return {
        n: (p.getState_PinNumber && p.getState_PinNumber()) || (st && st.pinNumber),
        name: (p.getState_PinName && p.getState_PinName()) || (st && st.pinName),
        x: (p.getState_X && p.getState_X()) || (st && st.x),
        y: (p.getState_Y && p.getState_Y()) || (st && st.y),
        net: (p.getState_Net && p.getState_Net()) || (st && st.net),
      };
    });
  }
  return {
    proj: info.uuid,
    c120: await pinsOf('004d113915448a0a'),
    c2: await pinsOf('e108'),
    c1: await pinsOf('e72'),
  };
})()
