(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  function sourceHash(source) {
    let hash = 2166136261;
    for (let i = 0; i < source.length; i += 1) {
      hash ^= source.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return source.length + ':' + (hash >>> 0).toString(16).padStart(8, '0');
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  const u20 = '92edd0bd8901c171';
  const pins = await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(u20);
  const pinRows = [];
  for (const pin of pins || []) {
    const n = pin.getState_PinNumber && pin.getState_PinNumber();
    const name = pin.getState_PinName && pin.getState_PinName();
    const x = pin.getState_X && pin.getState_X();
    const y = pin.getState_Y && pin.getState_Y();
    const keys = Object.keys(pin).filter((k) => /net|Net|wire|Wire/i.test(k)).slice(0, 20);
    pinRows.push({ n, name, x, y, keys });
  }
  const wireIds = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  const columnHits = [];
  const known = {};
  for (const id of ['fd3dd96d58a6e4c4', '7f42a9c09ffd80c9', '87fabd9d08a58a4e', '36ba2e457cce2b12', 'bea5bf207c6f4166', 'f030c09f4f3caf10']) {
    known[id] = (wireIds || []).includes(id);
  }
  for (const id of wireIds || []) {
    try {
      const w = await eda.sch_PrimitiveWire.get(id);
      const st = w && (w.getState ? w.getState() : w);
      const net = st && (st.net || (w.getState_Net && w.getState_Net()));
      const line = st && st.line;
      const segs = Array.isArray(line) ? line : [];
      let hitLeft = false;
      let hitRightUsb = false;
      for (const seg of segs) {
        const pts = Array.isArray(seg) ? seg : [];
        for (let i = 0; i + 3 < pts.length; i += 2) {
          const x1 = pts[i], y1 = pts[i + 1], x2 = pts[i + 2], y2 = pts[i + 3];
          const minX = Math.min(x1, x2), maxX = Math.max(x1, x2);
          const minY = Math.min(y1, y2), maxY = Math.max(y1, y2);
          if (minX <= 230 && maxX >= 230 && minY <= 850 && maxY >= 740) hitLeft = true;
          if (minX <= 570 && maxX >= 570 && minY <= 810 && maxY >= 800) hitRightUsb = true;
        }
      }
      if (hitLeft || hitRightUsb || net === '3V3' || (typeof net === 'string' && net.includes('USB'))) {
        columnHits.push({
          id,
          net,
          hitLeft,
          hitRightUsb,
          segs: segs.length,
          sample: segs.slice(0, 3),
        });
      }
    } catch (e) {
      columnHits.push({ id, err: String(e && e.message || e).slice(0, 120) });
    }
  }
  const source = await eda.sys_FileManager.getDocumentSource();
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  return {
    proj: info.uuid,
    sourceHash: sourceHash(source),
    components: (ids || []).length,
    wires: (wireIds || []).length,
    pinRows,
    known,
    columnHits,
  };
})()
