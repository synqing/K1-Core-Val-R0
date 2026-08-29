(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  await new Promise((r) => setTimeout(r, 8000));
  let comps = null;
  try {
    comps = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  } catch (e) {
    comps = { err: String(e && e.message || e).slice(0, 160) };
  }
  let srcLen = 0;
  try { srcLen = String(await eda.sys_FileManager.getDocumentSource() || '').length; }
  catch (e) { srcLen = -1; }
  return {
    componentCount: Array.isArray(comps) ? comps.length : comps,
    srcLen,
  };
})()
