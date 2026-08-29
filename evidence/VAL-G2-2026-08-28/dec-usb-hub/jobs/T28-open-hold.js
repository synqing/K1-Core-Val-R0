(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const ORACLE = 'dcd7e3cab2a24b9aa6e531d2b62e1b6f';
  const SCAR = '54d2a25bce4b44c3af878e8b91af3554';
  const HUSK = 'f0f6cd233d69411ea478de1037da28fc';
  const TARGET = '55ed9ee948734a0e903f37744b51f3b8';
  const FORBIDDEN = [LIVE, HUB, ORACLE];
  function slim(info) {
    if (!info) return null;
    const boards = info.data || [];
    return {
      uuid: info.uuid,
      friendlyName: info.friendlyName,
      name: info.name,
      boards: boards.map((b) => ({
        name: b.name || b.title,
        sch: b.schematic && b.schematic.uuid,
        schName: b.schematic && b.schematic.name,
        pages: ((b.schematic && b.schematic.page) || []).map((p) => ({ uuid: p.uuid, name: p.name })),
        pcb: b.pcb && b.pcb.uuid,
      })),
    };
  }
  const before = await eda.dmt_Project.getCurrentProjectInfo();
  if (before && FORBIDDEN.includes(before.uuid)) {
    return { stop: true, reason: 'FORBIDDEN_CURRENT', uuid: before.uuid };
  }
  let opened = null;
  try { opened = await eda.dmt_Project.openProject(TARGET); }
  catch (e) { opened = { err: String(e && e.message || e).slice(0, 200) }; }
  await new Promise((r) => setTimeout(r, 4000));
  let current = await eda.dmt_Project.getCurrentProjectInfo();
  if (current && FORBIDDEN.includes(current.uuid)) {
    return { stop: true, reason: 'FORBIDDEN_AFTER_OPEN', uuid: current.uuid };
  }
  if (!current || current.uuid !== TARGET) {
    return { stop: true, reason: 'NOT_HOLD', uuid: current && current.uuid, before: slim(before), opened };
  }
  let full = null;
  try { full = await eda.dmt_Project.getProjectInfo(TARGET); }
  catch (e) { full = { err: String(e && e.message || e).slice(0, 200) }; }
  const inv = slim(full && !full.err ? full : current);
  const pageUuid = inv && inv.boards && inv.boards[0] && inv.boards[0].pages && inv.boards[0].pages[0] && inv.boards[0].pages[0].uuid;
  let activated = null;
  if (pageUuid) {
    try {
      const tabId = await eda.dmt_EditorControl.openDocument(pageUuid);
      activated = { openDocument: tabId == null ? null : typeof tabId };
    } catch (e) {
      activated = { openErr: String(e && e.message || e).slice(0, 160) };
    }
    try {
      await eda.dmt_EditorControl.activateDocument(pageUuid + '@' + TARGET);
      activated = Object.assign(activated || {}, { activateDocument: pageUuid + '@' + TARGET });
    } catch (e) {
      activated = Object.assign(activated || {}, { activateErr: String(e && e.message || e).slice(0, 160) });
    }
  }
  await new Promise((r) => setTimeout(r, 4000));
  const after = await eda.dmt_Project.getCurrentProjectInfo();
  let src = '';
  try { src = String(await eda.sys_FileManager.getDocumentSource() || ''); }
  catch (e) { src = ''; }
  return {
    beforeUuid: before && before.uuid,
    leftScar: before && before.uuid === SCAR,
    leftHusk: before && before.uuid === HUSK,
    openedType: opened && (opened.uuid || opened.err || typeof opened),
    current: slim(current),
    full: inv,
    pageUuid,
    activated,
    after: slim(after),
    srcLen: src.length,
    c1exact: src.includes('"C1-PWR1"'),
    rcc1s: src.includes('"RCC1S-PWR1"'),
    u20: src.includes('U20'),
    j1: src.includes('J1'),
    forbidden: {
      isLive: after && after.uuid === LIVE,
      isHub: after && after.uuid === HUB,
      isOracle: after && after.uuid === ORACLE,
      isScar: after && after.uuid === SCAR,
    },
    hash: location.hash,
    title: document.title,
  };
})()
