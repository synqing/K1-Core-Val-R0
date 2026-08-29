(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const G22 = 'f0f6cd233d69411ea478de1037da28fc';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const SCH = 'cffcdb562c1b48d1a5214cfc263b6c90';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== G22) return { stop: true, reason: 'NOT_G22', uuid: current && current.uuid };
  if (current.uuid === LIVE) return { stop: true, reason: 'LIVE' };
  const tries = {};
  for (const [fn, args] of [
    ['openDocument', [PAGE]],
    ['openDocument', [PAGE + '@' + G22]],
    ['activateDocument', [PAGE + '@' + G22]],
    ['openDocument', [SCH]],
  ]) {
    const key = fn + ':' + args[0].slice(0, 12);
    try {
      if (eda.dmt_EditorControl[fn]) {
        tries[key] = await eda.dmt_EditorControl[fn](...args);
      } else {
        tries[key] = 'missing';
      }
    } catch (e) {
      tries[key] = { err: String(e && e.message || e).slice(0, 180) };
    }
  }
  await new Promise((r) => setTimeout(r, 2500));
  const after = await eda.dmt_Project.getCurrentProjectInfo();
  const pages = ((((after.data || [])[0] || {}).schematic || {}).page || []).map((p) => ({ uuid: p.uuid, name: p.name }));
  let src = null;
  try {
    const raw = await eda.sys_FileManager.getDocumentSource();
    src = { type: typeof raw, len: raw && raw.length, head: String(raw || '').slice(0, 80) };
  } catch (e) {
    src = { err: String(e && e.message || e).slice(0, 120) };
  }
  return {
    tries,
    afterUuid: after && after.uuid,
    pages,
    src,
    docType: after && after.documentType,
  };
})()
