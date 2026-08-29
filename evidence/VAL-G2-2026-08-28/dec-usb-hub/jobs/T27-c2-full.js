(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const TARGET = '54d2a25bce4b44c3af878e8b91af3554';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== TARGET) return { stop: true, uuid: current && current.uuid };
  const c2 = await eda.sch_PrimitiveComponent.get('e108');
  const slim = {};
  for (const k of Object.keys(c2)) {
    const v = c2[k];
    if (v == null || typeof v === 'string' || typeof v === 'number' || typeof v === 'boolean') slim[k] = v;
    else if (typeof v === 'object') slim[k] = Object.keys(v).slice(0, 12);
  }
  return {
    slim,
    createLen: eda.sch_PrimitiveComponent.create.length,
    faHint: String(eda.sch_PrimitiveComponent.create),
  };
})()
