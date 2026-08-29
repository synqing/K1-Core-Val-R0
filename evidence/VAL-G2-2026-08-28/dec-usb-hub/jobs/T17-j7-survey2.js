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
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const source = await eda.sys_FileManager.getDocumentSource();
  const recs = parse(source);
  const des = recs.filter((r) => r.key === 'Designator' && /J7|R21-ESP|R22-ESP|U10-ESP|R71-ESP|R73-ESP/.test(String(r.value || '')));
  const nets = recs.filter((r) => r.key === 'NET');
  const pick = (n) => nets.filter((r) => r.value === n).map((r) => ({ parentId: r.parentId, x: r.x, y: r.y }));
  const j7id = (des.find((r) => String(r.value).startsWith('J7')) || {}).parentId;
  let j7 = null;
  if (j7id) {
    try {
      const c = await eda.sch_PrimitiveComponent.get(j7id);
      j7 = { id: j7id, des: c.designator, name: c.name, x: c.x, y: c.y };
    } catch (e) {
      j7 = { id: j7id, err: String(e && e.message || e).slice(0, 120) };
    }
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
  };
})()
