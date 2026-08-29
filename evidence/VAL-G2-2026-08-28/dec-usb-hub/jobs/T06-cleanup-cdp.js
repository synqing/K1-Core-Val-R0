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
  const shorts = ['cb9b3ea684295582', 'b356e49afd7c50a9'];
  const deleted = [];
  for (const id of shorts) {
    try {
      await eda.sch_PrimitiveWire.delete(id);
      deleted.push({ id, ok: true });
    } catch (e) {
      deleted.push({ id, ok: false, err: String(e && e.message || e).slice(0, 120) });
    }
  }
  const flags = [];
  const flagJobs = [
    { tag: 'p14-gnd', kind: 'Ground', net: 'GND', x: 570, y: 750 },
    { tag: 'p13-3v3', kind: 'Power', net: '3V3', x: 570, y: 740 },
    { tag: 'p17-gnd', kind: 'Ground', net: 'GND', x: 570, y: 780 },
  ];
  for (const job of flagJobs) {
    if (!job.kind) continue;
    try {
      const p = await eda.sch_PrimitiveComponent.createNetFlag(job.kind, job.net, job.x, job.y);
      const st = p && (p.getState ? p.getState() : p);
      if (st && st.primitiveId) {
        try {
          await eda.sch_PrimitiveComponent.modify(st.primitiveId, { addIntoPcb: false });
        } catch (e) { /* ignore */ }
      }
      flags.push({ tag: job.tag, ok: true, id: st && st.primitiveId });
    } catch (e) {
      flags.push({ tag: job.tag, ok: false, err: String(e && e.message || e).slice(0, 120) });
    }
  }
  let labelApi = typeof (eda.sch_PrimitiveAttribute && eda.sch_PrimitiveAttribute.createNetLabel);
  const labels = [];
  if (eda.sch_PrimitiveAttribute && eda.sch_PrimitiveAttribute.createNetLabel) {
    const labJobs = [
      { net: 'USB_RBIAS', x: 600, y: 850 },
      { net: 'USB_CRFILT', x: 200, y: 760 },
      { net: 'USB_PLLFILT', x: 600, y: 840 },
      { net: 'USB_XTALIN', x: 600, y: 830 },
      { net: 'USB_XTALOUT', x: 600, y: 820 },
    ];
    for (const job of labJobs) {
      try {
        const p = await eda.sch_PrimitiveAttribute.createNetLabel(job.x, job.y, job.net);
        labels.push({ ok: true, net: job.net, id: p && (p.primitiveId || (p.getState && p.getState().primitiveId)) });
      } catch (e) {
        labels.push({ ok: false, net: job.net, err: String(e && e.message || e).slice(0, 120) });
      }
    }
  }
  await eda.sch_Document.save();
  const source = await eda.sys_FileManager.getDocumentSource();
  const comps = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  return {
    proj: info.uuid,
    deleted,
    flags,
    labelApi,
    labels,
    saved: true,
    sourceHash: sourceHash(source),
    components: (comps || []).length,
    wires: (wires || []).length,
  };
})()
