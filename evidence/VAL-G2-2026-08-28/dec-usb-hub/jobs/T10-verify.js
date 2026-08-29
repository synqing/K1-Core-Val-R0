(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  function sourceHash(source) {
    let hash = 2166136261;
    for (let i = 0; i < source.length; i += 1) {
      hash ^= source.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return source.length + ':' + (hash >>> 0).toString(16).padStart(8, '0');
  }
  function parse(source) {
    const recs = [];
    for (const chunk of source.split('\n')) {
      const parts = chunk.split('||');
      if (parts.length < 2) continue;
      try {
        const head = JSON.parse(parts[0].replace(/^\|/, ''));
        const body = JSON.parse(parts[1].replace(/\|$/, ''));
        recs.push({ ...head, ...body });
      } catch (e) { /* skip */ }
    }
    return recs;
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
      };
    });
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  const source = await eda.sys_FileManager.getDocumentSource();
  const recs = parse(source);
  const nets = recs.filter((r) => r.key === 'NET');
  const pick = (n) => nets.filter((r) => r.value === n).map((r) => ({ parentId: r.parentId, x: r.x, y: r.y }));
  const d1 = await eda.sch_PrimitiveComponent.get('e252');
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  const l8 = (await pinsOf('e3673')).find((p) => p.n === 'L8');
  const m8 = (await pinsOf('e3673')).find((p) => p.n === 'M8');
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    components: (ids || []).length,
    wires: (wires || []).length,
    d1: { des: d1.designator, name: d1.name, x: d1.x, y: d1.y },
    nets: {
      USB_DP_UP: pick('USB_DP_UP'),
      USB_DM_UP: pick('USB_DM_UP'),
      USB_DP_RT: pick('USB_DP_RT'),
      USB_DN_RT: pick('USB_DN_RT'),
      USB_DP_PROT: pick('USB_DP_PROT'),
      USB_DN_PROT: pick('USB_DN_PROT'),
    },
    l8, m8,
    counts: {
      USB_DP_UP: (source.match(/USB_DP_UP/g) || []).length,
      USB_DM_UP: (source.match(/USB_DM_UP/g) || []).length,
      USB_DP_RT: (source.match(/USB_DP_RT/g) || []).length,
      USB_DN_RT: (source.match(/USB_DN_RT/g) || []).length,
    },
  };
})()
