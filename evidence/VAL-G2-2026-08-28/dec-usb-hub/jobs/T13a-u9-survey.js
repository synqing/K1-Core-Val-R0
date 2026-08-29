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
  const u9 = recs.filter((r) => r.type === 'COMPONENT' && (String(r.designator || '').includes('U9') || r.id === 'e9'));
  const des = recs.filter((r) => r.key === 'Designator' && String(r.value || '').startsWith('U9'));
  const r73 = recs.filter((r) => r.key === 'Designator' && /R73|R74/.test(String(r.value || '')));
  let u9id = des[0] && des[0].parentId;
  const pins = u9id ? (await pinsOf(u9id)).filter((p) => ['8', '13', '14', '19', '20'].includes(p.n) || /IO15|IO19|IO20|USB/i.test(p.name)) : [];
  return {
    proj: info.uuid,
    u9des: des.map((r) => ({ parentId: r.parentId, value: r.value, x: r.x, y: r.y })),
    r73r74: r73.map((r) => ({ parentId: r.parentId, value: r.value, x: r.x, y: r.y })),
    pins,
  };
})()
