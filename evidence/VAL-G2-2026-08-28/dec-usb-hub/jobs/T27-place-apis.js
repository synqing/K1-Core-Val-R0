(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const TARGET = '54d2a25bce4b44c3af878e8b91af3554';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== TARGET) return { stop: true, reason: 'NOT_IMPORT', uuid: current && current.uuid };
  if ([LIVE, HUB].includes(current.uuid)) return { stop: true, reason: 'FORBIDDEN' };
  const own = (obj) => {
    const names = [];
    let cur = obj;
    let depth = 0;
    while (cur && depth < 4) {
      names.push(...Object.getOwnPropertyNames(cur));
      cur = Object.getPrototypeOf(cur);
      depth += 1;
    }
    return [...new Set(names)].filter((n) => typeof obj[n] === 'function').sort();
  };
  return {
    uuid: current.uuid,
    schComp: own(eda.sch_Component || {}).filter((n) => /add|place|create/i.test(n)),
    schDoc: own(eda.sch_Document || {}).filter((n) => /add|place|comp/i.test(n)),
    keys: Object.keys(eda).filter((k) => /comp|sch_/i.test(k)),
  };
})()
