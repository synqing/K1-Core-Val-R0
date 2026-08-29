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
  await eda.sch_Document.save();
  const source = await eda.sys_FileManager.getDocumentSource();
  const comps = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  const hits = {};
  for (const net of ['USB_PRTPWR1', 'USB_PRTPWR2', 'USB_EN1', 'USB_EN2', 'USB_OCS1_N', 'USB_OCS2_N', 'RT_USB_VBUS', 'S3_USB_VBUS_VALID']) {
    let n = 0;
    let idx = 0;
    while ((idx = source.indexOf(net, idx)) !== -1) {
      n += 1;
      idx += net.length;
    }
    hits[net] = n;
  }
  return {
    proj: info.uuid,
    friendly: info.friendlyName,
    saved: true,
    sourceHash: sourceHash(source),
    components: (comps || []).length,
    wires: (wires || []).length,
    hits,
  };
})()
