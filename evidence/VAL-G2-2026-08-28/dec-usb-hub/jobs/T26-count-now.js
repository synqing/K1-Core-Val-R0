(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const TARGET = '54d2a25bce4b44c3af878e8b91af3554';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== TARGET) return { stop: true, uuid: current && current.uuid };
  let ids = null;
  try { ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId(); }
  catch (e) { ids = { err: String(e && e.message || e).slice(0, 200) }; }
  const src = String(await eda.sys_FileManager.getDocumentSource() || '');
  return {
    uuid: current.uuid,
    idCount: Array.isArray(ids) ? ids.length : ids,
    srcLen: src.length,
    u20: src.includes('U20'),
  };
})()
