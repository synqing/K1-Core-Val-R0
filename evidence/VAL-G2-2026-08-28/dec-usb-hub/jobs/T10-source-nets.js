(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const source = await eda.sys_FileManager.getDocumentSource();
  const names = ['USB_DP_RT', 'USB_DN_RT', 'USB_DP_PROT', 'USB_DN_PROT', 'USB_DP_UP', 'USB_DM_UP', 'USB_DP_J1', 'USB_DN_J1'];
  const counts = {};
  for (const n of names) counts[n] = (source.match(new RegExp(n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length;
  const hits = {};
  for (const n of names) {
    const i = source.indexOf('"' + n + '"');
    const j = source.indexOf(n);
    hits[n] = {
      quoted: i,
      around: i >= 0 ? source.slice(i - 120, i + 80) : (j >= 0 ? source.slice(j - 80, j + 80) : null),
    };
  }
  return {
    proj: info.uuid,
    len: source.length,
    nl: (source.match(/\n/g) || []).length,
    sample: source.slice(0, 200),
    counts,
    hits,
  };
})()
