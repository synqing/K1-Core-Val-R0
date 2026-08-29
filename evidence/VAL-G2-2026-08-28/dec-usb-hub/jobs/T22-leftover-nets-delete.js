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
  const keepWires = new Set([
    '7a41eaf8f1832502', '916a2e5ac5bc3661', 'e103596',
    '41b3a32b40b5413b', '2b96fee724a60013', '68b99321ffb6afa2', '26c4ec3c99fc600f',
    '068877a397342e5e', '955e9ad023078e73', '946b8900cff89c09',
  ]);
  const deleteWires = [
    'e103678', 'e103682',
    'e103672', 'e103674',
    'e103650', 'e103680',
    'e103654', 'e103684',
  ];
  const wireDeletes = [];
  for (const id of deleteWires) {
    if (keepWires.has(id)) {
      wireDeletes.push({ id, ok: false, err: 'KEEP_GUARD' });
      continue;
    }
    try {
      await eda.sch_PrimitiveWire.delete(id);
      wireDeletes.push({ id, ok: true });
    } catch (e) {
      wireDeletes.push({ id, ok: false, err: String(e && e.message || e).slice(0, 120) });
    }
  }
  const dvbus = await eda.sch_PrimitiveComponent.get('ebrc000253').catch(() => null);
  const dvbusSt = dvbus && (dvbus.getState ? dvbus.getState() : dvbus);
  const dvbusName = dvbusSt ? String(dvbusSt.designator || dvbusSt.name || '') : '';
  let dvbusDeleted = false;
  if (dvbusSt && dvbusName.includes('DVBUS')) {
    await eda.sch_PrimitiveComponent.delete('ebrc000253');
    dvbusDeleted = true;
  }
  await eda.sch_Document.save();
  const source = await eda.sys_FileManager.getDocumentSource();
  const nets = parse(source).filter((r) => r.key === 'NET');
  const pick = (n) => nets.filter((r) => r.value === n).map((r) => r.parentId);
  let comps = 0;
  let wires = 0;
  for (const chunk of source.split('\n')) {
    if (chunk.includes('"type":"COMPONENT"')) comps += 1;
    if (chunk.includes('"type":"WIRE"')) wires += 1;
  }
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    wireDeletes,
    dvbusName,
    dvbusDeleted,
    sourceHasDVBUS: source.includes('DVBUS-PWR1'),
    S3_VBUS: pick('S3_VBUS'),
    USB_DP: pick('USB_DP'),
    USB_DM: pick('USB_DM'),
    USB_DP_ESD: pick('USB_DP_ESD'),
    USB_DM_ESD: pick('USB_DM_ESD'),
    ESP_USB_VBUS_SENSE: pick('ESP_USB_VBUS_SENSE'),
    USB_DP_S3: pick('USB_DP_S3'),
    USB_DM_S3: pick('USB_DM_S3'),
    comps,
    wires,
  };
})()
