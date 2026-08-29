(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
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

  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const proj = info && info.uuid;
  if (proj === LIVE) return { stop: true, reason: 'LIVE_FOCUSED', proj, friendly: info && info.friendlyName };
  if (proj !== HUB) return { stop: true, reason: 'WRONG_PROJECT', proj, friendly: info && info.friendlyName };

  await eda.dmt_EditorControl.activateDocument(TAB);
  await new Promise((r) => setTimeout(r, 400));

  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  let existing = null;
  try {
    existing = await eda.sch_PrimitiveComponent.get(CLAIMED);
  } catch (e) {
    existing = { error: String(e && e.message || e) };
  }

  let named = [];
  for (const id of ids || []) {
    try {
      const c = await eda.sch_PrimitiveComponent.get(id);
      const st = c && (c.getState ? c.getState() : c);
      const name = (st && (st.name || st.deviceName || (st.attrs && st.attrs.Name))) || '';
      const des = (st && (st.designator || (st.attrs && st.attrs.Designator))) || '';
      if (String(name).includes('7005A') || String(name).includes('USB4105') || String(des).includes('J1-PWR1') || id === CLAIMED) {
        named.push({
          id,
          name: String(name).slice(0, 80),
          designator: String(des).slice(0, 40),
          x: st && st.x,
          y: st && st.y,
        });
      }
    } catch (e) {
      /* skip */
    }
  }

  let placed = null;
  const already = named.some((n) => String(n.name).includes('7005A') || n.id === CLAIMED);
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
  if (placed) {
    newId = (placed && (placed.primitiveId || placed.id || placed.uuid)) || CLAIMED;
  } else if (named.find((n) => String(n.name).includes('7005A'))) {
    newId = named.find((n) => String(n.name).includes('7005A')).id;
  }

  let pins = [];
  try {
    const pinObjs = await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(newId);
    pins = (pinObjs || []).map((p) => {
      const st = p && (p.getState ? p.getState() : p);
      return {
        n: st && (st.pinNumber || st.number),
        name: st && (st.pinName || st.name),
      };
    });
  } catch (e) {
    pins = [{ error: String(e && e.message || e) }];
  }

  return {
    proj,
    friendly: info && (info.friendlyName || info.name),
    tab: TAB,
    already,
    placed: Boolean(placed),
    placedId: placed && (placed.primitiveId || placed.id || placed.uuid || Object.keys(placed)),
    saved,
    sourceHash: hash,
    sourceLen: typeof source === 'string' ? source.length : null,
    componentCount: (idsAfter || []).length,
    wireCount: (wires || []).length,
    named,
    newId,
    pinCount: pins.length,
    pins,
    existingClaimed: existing && (existing.primitiveId || existing.id || existing.error || Boolean(existing)),
  };
})()
