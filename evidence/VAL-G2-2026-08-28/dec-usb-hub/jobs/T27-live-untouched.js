(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const TARGET = '54d2a25bce4b44c3af878e8b91af3554';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  let live = null;
  try {
    const info = await eda.dmt_Project.getProjectInfo(LIVE);
    live = { uuid: info.uuid, name: info.friendlyName };
  } catch (e) {
    live = { err: String(e && e.message || e).slice(0, 120) };
  }
  return {
    currentUuid: current && current.uuid,
    currentName: current && current.friendlyName,
    didNotFocusLive: current && current.uuid !== LIVE,
    didNotFocusHub: current && current.uuid !== HUB,
    onImport: current && current.uuid === TARGET,
    live,
  };
})()
