(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const pins = await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId('e8065');
  const rows = (pins || []).map((p) => {
    const st = p.getState ? p.getState() : p;
    return {
      n: String((p.getState_PinNumber && p.getState_PinNumber()) || (st && st.pinNumber) || ''),
      name: (p.getState_PinName && p.getState_PinName()) || (st && st.pinName) || '',
      x: (p.getState_X && p.getState_X()) || (st && st.x),
      y: (p.getState_Y && p.getState_Y()) || (st && st.y),
      nc: (p.getState_NoConnected && p.getState_NoConnected()) || (st && st.noConnected) || false,
    };
  }).filter((p) => Number(p.n) >= 6 && Number(p.n) <= 16);
  rows.sort((a, b) => Number(a.n) - Number(b.n));
  return { proj: (await eda.dmt_Project.getCurrentProjectInfo()).uuid, rows };
})()
