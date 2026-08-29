(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const G22 = 'f0f6cd233d69411ea478de1037da28fc';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const ORACLE = 'dcd7e3cab2a24b9aa6e531d2b62e1b6f';
  function slim(info) {
    if (!info) return null;
    const board = (info.data && info.data[0]) || {};
    const sch = board.schematic || {};
    const pages = (sch.page || []).map((p) => ({ uuid: p.uuid, name: p.name }));
    return {
      uuid: info.uuid,
      friendlyName: info.friendlyName,
      name: info.name,
      schematicUuid: sch.uuid,
      schematicName: sch.name,
      pages,
      pageCount: pages.length,
      pcbUuid: board.pcb && board.pcb.uuid,
    };
  }
  let current = await eda.dmt_Project.getCurrentProjectInfo();
  if (current && current.uuid === LIVE) {
    return { stop: true, reason: 'LIVE_FOCUSED', uuid: current.uuid };
  }
  let opened = null;
  try {
    opened = await eda.dmt_Project.openProject(G22);
  } catch (e) {
    opened = { err: String(e && e.message || e).slice(0, 200) };
  }
  await new Promise((r) => setTimeout(r, 3000));
  current = await eda.dmt_Project.getCurrentProjectInfo();
  if (current && current.uuid === LIVE) {
    return { stop: true, reason: 'LIVE_AFTER_OPEN', uuid: current.uuid };
  }
  let full = null;
  try {
    full = await eda.dmt_Project.getProjectInfo(G22);
  } catch (e) {
    full = { err: String(e && e.message || e).slice(0, 200) };
  }
  let docs = null;
  try {
    if (eda.dmt_Project.listDocuments) docs = await eda.dmt_Project.listDocuments(G22);
    else if (eda.dmt_Project.getDocuments) docs = await eda.dmt_Project.getDocuments(G22);
  } catch (e) {
    docs = { err: String(e && e.message || e).slice(0, 120) };
  }
  const slimFull = slim(full && !full.err ? full : current);
  const pageUuid = slimFull && slimFull.pages && slimFull.pages[0] && slimFull.pages[0].uuid;
  let activated = null;
  if (pageUuid && current && current.uuid === G22) {
    const tab = pageUuid + '@' + G22;
    try {
      if (eda.dmt_EditorControl.openDocument) {
        const tabId = await eda.dmt_EditorControl.openDocument(pageUuid);
        activated = { openDocument: tabId };
      }
    } catch (e) {
      activated = { openErr: String(e && e.message || e).slice(0, 160) };
    }
    try {
      await eda.dmt_EditorControl.activateDocument(tab);
      activated = Object.assign(activated || {}, { activateDocument: tab });
    } catch (e) {
      activated = Object.assign(activated || {}, { activateErr: String(e && e.message || e).slice(0, 160) });
    }
  }
  await new Promise((r) => setTimeout(r, 1500));
  const after = await eda.dmt_Project.getCurrentProjectInfo();
  return {
    opened: opened && (opened.uuid || opened.err || typeof opened),
    current: slim(current),
    full: slimFull,
    docs,
    activated,
    after: slim(after),
    forbidden: {
      isLive: after && after.uuid === LIVE,
      isHub: after && after.uuid === HUB,
      isOracle: after && after.uuid === ORACLE,
    },
  };
})()
