(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const TARGET = '54d2a25bce4b44c3af878e8b91af3554';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== TARGET) return { stop: true, reason: 'NOT_IMPORT', uuid: current && current.uuid };
  if ([LIVE, HUB].includes(current.uuid)) return { stop: true, reason: 'FORBIDDEN' };
  const raw = await eda.sys_FileManager.getDocumentSource();
  const source = String(raw || '');
  return {
    uuid: current.uuid,
    name: current.friendlyName,
    source,
    j1: source.includes('J1'),
    j6: source.includes('J6'),
    j7: source.includes('J7'),
    u20: source.includes('U20'),
    u25: source.includes('U25'),
  };
})()
