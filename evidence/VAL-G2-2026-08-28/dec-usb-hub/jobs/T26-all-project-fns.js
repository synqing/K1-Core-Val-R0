(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const bags = {};
  for (const [key, obj] of Object.entries(eda)) {
    if (!obj || typeof obj !== 'object') continue;
    const names = [];
    let cur = obj;
    for (let d = 0; d < 4 && cur; d += 1) {
      try {
        names.push(...Object.getOwnPropertyNames(cur).filter((n) => typeof obj[n] === 'function'));
      } catch (e) {}
      cur = Object.getPrototypeOf(cur);
    }
    const hit = [...new Set(names)].filter((n) => /delete|remove|destroy|trash|archive/i.test(n));
    if (hit.length) bags[key] = hit.map((n) => n + ':' + String(obj[n]).slice(0, 100));
  }
  return bags;
})()
