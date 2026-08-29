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
  const lines = recs.filter((r) => r && r.lineGroup);
  function segs(net) {
    const ids = [...new Set(nets.filter((r) => r.value === net).map((r) => r.parentId))];
    return lines.filter((r) => ids.includes(r.lineGroup)).map((r) => [r.startX, r.startY, r.endX, r.endY, r.lineGroup]);
  }
  return {
    proj: info.uuid,
    five: segs('5V_USB').filter((s) => Math.abs(s[0]) < 2000 && Math.abs(s[1]) < 2000),
    valid: segs('5V0_USB_VALID'),
    tap: segs('TAP_VBUS'),
    s3: segs('S3_USB_VBUS_VALID'),
    rt: segs('RT_USB_VBUS'),
    hits: {
      USB_OCS1_N: (source.match(/USB_OCS1_N/g) || []).length,
      USB_OCS2_N: (source.match(/USB_OCS2_N/g) || []).length,
    },
  };
})()
