(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const HUSK = 'f0f6cd233d69411ea478de1037da28fc';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const names = [];
  let cur = eda.dmt_Project;
  for (let d = 0; d < 4 && cur; d += 1) {
    names.push(...Object.getOwnPropertyNames(cur).filter((n) => typeof eda.dmt_Project[n] === 'function'));
    cur = Object.getPrototypeOf(cur);
  }
  const closeFns = [...new Set(names)].filter((n) => /close|leave|exit/i.test(n));
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== HUSK) {
    return { stop: true, reason: 'NOT_HUSK', uuid: current && current.uuid, closeFns };
  }
  if ([LIVE, HUB].includes(current.uuid)) return { stop: true, reason: 'FORBIDDEN' };
  const sigs = {};
  for (const fn of closeFns) sigs[fn] = String(eda.dmt_Project[fn]).slice(0, 120);
  let closed = null;
  const tryFns = ['closeProject', 'closeCurrentProject', 'leaveProject'];
  for (const fn of tryFns) {
    if (typeof eda.dmt_Project[fn] === 'function') {
      try {
        closed = { fn, result: await eda.dmt_Project[fn](HUSK) };
        break;
      } catch (e) {
        closed = { fn, err: String(e && e.message || e).slice(0, 160) };
      }
    }
  }
  await new Promise((r) => setTimeout(r, 1500));
  const after = await eda.dmt_Project.getCurrentProjectInfo();
  return {
    closeFns,
    sigs,
    closed,
    afterUuid: after && after.uuid,
    afterName: after && after.friendlyName,
  };
})()
