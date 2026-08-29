(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
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
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  try { await eda.sch_PrimitiveWire.delete('88f10d494c93e9f4'); } catch (e) { /* continue */ }
  let created = null;
  try {
    const w = await eda.sch_PrimitiveWire.create([4020, 4340, 4050, 4340], 'USB_DM_S3');
    const st = w && (w.getState ? w.getState() : w);
    created = { id: st && (st.primitiveId || st.id), line: st && st.line, net: st && st.net };
  } catch (e) {
    created = { err: String(e && e.message || e).slice(0, 160) };
  }
  await eda.sch_Document.save();
  const source = await eda.sys_FileManager.getDocumentSource();
  const nets = parse(source).filter((r) => r.key === 'NET');
  const pick = (n) => nets.filter((r) => r.value === n).map((r) => ({ parentId: r.parentId, x: r.x, y: r.y }));
  return {
    proj: info.uuid,
    created,
    USB_DM_S3: pick('USB_DM_S3'),
    USB_DM_DN2: pick('USB_DM_DN2'),
  };
})()
