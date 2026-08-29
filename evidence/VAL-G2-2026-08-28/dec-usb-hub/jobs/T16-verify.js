(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
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
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  await eda.sch_Document.save();
  const source = await eda.sys_FileManager.getDocumentSource();
  const nets = parse(source).filter((r) => r.key === 'NET');
  const pick = (n) => nets.filter((r) => r.value === n).map((r) => ({ parentId: r.parentId, x: r.x, y: r.y }));
  const valid = pick('USB_5V_VALID');
  const dm = pick('USB_DM_S3');
  const gpio15OnDm = dm.some((r) => Math.abs(Number(r.x) - 4175) <= 20 && Math.abs(Math.abs(Number(r.y)) - 4340) <= 8);
  const gpio15OnValid = valid.some((r) => Math.abs(Number(r.x) - 4175) <= 40 && Math.abs(Math.abs(Number(r.y)) - 4340) <= 8);
  const gpio15OnS3 = pick('S3_VBUS').some((r) => Math.abs(Number(r.x) - 4175) <= 40);
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    components: ((await eda.sch_PrimitiveComponent.getAllPrimitiveId()) || []).length,
    wires: ((await eda.sch_PrimitiveWire.getAllPrimitiveId()) || []).length,
    USB_5V_VALID: valid,
    S3_USB_VBUS_VALID: pick('S3_USB_VBUS_VALID'),
    S3_VBUS: pick('S3_VBUS'),
    USB_DM_S3: dm,
    gpio15OnValid,
    gpio15OnDm,
    gpio15OnS3,
  };
})()
