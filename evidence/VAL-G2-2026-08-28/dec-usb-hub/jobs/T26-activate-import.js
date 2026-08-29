(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const TARGET = '54d2a25bce4b44c3af878e8b91af3554';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== TARGET) {
    return { stop: true, reason: 'NOT_IMPORT', uuid: current && current.uuid };
  }
  if ([LIVE, HUB].includes(current.uuid)) return { stop: true, reason: 'FORBIDDEN' };
  let opened = null;
  try { opened = await eda.dmt_EditorControl.openDocument(PAGE); }
  catch (e) { opened = { err: String(e && e.message || e).slice(0, 160) }; }
  if (eda.dmt_EditorControl.activateDocument) {
    try { await eda.dmt_EditorControl.activateDocument(PAGE + '@' + TARGET); }
    catch (e1) {
      try { await eda.dmt_EditorControl.activateDocument(PAGE); }
      catch (e2) { /* ignore */ }
    }
  }
  await new Promise((r) => setTimeout(r, 4000));
  let src = '';
  try { src = String(await eda.sys_FileManager.getDocumentSource() || ''); }
  catch (e) { src = ''; }
  const pcb = ((((current.data || [])[0] || {}).pcb) || {});
  return {
    uuid: current.uuid,
    name: current.friendlyName,
    opened: opened && (opened.uuid || opened.id || typeof opened),
    srcLen: src.length,
    j1: src.includes('J1'),
    j6: src.includes('J6'),
    j7: src.includes('J7'),
    u20: src.includes('U20'),
    u25: src.includes('U25'),
    hirose: src.includes('ea47c20') || src.includes('J1-PWR1'),
    kill: src.includes('KILL'),
    pageInSrc: src.includes(PAGE),
    hash: location.hash,
    title: document.title,
    pcbUuid: pcb.uuid || pcb.id,
  };
})()
