(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
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
  for (const net of ['USB_OCS1_N', 'USB_OCS2_N', '5V_USB', 'TAP_VBUS', '5V0_USB_VALID', 'S3_USB_VBUS_VALID', 'USB_5V_VALID', 'RT_USB_VBUS']) {
    byNet[net] = [...new Set(nets.filter((r) => r.value === net).map((r) => r.parentId))];
  }
  const lines = recs.filter((r) => r && r.lineGroup);
  const ocs2 = lines.filter((r) => byNet.USB_OCS2_N.includes(r.lineGroup)).map((r) => ({
    g: r.lineGroup, x1: r.startX, y1: r.startY, x2: r.endX, y2: r.endY,
  }));
  const ocs1 = lines.filter((r) => byNet.USB_OCS1_N.includes(r.lineGroup)).map((r) => ({
    g: r.lineGroup, x1: r.startX, y1: r.startY, x2: r.endX, y2: r.endY,
  }));
  return {
    proj: info.uuid,
    wireMethods: Object.keys(eda.sch_PrimitiveWire || {}),
    flagMethods: Object.keys(eda.sch_PrimitiveComponent || {}).filter((k) => /net|flag|label/i.test(k)),
    byNet,
    ocs1,
    ocs2,
    fiveCount: byNet['5V_USB'].length,
    tapCount: byNet.TAP_VBUS.length,
  };
})()
