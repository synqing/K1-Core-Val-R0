(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const G22 = 'f0f6cd233d69411ea478de1037da28fc';
  const PAGE = '1a0d4e1c8ed3fe8f';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const tab = PAGE + '@' + G22;
  const before = await eda.sys_FileManager.getDocumentSource();
  const beforeLen = String(before || '').length;
  const closed = await eda.dmt_EditorControl.closeDocument(tab);
  await new Promise((r) => setTimeout(r, 1500));
  let mid = await eda.dmt_Project.getCurrentProjectInfo();
  if (mid && [LIVE, HUB].includes(mid.uuid)) return { stop: true, reason: 'FORBIDDEN_MID', uuid: mid.uuid };
  const opened = await eda.dmt_Project.openProject(G22);
  await new Promise((r) => setTimeout(r, 2500));
  const openedDoc = await eda.dmt_EditorControl.openDocument(PAGE);
  await new Promise((r) => setTimeout(r, 2000));
  const after = await eda.dmt_Project.getCurrentProjectInfo();
  if (!after || after.uuid !== G22) return { stop: true, reason: 'NOT_G22_AFTER', uuid: after && after.uuid };
  const raw = await eda.sys_FileManager.getDocumentSource();
  const text = String(raw || '');
  const pages = ((((after.data || [])[0] || {}).schematic || {}).page || []).map((p) => ({ uuid: p.uuid, name: p.name }));
  return {
    closed,
    openedType: opened == null ? 'null' : typeof opened,
    openedDoc: openedDoc == null ? null : typeof openedDoc,
    afterUuid: after.uuid,
    afterName: after.friendlyName,
    pages,
    beforeLen,
    afterLen: text.length,
    hashStable: beforeLen === text.length,
    j1: text.includes('J1'),
    j6: text.includes('J6-ESP'),
    j7: text.includes('J7'),
    u20: text.includes('U20'),
  };
})()
