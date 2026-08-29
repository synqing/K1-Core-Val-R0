(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const TARGET = '54d2a25bce4b44c3af878e8b91af3554';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== TARGET) return { stop: true, uuid: current && current.uuid };
  if (current.uuid === LIVE) return { stop: true, reason: 'LIVE' };
  const src = String(await eda.sys_FileManager.getDocumentSource() || '');
  return {
    uuid: current.uuid,
    srcLen: src.length,
    c1exact: src.includes('"C1-PWR1"'),
    rcc1s: src.includes('"RCC1S-PWR1"'),
    u20: src.includes('U20-USB'),
    j1: src.includes('J1-PWR1'),
  };
})()
