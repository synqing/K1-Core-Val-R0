(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const TARGET = '54d2a25bce4b44c3af878e8b91af3554';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current) return { stop: true, reason: 'NO_PROJECT' };
  if (current.uuid === LIVE) return { stop: true, reason: 'LIVE_FOCUSED' };
  if (current.uuid === HUB) return { stop: true, reason: 'HUB_FOCUSED' };
  if (current.uuid !== TARGET) {
    const opened = await eda.dmt_Project.openProject(TARGET);
    await new Promise((r) => setTimeout(r, 2000));
  }
  const after = await eda.dmt_Project.getCurrentProjectInfo();
  if (!after || after.uuid !== TARGET) return { stop: true, reason: 'OPEN_FAILED', uuid: after && after.uuid };
  if ([LIVE, HUB].includes(after.uuid)) return { stop: true, reason: 'FORBIDDEN' };
  try { await eda.dmt_EditorControl.openDocument(PAGE); } catch (e) { /* continue */ }
  await new Promise((r) => setTimeout(r, 2500));
  const pages = ((((after.data || [])[0] || {}).schematic || {}).page || []).map((p) => p.uuid);
  const src = String(await eda.sys_FileManager.getDocumentSource() || '');
  return {
    uuid: after.uuid,
    name: after.friendlyName,
    pages,
    pageOpen: pages.includes(PAGE),
    srcLen: src.length,
    c1: src.includes('C1-PWR1'),
    rcc1s: src.includes('RCC1S-PWR1'),
    j1: src.includes('J1-PWR1'),
    u20: src.includes('U20-USB'),
    title: document.title,
    hash: location.hash,
    startPageOnly: /start page/i.test(document.title) && !String(location.hash || '').includes(PAGE),
  };
})()
