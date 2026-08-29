(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const TARGET = '54d2a25bce4b44c3af878e8b91af3554';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== TARGET) return { stop: true, uuid: current && current.uuid };
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
  return {
    component: own(eda.sch_PrimitiveComponent || {}),
    attr: own(eda.sch_PrimitiveAttribute || {}).filter((n) => /set|mod|name|desig|add/i.test(n)),
    wire: own(eda.sch_PrimitiveWire || {}).filter((n) => /add|create|place/i.test(n)),
    net: own(eda.sch_Net || {}).filter((n) => /add|connect|flag/i.test(n)),
    createComp: String(eda.sch_PrimitiveComponent.createComponent || eda.sch_PrimitiveComponent.add || '').slice(0, 300),
  };
})()
