(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
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
  const source = await eda.sys_FileManager.getDocumentSource();
  const recs = parse(source);
  const nets = recs.filter((r) => r.key === 'NET');
  const names = [
    'S3_VBUS', 'USB_DP', 'USB_DM', 'USB_DP_ESD', 'USB_DM_ESD',
    'ESP_USB_VBUS_SENSE', 'USB_DP_S3', 'USB_DM_S3', 'USB_DP_DN2', 'USB_DM_DN2',
  ];
  const pick = (n) => nets.filter((r) => r.value === n).map((r) => ({
    parentId: r.parentId, id: r.id, x: r.x, y: r.y, type: r.type,
  }));
  const dvbus = recs.filter((r) => String(r.designator || r.name || '').includes('DVBUS'));
  return {
    proj: info.uuid,
    nets: Object.fromEntries(names.map((n) => [n, pick(n)])),
    dvbus: dvbus.map((r) => ({ id: r.id, designator: r.designator, name: r.name, x: r.x, y: r.y, type: r.type })),
    sourceHasDVBUS: source.includes('DVBUS-PWR1'),
  };
})()
