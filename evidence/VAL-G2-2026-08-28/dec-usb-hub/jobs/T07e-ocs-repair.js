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
  function parse(src) {
    const recs = [];
    for (const chunk of src.split('|')) {
      const t = chunk.trim();
      if (!t) continue;
      try { recs.push(JSON.parse(t)); } catch (e) { /* skip */ }
    }
    return recs;
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  const source = await eda.sys_FileManager.getDocumentSource();
  const recs = parse(source);
  const nets = recs.filter((r) => r && r.key === 'NET');
  const ocs2Parents = [...new Set(nets.filter((r) => r.value === 'USB_OCS2_N').map((r) => r.parentId))];
  const ocs1Parents = [...new Set(nets.filter((r) => r.value === 'USB_OCS1_N').map((r) => r.parentId))];
  const fiveParents = [...new Set(nets.filter((r) => r.value === '5V_USB').map((r) => r.parentId))];
  const tapParents = [...new Set(nets.filter((r) => r.value === 'TAP_VBUS').map((r) => r.parentId))];
  const validParents = [...new Set(nets.filter((r) => r.value === '5V0_USB_VALID').map((r) => r.parentId))];
  const s3Parents = [...new Set(nets.filter((r) => r.value === 'S3_USB_VBUS_VALID').map((r) => r.parentId))];
  const lines = recs.filter((r) => r && r.lineGroup);
  const ocs2Lines = lines.filter((r) => ocs2Parents.includes(r.lineGroup)).map((r) => [r.startX, r.startY, r.endX, r.endY, r.lineGroup]);
  const wireIds = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  const deleted = [];
  const known = ['5dcc3c3eb557b5e8', '49b94488cc1ceb02', '362640b37920279b', '977f80ca81ce4d00', '7b6771e387d036b3'];
  for (const id of [...new Set([...ocs2Parents, ...known])]) {
    if (!(wireIds || []).includes(id) && !ocs2Parents.includes(id)) continue;
    try {
      await eda.sch_PrimitiveWire.delete(id);
      deleted.push({ id, ok: true });
    } catch (e) {
      deleted.push({ id, ok: false, err: String(e && e.message || e).slice(0, 120) });
    }
  }
  const restore5v = [
    [1535, 610, 1570, 610],
    [1570, 610, 1570, 590],
    [1570, 590, 1535, 590],
    [1570, 590, 1570, 560],
    [1570, 560, 1350, 560],
    [1350, 560, 470, 560],
    [1350, 560, 1350, 800],
    [1350, 800, 1380, 800],
    [1380, 800, 1400, 800],
    [1380, 800, 1380, 1200],
  ];
  const restoreTap = [
    [1460, 990, 1340, 990],
    [1340, 990, 1340, 1200],
    [1420, 1200, 1460, 1200],
  ];
  const created = [];
  for (const line of restore5v) {
    try {
      const w = await eda.sch_PrimitiveWire.create(line, '5V_USB');
      const st = w && (w.getState ? w.getState() : w);
      created.push({ net: '5V_USB', line, ok: true, id: st && st.primitiveId });
    } catch (e) {
      created.push({ net: '5V_USB', line, ok: false, err: String(e && e.message || e).slice(0, 120) });
    }
  }
  for (const line of restoreTap) {
    try {
      const w = await eda.sch_PrimitiveWire.create(line, 'TAP_VBUS');
      const st = w && (w.getState ? w.getState() : w);
      created.push({ net: 'TAP_VBUS', line, ok: true, id: st && st.primitiveId });
    } catch (e) {
      created.push({ net: 'TAP_VBUS', line, ok: false, err: String(e && e.message || e).slice(0, 120) });
    }
  }
  const flags = [];
  const flagJobs = [
    ['USB_OCS1_N', 200, 780],
    ['USB_OCS1_N', 1290, 810],
    ['USB_OCS2_N', 200, 740],
    ['USB_OCS2_N', 1290, 780],
  ];
  for (const [net, x, y] of flagJobs) {
    try {
      const f = await eda.sch_PrimitiveComponent.createNetFlag('Net', net, x, y);
      const st = f && (f.getState ? f.getState() : f);
      flags.push({ net, x, y, ok: true, id: st && st.primitiveId });
    } catch (e) {
      flags.push({ net, x, y, ok: false, err: String(e && e.message || e).slice(0, 120) });
    }
  }
  const stubs = [
    [230, 780, 200, 780, 'USB_OCS1_N'],
    [1260, 810, 1290, 810, 'USB_OCS1_N'],
    [230, 740, 200, 740, 'USB_OCS2_N'],
    [1260, 780, 1290, 780, 'USB_OCS2_N'],
  ];
  for (const [x1, y1, x2, y2, net] of stubs) {
    try {
      const w = await eda.sch_PrimitiveWire.create([x1, y1, x2, y2], net);
      const st = w && (w.getState ? w.getState() : w);
      created.push({ net, line: [x1, y1, x2, y2], ok: true, id: st && st.primitiveId });
    } catch (e) {
      created.push({ net, line: [x1, y1, x2, y2], ok: false, err: String(e && e.message || e).slice(0, 120) });
    }
  }
  await eda.sch_Document.save();
  const after = await eda.sys_FileManager.getDocumentSource();
  const hits = {};
  for (const net of ['USB_OCS1_N', 'USB_OCS2_N', '5V_USB', 'TAP_VBUS', '5V0_USB_VALID', 'S3_USB_VBUS_VALID', 'RT_USB_VBUS']) {
    let n = 0; let idx = 0;
    while ((idx = after.indexOf(net, idx)) !== -1) { n += 1; idx += net.length; }
    hits[net] = n;
  }
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(after),
    before: {
      ocs2Parents, ocs1Parents, fiveParents: fiveParents.length, tapParents: tapParents.length,
      validParents: validParents.length, s3Parents: s3Parents.length,
      ocs2LineCount: ocs2Lines.length, ocs2Lines: ocs2Lines.slice(0, 40),
    },
    deleted, created, flags, hits,
    components: ((await eda.sch_PrimitiveComponent.getAllPrimitiveId()) || []).length,
    wires: ((await eda.sch_PrimitiveWire.getAllPrimitiveId()) || []).length,
  };
})()
