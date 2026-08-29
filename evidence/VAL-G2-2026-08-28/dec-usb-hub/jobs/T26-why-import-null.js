(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const ORACLE = 'dcd7e3cab2a24b9aa6e531d2b62e1b6f';
  const HUSK = 'f0f6cd233d69411ea478de1037da28fc';
  const NAME = 'K1-Core-Val-R0-G2.2-READABLE-CANDIDATE';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  const fm = Object.getOwnPropertyNames(eda.sys_FileManager || {}).sort();
  const proj = Object.getOwnPropertyNames(eda.dmt_Project || {}).filter((n) =>
    /delete|remove|list|search|find|project/i.test(n)
  );
  let huskInfo = null;
  try {
    huskInfo = await eda.dmt_Project.getProjectInfo(HUSK);
  } catch (e) {
    huskInfo = { err: String(e && e.message || e).slice(0, 160) };
  }
  let listed = null;
  const listFns = ['listProjects', 'getProjects', 'searchProjects', 'listTeamProjects'];
  for (const fn of listFns) {
    if (typeof eda.dmt_Project[fn] === 'function') {
      try {
        listed = { fn, result: await eda.dmt_Project[fn]() };
        break;
      } catch (e) {
        listed = { fn, err: String(e && e.message || e).slice(0, 160) };
      }
    }
  }
  const slimHusk = huskInfo && !huskInfo.err ? {
    uuid: huskInfo.uuid,
    friendlyName: huskInfo.friendlyName,
    name: huskInfo.name,
    pages: ((((huskInfo.data || [])[0] || {}).schematic || {}).page || []).length,
  } : huskInfo;
  return {
    currentUuid: current && current.uuid,
    currentName: current && current.friendlyName,
    husk: slimHusk,
    fileManager: fm,
    projectFns: proj.sort(),
    listedType: listed && listed.fn,
    listedErr: listed && listed.err,
    listedCount: listed && listed.result && (Array.isArray(listed.result) ? listed.result.length : typeof listed.result),
    forbidden: { isLive: current && current.uuid === LIVE, isHub: current && current.uuid === HUB, isOracle: current && current.uuid === ORACLE },
    name,
  };
})()
