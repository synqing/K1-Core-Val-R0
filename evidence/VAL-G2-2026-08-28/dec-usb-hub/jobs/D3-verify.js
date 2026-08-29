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
  const byNet = {};
  for (const net of ['USB_OCS1_N', 'USB_OCS2_N', '5V_USB', '5V0_USB_VALID', 'TAP_VBUS', 'GND']) {
    byNet[net] = [...new Set(nets.filter((r) => r.value === net).map((r) => r.parentId))];
  }
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    components: ((await eda.sch_PrimitiveComponent.getAllPrimitiveId()) || []).length,
    wires: ((await eda.sch_PrimitiveWire.getAllPrimitiveId()) || []).length,
    byNet,
    hits: {
      '5V_USB': (source.match(/5V_USB/g) || []).length,
      DVBUS: (source.match(/DVBUS-PWR1/g) || []).length,
    },
  };
})()
