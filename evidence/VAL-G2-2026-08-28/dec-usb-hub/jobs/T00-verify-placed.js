(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  function sourceHash(source) {
    let hash = 2166136261;
    for (let i = 0; i < source.length; i += 1) {
      hash ^= source.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return source.length + ':' + (hash >>> 0).toString(16).padStart(8, '0');
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const interesting = [];
  for (const id of ids || []) {
    try {
      const c = await eda.sch_PrimitiveComponent.get(id);
      const st = c && (c.getState ? c.getState() : c);
      const name = String((st && (st.name || st.deviceName)) || '');
      const des = String((st && st.designator) || '');
      if (name.includes('7005A') || name.includes('USB4105') || des.includes('J1') || des === 'U?') {
        interesting.push({ id, name: name.slice(0, 80), designator: des.slice(0, 40), x: st && st.x, y: st && st.y });
      }
    } catch (e) { /* skip */ }
  }
  const neu = interesting.find((n) => n.name.includes('7005A') || n.designator === 'U?');
  let pins = [];
  if (neu) {
    try {
      const pinObjs = await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(neu.id);
      pins = (pinObjs || []).map((p) => {
        const st = p && (p.getState ? p.getState() : p);
        return { n: st && (st.pinNumber || st.number), name: st && (st.pinName || st.name) };
      });
    } catch (e) { pins = [{ error: String(e && e.message || e) }]; }
  }
  const source = await eda.sys_FileManager.getDocumentSource();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  const texts = await eda.sch_PrimitiveText.getAllPrimitiveId();
  return {
    proj: info.uuid,
    friendly: info.friendlyName,
    sourceHash: typeof source === 'string' ? sourceHash(source) : null,
    sourceIsSymbol: typeof source === 'string' && source.includes('"docType":"SYMBOL"'),
    components: (ids || []).length,
    wires: (wires || []).length,
    texts: (texts || []).length,
    interesting,
    newId: neu && neu.id,
    pinCount: pins.length,
    pins,
  };
})()
