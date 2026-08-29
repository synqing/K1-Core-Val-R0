(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  function parseRecords(src) {
    const recs = [];
    for (const line of src.split('\n')) {
      const parts = line.split('||');
      if (parts.length < 2) continue;
      try {
        const head = JSON.parse(parts[0]);
        const body = JSON.parse(parts[1]);
        recs.push({ ...head, ...body });
      } catch (e) { /* skip */ }
    }
    return recs;
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  const source = await eda.sys_FileManager.getDocumentSource();
  const recs = parseRecords(source);
  const nets = recs.filter((r) => r.key === 'NET');
  const parents = {};
  for (const net of ['5V_PROTECTED', '5V_USB', 'GND']) {
    parents[net] = [...new Set(nets.filter((r) => r.value === net).map((r) => r.parentId))];
  }
  const wires = recs.filter((r) => r.type === 'WIRE');
  const near = wires.filter((w) => {
    const pts = w.points || w.path || [];
    const xs = [];
    const ys = [];
    if (Array.isArray(pts) && pts.length && typeof pts[0] === 'object') {
      for (const p of pts) { xs.push(p.x); ys.push(p.y); }
    }
    const x = w.x, y = w.y, x1 = w.x1, y1 = w.y1, x2 = w.x2, y2 = w.y2;
    const allx = [x, x1, x2, ...xs].filter((n) => Number.isFinite(n));
    const ally = [y, y1, y2, ...ys].filter((n) => Number.isFinite(n));
    return allx.some((n) => n >= 1230 && n <= 1360) && ally.some((n) => n >= 1270 && n <= 1370);
  }).map((w) => ({ id: w.id, x: w.x, y: w.y, x1: w.x1, y1: w.y1, x2: w.x2, y2: w.y2, points: w.points, net: w.net }));
  const flags = recs.filter((r) => r.type === 'COMPONENT' && /5V_PROTECTED|Power|Ground/.test(JSON.stringify(r))).slice(0, 20);
  const c120flags = recs.filter((r) => r.type === 'COMPONENT' && r.x >= 1200 && r.x <= 1400 && r.y >= 1260 && r.y <= 1380)
    .map((r) => ({ id: r.id, x: r.x, y: r.y, designator: r.designator, name: r.name }));
  const flagNets = recs.filter((r) => r.key === 'NET' && (r.value === '5V_PROTECTED' || r.value === 'GND') && c120flags.some((f) => f.id === r.parentId));
  return {
    proj: info.uuid,
    parents,
    nearWires: near.slice(0, 30),
    nearCount: near.length,
    c120flags,
    flagNets,
  };
})()
