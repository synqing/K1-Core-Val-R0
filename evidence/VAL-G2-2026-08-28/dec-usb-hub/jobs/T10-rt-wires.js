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
        n: String((p.getState_PinNumber && p.getState_PinNumber()) || (st && st.pinNumber) || ''),
        name: (p.getState_PinName && p.getState_PinName()) || (st && st.pinName),
        x: (p.getState_X && p.getState_X()) || (st && st.x),
        y: (p.getState_Y && p.getState_Y()) || (st && st.y),
        net: (p.getState_Net && p.getState_Net()) || (st && st.net),
        id: (p.getId && p.getId()) || (st && st.id) || (p.primitiveId),
      };
    });
  }
  const u6a = await pinsOf('e3295');
  const u6b = await pinsOf('e3673');
  const want = /^(L8|M8|N6|M6|M7|N12|N4|N5)$/;
  const u6usb = {
    e3295: u6a.filter((p) => want.test(p.n) || want.test(String(p.name))),
    e3673: u6b.filter((p) => want.test(p.n) || want.test(String(p.name))),
  };
  const wids = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  const nearRus = [];
  const nearU20us = [];
  for (const id of wids || []) {
    let w;
    try { w = await eda.sch_PrimitiveWire.get(id); } catch (e) { continue; }
    if (!w) continue;
    const line = w.line || w.points || [];
    const xs = [], ys = [];
    if (Array.isArray(line)) {
      for (const seg of line) {
        if (Array.isArray(seg)) {
          for (let i = 0; i < seg.length; i += 2) { xs.push(seg[i]); ys.push(seg[i + 1]); }
        } else if (seg && typeof seg === 'object') {
          xs.push(seg.x); ys.push(seg.y);
        }
      }
    }
    const hitRus = xs.some((x, i) => x >= 520 && x <= 700 && ys[i] >= 4140 && ys[i] <= 4220);
    const hitUs = xs.some((x, i) => x >= 560 && x <= 700 && ys[i] >= 790 && ys[i] <= 820);
    if (hitRus) nearRus.push({ id, net: w.net, line: line, x: w.x, y: w.y });
    if (hitUs) nearU20us.push({ id, net: w.net, line });
  }
  return { proj: info.uuid, u6usb, nearRus, nearU20us, wireCount: (wids || []).length };
})()
