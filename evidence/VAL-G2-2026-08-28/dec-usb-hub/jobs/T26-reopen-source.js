(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const G22 = 'f0f6cd233d69411ea478de1037da28fc';
  const PAGE = '1a0d4e1c8ed3fe8f';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== G22) return { stop: true, uuid: current && current.uuid };
  await eda.dmt_EditorControl.openDocument(PAGE);
  await new Promise((r) => setTimeout(r, 4000));
  let src = '';
  try { src = String(await eda.sys_FileManager.getDocumentSource() || ''); }
  catch (e) { return { err: String(e && e.message || e).slice(0, 160) }; }
  const pages = ((((current.data || [])[0] || {}).schematic || {}).page || []).map((p) => p.uuid);
  return {
    uuid: current.uuid,
    pages,
    srcLen: src.length,
    j1: src.includes('J1'),
    j6: src.includes('J6-ESP'),
    head: src.slice(0, 140),
  };
})()
