(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
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
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  const src = await eda.sys_FileManager.getDocumentSource();
  const recs = parse(src);
  const gnd = recs.filter((r) => r.key === 'NET' && r.value === 'GND');
  const tap = recs.filter((r) => r.key === 'NET' && (r.value === 'TAP_REF' || r.value === 'TAP_VBUS'));
  const oldGnd = recs.filter((r) => r.id === '0170749d64f794d2' || r.parentId === '0170749d64f794d2' || r.lineGroup === '0170749d64f794d2');
  const mega = recs.filter((r) => r.id === 'cc9e090de2555cfb' || r.parentId === 'cc9e090de2555cfb' || r.lineGroup === 'cc9e090de2555cfb');
  const gndParents = [...new Set(gnd.map((r) => r.parentId))];
  let megaState = null;
  try {
    const prim = await eda.sch_PrimitiveWire.get('cc9e090de2555cfb');
    megaState = prim && (prim.getState ? prim.getState() : prim);
    megaState = { net: megaState && megaState.net, id: megaState && megaState.primitiveId, lineLen: (megaState && megaState.line && megaState.line.length) || 0 };
  } catch (e) {
    megaState = { err: String(e && e.message || e).slice(0, 80) };
  }
  const proto = megaState && Object.getOwnPropertyNames(eda.sch_PrimitiveWire);
  let modifyKeys = [];
  try {
    const prim = await eda.sch_PrimitiveWire.get('cc9e090de2555cfb');
    modifyKeys = Object.keys(prim || {}).slice(0, 40);
  } catch (e) { /* ok */ }
  return {
    proj: info.uuid,
    gndNetCount: gnd.length,
    gndParents: gndParents.slice(0, 20),
    gndParentCount: gndParents.length,
    tap: tap.map((r) => ({ parentId: r.parentId, value: r.value, x: r.x, y: r.y })),
    oldGndCount: oldGnd.length,
    megaChildCount: mega.length,
    megaNets: mega.filter((r) => r.key === 'NET').map((r) => r.value),
    megaState,
    modifyKeys,
    proto,
  };
})()
