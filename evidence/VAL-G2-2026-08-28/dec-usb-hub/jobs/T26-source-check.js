(async () => {
  const eda = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda).eda;
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  const raw = await eda.sys_FileManager.getDocumentSource();
  const text = String(raw || '');
  return {
    uuid: current && current.uuid,
    friendlyName: current && current.friendlyName,
    srcLen: text.length,
    j1: text.includes('"J1"') || text.includes('J1'),
    u20: text.includes('U20'),
    j7: text.includes('J7'),
    head: text.slice(0, 160),
  };
})()
