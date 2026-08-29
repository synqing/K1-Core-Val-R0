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
  async function part(id) {
    const g = await eda.sch_PrimitiveComponent.get(id);
    return {
      id,
      des: g && g.designator,
      name: g && g.name,
      x: g && g.x,
      y: g && g.y,
      pins: await pinsOf(id),
    };
  }
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const named = [];
  for (const id of ids || []) {
    const g = await eda.sch_PrimitiveComponent.get(id);
    const des = String((g && g.designator) || '');
    if (/D1-PWR1|RUSB_DP-PWR1|RUSB_DN-PWR1|U20-USB|U6-RTC|J1-PWR1|CUSBVBUS/.test(des)) {
      named.push({ id, des, name: g.name, x: g.x, y: g.y });
    }
  }
  const u20 = named.find((p) => p.des === 'U20-USB');
  const d1 = named.find((p) => p.des === 'D1-PWR1');
  const rdp = named.find((p) => p.des === 'RUSB_DP-PWR1');
  const rdn = named.find((p) => p.des === 'RUSB_DN-PWR1');
  const j1 = named.filter((p) => /J1/.test(p.des));
  const u6 = named.filter((p) => /U6/.test(p.des));
  return {
    proj: info.uuid,
    named,
    d1: d1 && await part(d1.id),
    rdp: rdp && await part(rdp.id),
    rdn: rdn && await part(rdn.id),
    u20: u20 && await part(u20.id),
    j1,
    u6,
  };
})()
