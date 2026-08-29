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
  const comps = recs.filter((r) => r.type === 'COMPONENT' && r.x != null && Math.abs(Number(r.x) - 2230) <= 20 && Math.abs(Math.abs(Number(r.y)) - 4040) <= 40);
  const near = recs.filter((r) => r.x != null && Math.abs(Number(r.x) - 2230) <= 15 && Math.abs(Math.abs(Number(r.y)) - 4040) <= 20).slice(0, 40);
  const flags = recs.filter((r) => (r.key === 'Name' || r.key === 'NET' || r.key === 'Designator') && String(r.value || '').includes('RT_USB_VBUS'));
  return {
    proj: info.uuid,
    compsNearN6: comps,
    flags,
    nearN6Recs: near.map((r) => ({ type: r.type, id: r.id, parentId: r.parentId, key: r.key, value: r.value, x: r.x, y: r.y })),
  };
})()
