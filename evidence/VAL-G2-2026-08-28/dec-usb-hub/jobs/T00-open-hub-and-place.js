(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  if (!eda) return { stop: true, reason: 'NO_EXTAPI' };
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const TAB = PAGE + '@' + HUB;
  const CLAIMED = 'ea47c20de228fa3a';
  const LIB = '27700277ef7a49e48a0293bece6b2993';
  const DEV = '64a4890ac65a4002b950d8b07c8459df';

  function sourceHash(source) {
    let hash = 2166136261;
    for (let i = 0; i < source.length; i += 1) {
      hash ^= source.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return source.length + ':' + (hash >>> 0).toString(16).padStart(8, '0');
  }

  let info = await eda.dmt_Project.getCurrentProjectInfo();
  let proj = info && info.uuid;
  if (proj === LIVE) return { stop: true, reason: 'LIVE_FOCUSED', proj };
  if (proj !== HUB) {
    const opened = await eda.dmt_Project.openProject(HUB);
    await new Promise((r) => setTimeout(r, 2500));
    info = await eda.dmt_Project.getCurrentProjectInfo();
    proj = info && info.uuid;
    if (proj === LIVE) return { stop: true, reason: 'LIVE_AFTER_OPEN', proj, opened };
    if (proj !== HUB) return { stop: true, reason: 'OPEN_FAILED', proj, opened, friendly: info && info.friendlyName };
  }

  await eda.dmt_EditorControl.activateDocument(TAB);
  await new Promise((r) => setTimeout(r, 800));

  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const named = [];
  for (const id of ids || []) {
    try {
      const c = await eda.sch_PrimitiveComponent.get(id);
      const st = c && (c.getState ? c.getState() : c);
      const name = String((st && (st.name || st.deviceName)) || '');
      const des = String((st && st.designator) || '');
      if (name.includes('7005A') || name.includes('USB4105') || des.includes('J1-PWR1') || id === CLAIMED) {
        named.push({ id, name: name.slice(0, 80), designator: des.slice(0, 40), x: st && st.x, y: st && st.y });
      }
    } catch (e) { /* skip */ }
  }

  let placed = null;
  const already = named.some((n) => n.name.includes('7005A') || n.id === CLAIMED);
  if (!already) {
    placed = await eda.sch_PrimitiveComponent.create(
      { libraryUuid: LIB, uuid: DEV },
      185,
      -3480,
      undefined,
      0,
      false,
      true,
      false
    );
  }

  const saved = await eda.sch_Document.save();
  const source = await eda.sys_FileManager.getDocumentSource();
  const hash = typeof source === 'string' ? sourceHash(source) : null;
  const idsAfter = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();

  let newId = CLAIMED;
  if (placed) newId = placed.primitiveId || placed.id || placed.uuid || CLAIMED;
  else if (named.find((n) => n.name.includes('7005A'))) newId = named.find((n) => n.name.includes('7005A')).id;

  let pins = [];
  try {
    const pinObjs = await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(newId);
    pins = (pinObjs || []).map((p) => {
      const st = p && (p.getState ? p.getState() : p);
      return { n: st && (st.pinNumber || st.number), name: st && (st.pinName || st.name) };
    });
  } catch (e) {
    pins = [{ error: String(e && e.message || e) }];
  }

  return {
    proj,
    friendly: info && (info.friendlyName || info.name),
    already,
    placed: Boolean(placed),
    placedKeys: placed && Object.keys(placed),
    placedId: placed && (placed.primitiveId || placed.id || placed.uuid),
    saved,
    sourceHash: hash,
    sourceLooksLikeSymbol: typeof source === 'string' && source.includes('"docType":"SYMBOL"'),
    componentCount: (idsAfter || []).length,
    wireCount: (wires || []).length,
    named,
    newId,
    pinCount: pins.length,
    pins,
  };
})()
