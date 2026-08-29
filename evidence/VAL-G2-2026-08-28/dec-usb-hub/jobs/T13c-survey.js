(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  async function pinsOf(id) {
    const pins = await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(id);
    return (pins || []).map((p) => {
      const st = p.getState ? p.getState() : p;
      return {
        n: String((p.getState_PinNumber && p.getState_PinNumber()) || (st && st.pinNumber) || ''),
        x: (p.getState_X && p.getState_X()) || (st && st.x),
        y: (p.getState_Y && p.getState_Y()) || (st && st.y),
      };
    });
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  return {
    proj: info.uuid,
    dp: await pinsOf('f5380a109ca65eb9'),
    dm: await pinsOf('e105d8e42924191c'),
    r94: await pinsOf('b027c9ae9b996415'),
    u9: (await pinsOf('e8065')).filter((p) => ['13', '14'].includes(p.n)),
  };
})()
