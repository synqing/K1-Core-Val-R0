(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  function rows(pins) {
    return (pins || []).map((p) => {
      const st = p.getState ? p.getState() : p;
      return {
        n: String((p.getState_PinNumber && p.getState_PinNumber()) || (st && st.pinNumber) || ''),
        name: String((p.getState_PinName && p.getState_PinName()) || (st && st.pinName) || ''),
        nc: !!(p.getState_NoConnected && p.getState_NoConnected()) || !!(st && st.noConnected),
        x: (p.getState_X && p.getState_X()) || (st && st.x),
        y: (p.getState_Y && p.getState_Y()) || (st && st.y),
      };
    });
  }
  const j1 = rows(await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId('ea47c20de228fa3a'));
  const u20 = rows(await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId('92edd0bd8901c171'));
  const u6 = rows(await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId('e3673'));
  const want = new Set(['N12', 'N7', 'P6', 'P7', 'USB_OTG1_CHD_B', 'USB_OTG2_DN', 'USB_OTG2_VBUS', 'USB_OTG2_DP']);
  const u6hit = u6.filter((p) => want.has(p.n) || want.has(p.name) || /OTG2|CHD/.test(p.name));
  return {
    proj: info.uuid,
    j1: j1.map((p) => ({ n: p.n, name: p.name, nc: p.nc })),
    u20pin6: u20.filter((p) => p.n === '6' || p.name === 'NC'),
    u6hit,
  };
})()
