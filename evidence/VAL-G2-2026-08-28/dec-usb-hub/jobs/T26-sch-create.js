(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const names = [];
  let cur = eda.dmt_Schematic;
  for (let d = 0; d < 4 && cur; d += 1) {
    names.push(...Object.getOwnPropertyNames(cur).filter((n) => typeof eda.dmt_Schematic[n] === 'function'));
    cur = Object.getPrototypeOf(cur);
  }
  const uniq = [...new Set(names)].sort();
  const sigs = {};
  for (const n of uniq) sigs[n] = String(eda.dmt_Schematic[n]).slice(0, 180);
  return sigs;
})()
