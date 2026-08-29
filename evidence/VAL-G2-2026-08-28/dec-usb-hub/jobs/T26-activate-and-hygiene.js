(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const G22 = 'f0f6cd233d69411ea478de1037da28fc';
  const PAGE = '1a0d4e1c8ed3fe8f';
  const KEEP_SCH = 'cffcdb562c1b48d1a5214cfc263b6c90';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== G22) return { stop: true, reason: 'NOT_G22', uuid: current && current.uuid };
  if ([LIVE, HUB].includes(current.uuid)) return { stop: true, reason: 'FORBIDDEN' };

  const opened = await eda.dmt_EditorControl.openDocument(PAGE);
  let activated = null;
  try {
    if (eda.dmt_EditorControl.activateDocument) {
      activated = await eda.dmt_EditorControl.activateDocument(PAGE + '@' + G22);
    }
  } catch (e) {
    activated = { err: String(e && e.message || e).slice(0, 120) };
  }
  await new Promise((r) => setTimeout(r, 1500));

  const schs = await eda.dmt_Schematic.getAllSchematicsInfo();
  const deleted = [];
  for (const s of schs || []) {
    if (s.uuid !== KEEP_SCH && s.parentProjectUuid === G22) {
      try {
        deleted.push({ uuid: s.uuid, name: s.name, result: await eda.dmt_Schematic.deleteSchematic(s.uuid) });
      } catch (e) {
        deleted.push({ uuid: s.uuid, err: String(e && e.message || e).slice(0, 120) });
      }
    }
  }

  let boards = null;
  try {
    if (eda.dmt_Board && eda.dmt_Board.getAllBoardsInfo) {
      boards = await eda.dmt_Board.getAllBoardsInfo();
    }
  } catch (e) {
    boards = { err: String(e && e.message || e).slice(0, 80) };
  }

  const after = await eda.dmt_Project.getCurrentProjectInfo();
  const pages = ((((after.data || [])[0] || {}).schematic || {}).page || []).map((p) => ({ uuid: p.uuid, name: p.name }));
  let src = null;
  try {
    const raw = await eda.sys_FileManager.getDocumentSource();
    src = { len: raw && String(raw).length, head: String(raw || '').slice(0, 120), j1: String(raw || '').includes('J1') };
  } catch (e) {
    src = { err: String(e && e.message || e).slice(0, 140) };
  }
  return {
    opened: opened == null ? null : typeof opened,
    activated,
    deleted,
    boards,
    pages,
    src,
    afterUuid: after && after.uuid,
  };
})()
