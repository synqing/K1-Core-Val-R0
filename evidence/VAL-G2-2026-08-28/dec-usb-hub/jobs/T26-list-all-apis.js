(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  if (!sandbox) return { error: 'no sandbox' };
  const eda = sandbox.eda;
  const own = (obj) => {
    const names = [];
    let cur = obj;
    let depth = 0;
    while (cur && depth < 5) {
      names.push(...Object.getOwnPropertyNames(cur));
      cur = Object.getPrototypeOf(cur);
      depth += 1;
    }
    return [...new Set(names)].filter((n) => typeof obj[n] === 'function').sort();
  };
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  return {
    uuid: current && current.uuid,
    name: current && current.friendlyName,
    project: own(eda.dmt_Project || {}),
    fileManager: own(eda.sys_FileManager || {}),
    schematic: own(eda.dmt_Schematic || {}).filter((n) => /page|copy|import|create|open/i.test(n)),
    edaKeys: Object.keys(eda).filter((k) => /project|file|import|export|doc/i.test(k)).sort(),
  };
})()
