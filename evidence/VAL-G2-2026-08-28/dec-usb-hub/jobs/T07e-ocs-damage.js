(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
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
  let merged = null;
  try {
    const prim = await eda.sch_PrimitiveWire.getPrimitiveById('5dcc3c3eb557b5e8');
    const st = prim && prim.getState ? prim.getState() : prim;
    merged = {
      id: '5dcc3c3eb557b5e8',
      net: st && (st.net || st.netName),
      keys: st ? Object.keys(st) : [],
      line: st && st.line,
      points: st && st.points,
    };
  } catch (e) {
    merged = { error: String(e && e.message || e) };
  }
  const api = Object.keys(eda.sch_PrimitiveWire || {}).filter((k) => /delete|modify|split|break|remove|net/i.test(k));
  return {
    proj: info.uuid,
    wireApi: api,
    merged,
    u21: await pinsOf('fb7c84f0a582bd9c'),
    u22: await pinsOf('4c311982f7a3bb0d'),
    u23: await pinsOf('125f3f5842b2d308'),
    u24: await pinsOf('8d95d838df2d5f43'),
    u25: await pinsOf('cace78f52f4c7139'),
    u20_ocs: (await pinsOf('92edd0bd8901c171')).filter((p) => p.n === '8' || p.n === '12' || p.n === '7' || p.n === '11'),
  };
})()
