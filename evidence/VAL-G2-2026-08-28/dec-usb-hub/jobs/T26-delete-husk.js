(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  if (!sandbox) return { error: 'no sandbox' };
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const ORACLE = 'dcd7e3cab2a24b9aa6e531d2b62e1b6f';
  const HUSK = 'f0f6cd233d69411ea478de1037da28fc';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  const husk = await eda.dmt_Project.getProjectInfo(HUSK);
  const pages = ((((husk.data || [])[0] || {}).schematic || {}).page || []).length;
  const sig = String(eda.dmt_Project.deleteProject);
  if (!current || current.uuid !== HUSK) {
    return { stop: true, reason: 'NOT_ON_HUSK', current: current && current.uuid, pages, sig: sig.slice(0, 200) };
  }
  if (pages !== 0) {
    return { stop: true, reason: 'HUSK_HAS_PAGES', pages, sig: sig.slice(0, 200) };
  }
  if ([LIVE, HUB, ORACLE].includes(HUSK)) {
    return { stop: true, reason: 'FORBIDDEN' };
  }
  let deleted = null;
  try {
    deleted = await eda.dmt_Project.deleteProject(HUSK);
  } catch (e1) {
    try {
      deleted = await eda.dmt_Project.deleteProject({ uuid: HUSK });
    } catch (e2) {
      deleted = { err1: String(e1 && e1.message || e1).slice(0, 160), err2: String(e2 && e2.message || e2).slice(0, 160) };
    }
  }
  await new Promise((r) => setTimeout(r, 1500));
  let after = null;
  try {
    after = await eda.dmt_Project.getCurrentProjectInfo();
  } catch (e) {
    after = { err: String(e && e.message || e).slice(0, 120) };
  }
  return {
    deleted: deleted && (deleted.uuid || deleted.err1 || typeof deleted),
    afterUuid: after && after.uuid,
    afterName: after && after.friendlyName,
    sig: sig.slice(0, 240),
  };
})()
