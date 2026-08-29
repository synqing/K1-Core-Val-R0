(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (current && current.uuid === LIVE) return { stop: true, reason: 'LIVE_FOCUSED' };
  let info = null;
  try { info = await eda.dmt_Project.getProjectInfo(LIVE); }
  catch (e) { info = { err: String(e && e.message || e).slice(0, 160) }; }
  return {
    currentUuid: current && current.uuid,
    liveUuid: info && info.uuid,
    liveName: info && info.friendlyName,
    didNotFocusLive: current && current.uuid !== LIVE,
  };
})()
