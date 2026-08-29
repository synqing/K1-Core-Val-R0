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
  const ids = [
    'e103620', 'e103634',
    'e103612', 'e103618', 'e103626', 'e103632', 'e103640', 'e103670',
    'e103604', 'e103622', 'e103636',
    'e103608', 'e103624', 'e103638',
    'e103614', 'e103610',
  ];
  const deleted = [];
  for (const id of ids) {
    try {
      await eda.sch_PrimitiveWire.delete(id);
      deleted.push({ id, ok: true });
    } catch (e) {
      deleted.push({ id, ok: false, err: String(e && e.message || e).slice(0, 120) });
    }
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
    USB_CC1: pick('USB_CC1'),
    USB_CC2: pick('USB_CC2'),
    S3_VBUS: pick('S3_VBUS'),
    USB_DP: pick('USB_DP'),
    USB_DM: pick('USB_DM'),
    USB_DP_S3: pick('USB_DP_S3'),
    components: ((await eda.sch_PrimitiveComponent.getAllPrimitiveId()) || []).length,
    wires: ((await eda.sch_PrimitiveWire.getAllPrimitiveId()) || []).length,
  };
})()
