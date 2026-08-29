(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  if (!sandbox) return { error: 'no sandbox' };
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const ORACLE = 'dcd7e3cab2a24b9aa6e531d2b62e1b6f';
  const HUSK = 'f0f6cd233d69411ea478de1037da28fc';
  const NEW_NAME = 'K1-Core-Val-R0-G2.2-HUSK-ABANDONED';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== HUSK) {
    return { stop: true, reason: 'NOT_ON_HUSK', uuid: current && current.uuid };
  }
  if ([LIVE, HUB, ORACLE].includes(HUSK)) return { stop: true, reason: 'FORBIDDEN' };
  const sig = String(eda.dmt_Project.modifyProjectFriendlyName);
  let renamed = null;
  try {
    renamed = await eda.dmt_Project.modifyProjectFriendlyName(NEW_NAME);
  } catch (e1) {
    try {
      renamed = await eda.dmt_Project.modifyProjectFriendlyName(HUSK, NEW_NAME);
    } catch (e2) {
      try {
        renamed = await eda.dmt_Project.modifyProjectFriendlyName({ uuid: HUSK, friendlyName: NEW_NAME });
      } catch (e3) {
        renamed = {
          err1: String(e1 && e1.message || e1).slice(0, 160),
          err2: String(e2 && e2.message || e2).slice(0, 160),
          err3: String(e3 && e3.message || e3).slice(0, 160),
        };
      }
    }
  }
  await new Promise((r) => setTimeout(r, 800));
  const after = await eda.dmt_Project.getProjectInfo(HUSK);
  return {
    sig: sig.slice(0, 400),
    renamedType: renamed == null ? null : typeof renamed,
    renamedKeys: renamed && typeof renamed === 'object' ? Object.keys(renamed).slice(0, 20) : null,
    afterUuid: after && after.uuid,
    afterName: after && after.friendlyName,
    afterSlug: after && after.name,
  };
})()
