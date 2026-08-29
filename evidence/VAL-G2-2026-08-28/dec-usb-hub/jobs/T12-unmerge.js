(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  function sourceHash(source) {
    let hash = 2166136261;
    for (let i = 0; i < source.length; i += 1) {
      hash ^= source.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
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
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);

  const deleted = [];
  try {
    await eda.sch_PrimitiveWire.delete('b9520eddf98cb22f');
    deleted.push({ id: 'b9520eddf98cb22f', ok: true });
  } catch (e) {
    deleted.push({ id: 'b9520eddf98cb22f', ok: false, err: String(e && e.message || e).slice(0, 160) });
  }

  let restored = null;
  try {
    const w = await eda.sch_PrimitiveWire.create([2250, 4040, 2250, 4060], 'FLEXSPI_D1');
    const st = w && (w.getState ? w.getState() : w);
    restored = { ok: true, id: st && (st.primitiveId || st.id), net: st && st.net, line: st && st.line };
  } catch (e) {
    restored = { ok: false, err: String(e && e.message || e).slice(0, 160) };
  }

  await eda.sch_Document.save();
  const source = await eda.sys_FileManager.getDocumentSource();
  const nets = parse(source).filter((r) => r.key === 'NET');
  const pick = (n) => nets.filter((r) => r.value === n).map((r) => ({ parentId: r.parentId, x: r.x, y: r.y }));
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    deleted,
    restored,
    RT_USB_VBUS: pick('RT_USB_VBUS'),
    FLEXSPI_D1: pick('FLEXSPI_D1'),
    sharedOnVbus: pick('RT_USB_VBUS').map((r) => r.parentId).filter((id, i, a) => a.indexOf(id) === i),
  };
})()
