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
  const id = 'fd3dd96d58a6e4c4';
  const w = await eda.sch_PrimitiveWire.get(id);
  const proto = [];
  let o = w;
  for (let i = 0; i < 4 && o; i += 1) {
    proto.push(Object.getOwnPropertyNames(o).slice(0, 40));
    o = Object.getPrototypeOf(o);
  }
  const st = w && w.getState ? w.getState() : null;
  const stKeys = st && typeof st === 'object' ? Object.keys(st).slice(0, 40) : typeof st;
  let lineGetter = null;
  try { lineGetter = w.getState_Line && w.getState_Line(); } catch (e) { lineGetter = 'err ' + e.message; }
  let netGetter = null;
  try { netGetter = w.getState_Net && w.getState_Net(); } catch (e) { netGetter = 'err ' + e.message; }
  return {
    proj: info.uuid,
    type: typeof w,
    proto,
    stKeys,
    stNet: st && st.net,
    stLineType: st && (Array.isArray(st.line) ? 'arr' + st.line.length : typeof st.line),
    lineGetterType: Array.isArray(lineGetter) ? 'arr' + lineGetter.length : typeof lineGetter,
    lineGetterHead: Array.isArray(lineGetter) ? lineGetter.slice(0, 12) : lineGetter,
    netGetter,
  };
})()
