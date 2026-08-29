(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const TARGET = '54d2a25bce4b44c3af878e8b91af3554';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== TARGET) return { stop: true, reason: 'NOT_IMPORT', uuid: current && current.uuid };
  if (current.uuid === LIVE) return { stop: true, reason: 'LIVE_FOCUSED' };
  const file = await eda.sys_FileManager.getProjectFileByProjectUuid(LIVE);
  const buf = await file.arrayBuffer();
  const bytes = new Uint8Array(buf);
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  const sha = [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, '0')).join('');
  let liveInfo = null;
  try {
    const info = await eda.dmt_Project.getProjectInfo(LIVE);
    liveInfo = { uuid: info.uuid, name: info.friendlyName };
  } catch (e) {
    liveInfo = { err: String(e && e.message || e).slice(0, 120) };
  }
  return {
    currentUuid: current.uuid,
    didNotFocusLive: current.uuid !== LIVE,
    didNotFocusHub: current.uuid !== HUB,
    live: liveInfo,
    epro2Bytes: bytes.length,
    epro2Sha256: sha,
    fileName: file && file.name,
  };
})()
