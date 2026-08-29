(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  if (!sandbox) return { error: 'no sandbox' };
  const eda = sandbox.eda;
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
  const fm = own(eda.sys_FileManager || {});
  const proj = own(eda.dmt_Project || {});
  return {
    fm: fm.filter((n) => /import|export|extract|convert|delete|project|file/i.test(n)),
    proj: proj.filter((n) => /delete|remove|open|list|import|export|info/i.test(n)),
    fmAllCount: fm.length,
    projAllCount: proj.length,
  };
})()
