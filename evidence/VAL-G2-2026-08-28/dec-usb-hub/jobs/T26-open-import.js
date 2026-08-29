(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const ORACLE = 'dcd7e3cab2a24b9aa6e531d2b62e1b6f';
  const TARGET = '54d2a25bce4b44c3af878e8b91af3554';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (current && [LIVE, HUB, ORACLE].includes(current.uuid)) {
    return { stop: true, reason: 'FORBIDDEN_CURRENT', uuid: current.uuid };
  }
  const opened = await eda.dmt_Project.openProject(TARGET);
  await new Promise((r) => setTimeout(r, 2500));
  const after = await eda.dmt_Project.getCurrentProjectInfo();
  if (!after || after.uuid !== TARGET) {
    return { stop: true, reason: 'OPEN_FAILED', uuid: after && after.uuid, opened: !!opened };
  }
  if ([LIVE, HUB, ORACLE].includes(after.uuid)) return { stop: true, reason: 'FORBIDDEN' };
  const boards = after.data || [];
  const inventory = boards.map((b) => ({
    name: b.name || b.title,
    sch: b.schematic && (b.schematic.uuid || b.schematic.id),
    pages: ((b.schematic && b.schematic.page) || []).map((p) => ({
      uuid: p.uuid, name: p.name, title: p.title,
    })),
    pcb: b.pcb && (b.pcb.uuid || b.pcb.id),
  }));
  let docs = null;
  try {
    if (eda.dmt_Project.listDocuments) docs = await eda.dmt_Project.listDocuments(TARGET);
  } catch (e) {
    docs = { err: String(e && e.message || e).slice(0, 120) };
  }
  let pageInfo = null;
  try { pageInfo = await eda.dmt_Schematic.getCurrentSchematicAllSchematicPagesInfo(); }
  catch (e) { pageInfo = { err: String(e && e.message || e).slice(0, 120) }; }
  let srcLen = 0;
  let srcHash = null;
  try {
    const src = String(await eda.sys_FileManager.getDocumentSource() || '');
    srcLen = src.length;
    srcHash = src.length ? `${src.length}:${(await (async () => {
      let h = 0;
      for (let i = 0; i < src.length; i += 1) h = ((h << 5) - h + src.charCodeAt(i)) | 0;
      return (h >>> 0).toString(16);
    })())}` : 'empty';
  } catch (e) {
    srcLen = -1;
  }
  return {
    uuid: after.uuid,
    name: after.friendlyName,
    slug: after.name,
    inventory,
    pageInfo,
    srcLen,
    srcHash,
    startPage: !String(location.hash || '').includes(TARGET) || /start/i.test(document.title),
    hash: location.hash,
    title: document.title,
  };
})()
