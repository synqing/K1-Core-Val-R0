(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
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
        name: (p.getState_PinName && p.getState_PinName()) || (st && st.pinName) || '',
        x: (p.getState_X && p.getState_X()) || (st && st.x),
        y: (p.getState_Y && p.getState_Y()) || (st && st.y),
      };
    });
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const source = await eda.sys_FileManager.getDocumentSource();
  const recs = parse(source);
  const des = recs.filter((r) => r.key === 'Designator' && /J7|R21-ESP|R22-ESP|U10-ESP/.test(String(r.value || '')));
  const nets = recs.filter((r) => r.key === 'NET');
  const pick = (n) => nets.filter((r) => r.value === n).map((r) => ({ parentId: r.parentId, x: r.x, y: r.y }));
  const j7id = (des.find((r) => r.value === 'J7-ESP') || {}).parentId;
  let j7 = null;
  if (j7id) {
    const c = await eda.sch_PrimitiveComponent.get(j7id);
    j7 = { id: j7id, des: c.designator, x: c.x, y: c.y, pins: await pinsOf(j7id) };
  }
  return {
    proj: info.uuid,
    des: des.map((r) => ({ parentId: r.parentId, value: r.value, x: r.x, y: r.y })),
    j7,
    USB_CC1: pick('USB_CC1'),
    USB_CC2: pick('USB_CC2'),
    S3_VBUS: pick('S3_VBUS'),
    USB_DP: pick('USB_DP'),
    USB_DM: pick('USB_DM'),
    USB_DP_ESD: pick('USB_DP_ESD'),
    USB_DM_ESD: pick('USB_DM_ESD'),
    USB_DP_S3: pick('USB_DP_S3'),
    USB_DM_S3: pick('USB_DM_S3'),
    USB_DP_J1: pick('USB_DP_J1'),
    USB_DN_J1: pick('USB_DN_J1'),
  };
})()
