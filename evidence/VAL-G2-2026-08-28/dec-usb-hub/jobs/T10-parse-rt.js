(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const source = await eda.sys_FileManager.getDocumentSource();
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
  const nets = recs.filter((r) => r.key === 'NET');
  const want = ['USB_DP_RT', 'USB_DN_RT', 'USB_DP_PROT', 'USB_DN_PROT', 'USB_DP_J1', 'USB_DN_J1'];
  const by = {};
  for (const n of want) {
    const rows = nets.filter((r) => r.value === n);
    by[n] = rows.map((r) => ({ id: r.id, parentId: r.parentId, type: r.type, x: r.x, y: r.y }));
  }
  const parents = [...new Set(Object.values(by).flat().map((r) => r.parentId).filter(Boolean))];
  const parentRecs = [];
  for (const pid of parents) {
    const r = recs.find((x) => x.id === pid);
    if (r) parentRecs.push({ id: r.id, type: r.type, x: r.x, y: r.y, x1: r.x1, y1: r.y1, points: r.points, line: r.line, net: r.net });
  }
  return {
    proj: info.uuid,
    recCount: recs.length,
    netCount: nets.length,
    by,
    parentRecs,
  };
})()
