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
  async function addWire(line, net) {
    try {
      const w = await eda.sch_PrimitiveWire.create(line, net);
      const st = w && (w.getState ? w.getState() : w);
      return { ok: true, net, line, id: st && st.primitiveId };
    } catch (e) {
      return { ok: false, net, line, err: String(e && e.message || e).slice(0, 140) };
    }
  }
  async function addFlag(net, x, y) {
    try {
      const f = await eda.sch_PrimitiveComponent.createNetFlag('Net', net, x, y);
      const st = f && (f.getState ? f.getState() : f);
      return { ok: true, net, x, y, id: st && st.primitiveId };
    } catch (e) {
      return { ok: false, net, x, y, err: String(e && e.message || e).slice(0, 140) };
    }
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);

  const beforeSrc = await eda.sys_FileManager.getDocumentSource();
  const beforeRecs = parse(beforeSrc);
  const beforeNets = {};
  for (const r of beforeRecs) {
    if (r && r.key === 'NET') {
      beforeNets[r.value] = beforeNets[r.value] || [];
      if (!beforeNets[r.value].includes(r.parentId)) beforeNets[r.value].push(r.parentId);
    }
  }

  const deleteIds = ['d90715b579268a82', 'df38bef06ba6e5f2'];
  const deleted = [];
  for (const id of deleteIds) {
    try {
      await eda.sch_PrimitiveWire.delete(id);
      deleted.push({ id, ok: true });
    } catch (e) {
      deleted.push({ id, ok: false, err: String(e && e.message || e).slice(0, 140) });
    }
  }

  const created = [];
  const five = [
    [1535, 610, 1570, 610],
    [1570, 610, 1570, 560],
    [1570, 590, 1535, 590],
    [1570, 560, 1350, 560],
    [1350, 560, 470, 560],
    [470, 560, 470, 640],
    [470, 640, 420, 640],
    [420, 640, 420, 980],
    [470, 640, 260, 640],
    [260, 640, 260, 980],
    [260, 640, 240, 640],
    [1350, 560, 1350, 800],
    [1350, 800, 1400, 800],
    [1380, 800, 1380, 1200],
  ];
  const valid = [
    [1140, 800, 1080, 800],
    [1080, 800, 1080, 1000],
    [1080, 1000, 1100, 1000],
    [1465, 610, 1455, 610],
    [1455, 610, 1455, 780],
    [1455, 780, 1565, 780],
    [1565, 780, 1565, 800],
  ];
  const tap = [
    [1460, 990, 1460, 1200],
  ];
  for (const line of five) created.push(await addWire(line, '5V_USB'));
  for (const line of valid) created.push(await addWire(line, '5V0_USB_VALID'));
  for (const line of tap) created.push(await addWire(line, 'TAP_VBUS'));

  const flags = [];
  flags.push(await addFlag('USB_OCS1_N', 210, 780));
  flags.push(await addFlag('USB_OCS1_N', 1285, 810));
  flags.push(await addFlag('USB_OCS2_N', 210, 740));
  flags.push(await addFlag('USB_OCS2_N', 1285, 780));
  created.push(await addWire([230, 780, 210, 780], 'USB_OCS1_N'));
  created.push(await addWire([1260, 810, 1285, 810], 'USB_OCS1_N'));
  created.push(await addWire([230, 740, 210, 740], 'USB_OCS2_N'));
  created.push(await addWire([1260, 780, 1285, 780], 'USB_OCS2_N'));

  await eda.sch_Document.save();
  const after = await eda.sys_FileManager.getDocumentSource();
  const hits = {};
  for (const net of ['USB_OCS1_N', 'USB_OCS2_N', '5V_USB', 'TAP_VBUS', '5V0_USB_VALID', 'S3_USB_VBUS_VALID', 'USB_5V_VALID', 'RT_USB_VBUS', '3V3']) {
    let n = 0; let idx = 0;
    while ((idx = after.indexOf(net, idx)) !== -1) { n += 1; idx += net.length; }
    hits[net] = n;
  }
  const afterRecs = parse(after);
  const afterNets = {};
  for (const r of afterRecs) {
    if (r && r.key === 'NET') {
      afterNets[r.value] = afterNets[r.value] || [];
      if (!afterNets[r.value].includes(r.parentId)) afterNets[r.value].push(r.parentId);
    }
  }
  const shared = [];
  const map = {};
  for (const [net, ids] of Object.entries(afterNets)) {
    for (const id of ids) {
      map[id] = map[id] || [];
      map[id].push(net);
    }
  }
  for (const [id, names] of Object.entries(map)) {
    if (names.length > 1) shared.push({ id, names });
  }
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(after),
    deleted,
    created,
    flags,
    hits,
    beforeParents: {
      USB_OCS1_N: beforeNets.USB_OCS1_N,
      USB_OCS2_N: beforeNets.USB_OCS2_N,
      '5V0_USB_VALID': beforeNets['5V0_USB_VALID'],
      TAP_VBUS: beforeNets.TAP_VBUS,
    },
    afterParents: {
      USB_OCS1_N: afterNets.USB_OCS1_N,
      USB_OCS2_N: afterNets.USB_OCS2_N,
      '5V_USB': (afterNets['5V_USB'] || []).length,
      '5V0_USB_VALID': afterNets['5V0_USB_VALID'],
      TAP_VBUS: afterNets.TAP_VBUS,
    },
    shared,
    components: ((await eda.sch_PrimitiveComponent.getAllPrimitiveId()) || []).length,
    wires: ((await eda.sch_PrimitiveWire.getAllPrimitiveId()) || []).length,
  };
})()
