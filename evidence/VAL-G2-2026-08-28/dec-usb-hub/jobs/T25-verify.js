(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  function sourceHash(source) {
    let hash = 2166136261;
    for (let i = 0; i < source.length; i += 1) {
      hash ^= source.charCodeAt(i);
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
  function hasBar(line) {
    if (!Array.isArray(line)) return false;
    for (let i = 0; i + 3 < line.length; i += 2) {
      const x1 = line[i], y1 = line[i + 1], x2 = line[i + 2], y2 = line[i + 3];
      if (y1 === 1010 && y2 === 1010 && Math.min(x1, x2) <= 1460 && Math.max(x1, x2) >= 1580) return true;
    }
    return false;
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  try { await eda.sch_SelectControl.clearSelected(); } catch (e) { /* ok */ }
  const src = await eda.sys_FileManager.getDocumentSource();
  const recs = parse(src);
  const tap = { TAP_VBUS: [], TAP_REF: [] };
  for (const r of recs) {
    if (r && r.key === 'NET' && tap[r.value]) {
      if (!tap[r.value].includes(r.parentId)) tap[r.value].push(r.parentId);
    }
  }
  const wireIds = [...new Set([...tap.TAP_VBUS, ...tap.TAP_REF])];
  const wires = [];
  for (const id of wireIds) {
    const prim = await eda.sch_PrimitiveWire.get(id).catch(() => null);
    const st = prim && (prim.getState ? prim.getState() : prim);
    wires.push({ id, present: !!st, net: st && st.net, line: st && st.line, bar: hasBar(st && st.line) });
  }
  const watch = {
    U21: 'fb7c84f0a582bd9c',
    R85: '5cf017917b429da4',
    J6: 'e98163',
    U9: 'e8065',
    R85wire: '0df3701fe687193c',
  };
  const watched = {};
  for (const [name, id] of Object.entries(watch)) {
    if (name === 'R85wire') {
      const prim = await eda.sch_PrimitiveWire.get(id).catch(() => null);
      const st = prim && (prim.getState ? prim.getState() : prim);
      watched[name] = { id, present: !!st, net: st && st.net, line: st && st.line };
    } else {
      const prim = await eda.sch_PrimitiveComponent.get(id).catch(() => null);
      const st = prim && (prim.getState ? prim.getState() : prim);
      watched[name] = { id, present: !!st, des: st && (st.designator || st.name), x: st && st.x, y: st && st.y };
    }
  }
  const gpioNets = recs.filter((r) => r.key === 'NET' && (r.value === 'USB_5V_VALID' || r.value === 'S3_VBUS' || r.value === 'USB_DM_S3'))
    .map((r) => ({ parentId: r.parentId, value: r.value, x: r.x, y: r.y }));
  return {
    proj: info.uuid,
    hash: sourceHash(src),
    sourceLen: src.length,
    tap,
    shared: tap.TAP_VBUS.filter((id) => tap.TAP_REF.includes(id)),
    wires,
    stillBad: recs.some((r) => r.id === 'e34ae57efe3e3790' || r.parentId === 'e34ae57efe3e3790'),
    watched,
    gpioNets: gpioNets.slice(0, 20),
    census: {
      components: ((await eda.sch_PrimitiveComponent.getAllPrimitiveId()) || []).length,
      wires: ((await eda.sch_PrimitiveWire.getAllPrimitiveId()) || []).length,
    },
  };
})()
