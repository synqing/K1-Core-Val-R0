(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const TARGET = '54d2a25bce4b44c3af878e8b91af3554';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const tab = PAGE + '@' + TARGET;
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== TARGET) return { stop: true, reason: 'NOT_IMPORT', uuid: current && current.uuid };
  if ([LIVE, HUB].includes(current.uuid)) return { stop: true, reason: 'FORBIDDEN' };
  const before = String(await eda.sys_FileManager.getDocumentSource() || '');
  const closed = await eda.dmt_EditorControl.closeDocument(tab);
  await new Promise((r) => setTimeout(r, 2000));
  let mid = await eda.dmt_Project.getCurrentProjectInfo();
  if (mid && [LIVE, HUB].includes(mid.uuid)) return { stop: true, reason: 'FORBIDDEN_MID', uuid: mid.uuid };
  const opened = await eda.dmt_Project.openProject(TARGET);
  await new Promise((r) => setTimeout(r, 2500));
  const openedDoc = await eda.dmt_EditorControl.openDocument(PAGE);
  await new Promise((r) => setTimeout(r, 4000));
  const after = await eda.dmt_Project.getCurrentProjectInfo();
  if (!after || after.uuid !== TARGET) return { stop: true, reason: 'NOT_IMPORT_AFTER', uuid: after && after.uuid };
  if ([LIVE, HUB].includes(after.uuid)) return { stop: true, reason: 'FORBIDDEN_AFTER' };
  const text = String(await eda.sys_FileManager.getDocumentSource() || '');
  const pages = ((((after.data || [])[0] || {}).schematic || {}).page || []).map((p) => ({ uuid: p.uuid, name: p.name }));
  return {
    closed: closed == null ? null : typeof closed,
    openedType: opened == null ? 'null' : typeof opened,
    openedDoc: openedDoc == null ? null : typeof openedDoc,
    afterUuid: after.uuid,
    afterName: after.friendlyName,
    pages,
    beforeLen: before.length,
    afterLen: text.length,
    hashStable: before.length === text.length,
    j1: text.includes('J1-PWR1'),
    j6: text.includes('J6-ESP'),
    j7: text.includes('J7'),
    u20: text.includes('U20'),
    u25: text.includes('U25'),
  };
})()
