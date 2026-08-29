(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const ORACLE = 'dcd7e3cab2a24b9aa6e531d2b62e1b6f';
  const TARGET = '55ed9ee948734a0e903f37744b51f3b8';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== TARGET) {
    return { stop: true, reason: 'NOT_HOLD', uuid: current && current.uuid };
  }
  if ([LIVE, HUB, ORACLE].includes(current.uuid)) {
    return { stop: true, reason: 'FORBIDDEN', uuid: current.uuid };
  }
  const tries = {};
  for (const [fn, args] of [
    ['openDocument', [PAGE]],
    ['openDocument', [PAGE + '@' + TARGET]],
    ['activateDocument', [PAGE + '@' + TARGET]],
    ['activateDocument', [PAGE]],
  ]) {
    const key = fn + ':' + String(args[0]).slice(0, 20);
    try {
      if (eda.dmt_EditorControl[fn]) tries[key] = await eda.dmt_EditorControl[fn](...args);
      else tries[key] = 'missing';
    } catch (e) {
      tries[key] = { err: String(e && e.message || e).slice(0, 180) };
    }
  }
  await new Promise((r) => setTimeout(r, 5000));
  const after = await eda.dmt_Project.getCurrentProjectInfo();
  if (!after || after.uuid !== TARGET) {
    return { stop: true, reason: 'NOT_HOLD_AFTER', uuid: after && after.uuid, tries };
  }
  let src = '';
  try { src = String(await eda.sys_FileManager.getDocumentSource() || ''); }
  catch (e) { src = ''; }
  const pages = ((((after.data || [])[0] || {}).schematic || {}).page || []).map((p) => ({ uuid: p.uuid, name: p.name }));
  return {
    uuid: after.uuid,
    name: after.friendlyName,
    tries,
    pages,
    srcLen: src.length,
    c1exact: src.includes('"C1-PWR1"'),
    rcc1s: src.includes('"RCC1S-PWR1"'),
    u20: src.includes('U20'),
    j1: src.includes('J1'),
    hash: location.hash,
    title: document.title,
  };
})()
