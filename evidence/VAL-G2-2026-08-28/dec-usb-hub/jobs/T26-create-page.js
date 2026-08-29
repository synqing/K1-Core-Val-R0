(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const G22 = 'f0f6cd233d69411ea478de1037da28fc';
  const SCH = 'cffcdb562c1b48d1a5214cfc263b6c90';
  const HUB_PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== G22) return { stop: true, reason: 'NOT_G22', uuid: current && current.uuid };
  if ([LIVE, HUB].includes(current.uuid)) return { stop: true, reason: 'FORBIDDEN' };

  let allSch = null;
  try { allSch = await eda.dmt_Schematic.getAllSchematicsInfo(); }
  catch (e) { allSch = { err: String(e && e.message || e).slice(0, 160) }; }
  let allPages = null;
  try { allPages = await eda.dmt_Schematic.getAllSchematicPagesInfo(); }
  catch (e) { allPages = { err: String(e && e.message || e).slice(0, 160) }; }
  let schInfo = null;
  try { schInfo = await eda.dmt_Schematic.getSchematicInfo(SCH); }
  catch (e) { schInfo = { err: String(e && e.message || e).slice(0, 160) }; }

  let created = null;
  try {
    created = await eda.dmt_Schematic.createSchematicPage(SCH);
  } catch (e1) {
    try {
      created = await eda.dmt_Schematic.createSchematicPage({ schematicUuid: SCH, name: 'P1' });
    } catch (e2) {
      created = { err1: String(e1 && e1.message || e1).slice(0, 160), err2: String(e2 && e2.message || e2).slice(0, 160) };
    }
  }

  await new Promise((r) => setTimeout(r, 2000));
  let pagesAfter = null;
  try { pagesAfter = await eda.dmt_Schematic.getAllSchematicPagesInfo(); }
  catch (e) { pagesAfter = { err: String(e && e.message || e).slice(0, 120) }; }
  const after = await eda.dmt_Project.getCurrentProjectInfo();
  const pages = ((((after.data || [])[0] || {}).schematic || {}).page || []).map((p) => ({ uuid: p.uuid, name: p.name }));

  return {
    allSch,
    allPages,
    schInfo,
    created,
    pagesAfter,
    currentPages: pages,
    afterUuid: after && after.uuid,
  };
})()
