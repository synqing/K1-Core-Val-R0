(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
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
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  const ids = {
    U23: '125f3f5842b2d308',
    R81: '22c6a17a7dbbd174',
    R82: 'dac528b1bfdc76ab',
    R83: '252b7a11c6b4da53',
    R84: '6b258885a490d64b',
    R85: '5cf017917b429da4',
    U21: 'fb7c84f0a582bd9c',
    bad: 'e34ae57efe3e3790',
  };
  const comps = {};
  for (const [name, id] of Object.entries(ids)) {
    if (name === 'bad') continue;
    const prim = await eda.sch_PrimitiveComponent.get(id).catch(() => null);
    const st = prim && (prim.getState ? prim.getState() : prim);
    const pins = prim ? await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(id) : [];
    comps[name] = {
      id,
      present: !!st,
      des: st && (st.designator || st.name),
      x: st && st.x,
      y: st && st.y,
      pins: (pins || []).map((p) => {
        const ps = p.getState ? p.getState() : p;
        return {
          n: String((p.getState_PinNumber && p.getState_PinNumber()) || (ps && ps.pinNumber) || ''),
          name: String((p.getState_PinName && p.getState_PinName()) || (ps && ps.pinName) || ''),
          x: (p.getState_X && p.getState_X()) || (ps && ps.x),
          y: (p.getState_Y && p.getState_Y()) || (ps && ps.y),
        };
      }),
    };
  }
  const source = await eda.sys_FileManager.getDocumentSource();
  const recs = parse(source);
  const nets = recs.filter((r) => r.key === 'NET' && (r.value === 'TAP_VBUS' || r.value === 'TAP_REF'));
  const bad = recs.filter((r) => r.id === ids.bad || r.parentId === ids.bad);
  const wire = recs.find((r) => r.id === ids.bad);
  return {
    proj: info.uuid,
    comps,
    tapNets: nets.map((r) => ({ id: r.id, parentId: r.parentId, value: r.value, x: r.x, y: r.y })),
    badWire: wire ? { id: wire.id, type: wire.type, points: wire.points || wire.path || wire.line, keys: Object.keys(wire) } : null,
    badChildren: bad.map((r) => ({ id: r.id, type: r.type, key: r.key, value: r.value, x: r.x, y: r.y, points: r.points || r.path })),
  };
})()
