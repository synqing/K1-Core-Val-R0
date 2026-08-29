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
  const near = nets.filter((r) => {
    const x = Number(r.x);
    const y = Math.abs(Number(r.y));
    return (Math.abs(x - 4175) <= 80 && Math.abs(y - 4340) <= 40)
      || (Math.abs(x - 1720) <= 80 && Math.abs(y - 1200) <= 40);
  });
  const pick = (n) => nets.filter((r) => r.value === n).map((r) => ({ parentId: r.parentId, x: r.x, y: r.y }));
  const nc = recs.filter((r) => r.key === 'NO_CONNECT' && Math.abs(Number(r.x) - 4175) <= 20 && Math.abs(Math.abs(Number(r.y)) - 4340) <= 15);
  return {
    proj: info.uuid,
    nearGpio15AndR85: near.map((r) => ({ net: r.value, parentId: r.parentId, x: r.x, y: r.y })),
    USB_5V_VALID: pick('USB_5V_VALID'),
    S3_USB_VBUS_VALID: pick('S3_USB_VBUS_VALID'),
    USB_DM_S3: pick('USB_DM_S3'),
    ESP_USB_VBUS_SENSE: pick('ESP_USB_VBUS_SENSE'),
    S3_VBUS: pick('S3_VBUS'),
    nc,
  };
})()
