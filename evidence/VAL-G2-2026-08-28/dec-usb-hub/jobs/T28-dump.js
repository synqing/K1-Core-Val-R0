(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const ORACLE = 'dcd7e3cab2a24b9aa6e531d2b62e1b6f';
  const TARGET = '55ed9ee948734a0e903f37744b51f3b8';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== TARGET) return { stop: true, reason: 'NOT_HOLD', uuid: current && current.uuid };
  if ([LIVE, HUB, ORACLE].includes(current.uuid)) return { stop: true, reason: 'FORBIDDEN' };
  const raw = await eda.sys_FileManager.getDocumentSource();
  const source = String(raw || '');
  return {
    uuid: current.uuid,
    name: current.friendlyName,
    source,
    c1exact: source.includes('"C1-PWR1"'),
    rcc1s: source.includes('"RCC1S-PWR1"'),
  };
})()
