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
        x: (p.getState_X && p.getState_X()) || (st && st.x),
        y: (p.getState_Y && p.getState_Y()) || (st && st.y),
      };
    });
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const r85 = await eda.sch_PrimitiveComponent.get('5cf017917b429da4');
  const source = await eda.sys_FileManager.getDocumentSource();
  const nets = parse(source).filter((r) => r.key === 'NET');
  const pick = (n) => nets.filter((r) => r.value === n).map((r) => ({ parentId: r.parentId, x: r.x, y: r.y }));
  return {
    proj: info.uuid,
    r85: { des: r85.designator, name: r85.name, x: r85.x, y: r85.y, pins: await pinsOf('5cf017917b429da4') },
    USB_5V_VALID: pick('USB_5V_VALID'),
    S3_VBUS: pick('S3_VBUS'),
    ESP_USB_VBUS_SENSE: pick('ESP_USB_VBUS_SENSE'),
    OUT2: pick('OUT2'),
  };
})()
