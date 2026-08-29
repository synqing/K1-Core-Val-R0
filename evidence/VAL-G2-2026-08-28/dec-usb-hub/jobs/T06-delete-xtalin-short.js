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
  const kill = ['fac587965c1a2f0d'];
  const deleted = [];
  for (const id of kill) {
    try {
      await eda.sch_PrimitiveWire.delete(id);
      deleted.push({ id, ok: true });
    } catch (e) {
      deleted.push({ id, ok: false, err: String(e && e.message || e).slice(0, 120) });
    }
  }
  const labels = [];
  const labJobs = [
    { net: 'USB_RBIAS', x: 570, y: 850 },
    { net: 'USB_CRFILT', x: 230, y: 760 },
    { net: 'USB_PLLFILT', x: 570, y: 840 },
    { net: 'USB_XTALIN', x: 570, y: 830 },
    { net: 'USB_XTALOUT', x: 570, y: 820 },
  ];
  for (const job of labJobs) {
    try {
      await eda.sch_PrimitiveAttribute.createNetLabel(job.x, job.y, job.net);
      labels.push({ ok: true, net: job.net });
    } catch (e) {
      labels.push({ ok: false, net: job.net, err: String(e && e.message || e).slice(0, 120) });
    }
  }
  await eda.sch_Document.save();
  const source = await eda.sys_FileManager.getDocumentSource();
  const comps = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  return {
    proj: info.uuid,
    deleted,
    labels,
    saved: true,
    sourceHash: sourceHash(source),
    components: (comps || []).length,
    wires: (wires || []).length,
  };
})()
