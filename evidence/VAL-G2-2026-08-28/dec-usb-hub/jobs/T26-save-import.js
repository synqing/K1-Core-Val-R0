(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const TARGET = '54d2a25bce4b44c3af878e8b91af3554';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== TARGET) return { stop: true, reason: 'NOT_IMPORT', uuid: current && current.uuid };
  if ([LIVE, HUB].includes(current.uuid)) return { stop: true, reason: 'FORBIDDEN' };
  const own = (obj) => {
    const names = [];
    let cur = obj;
    let depth = 0;
    while (cur && depth < 4) {
      names.push(...Object.getOwnPropertyNames(cur));
      cur = Object.getPrototypeOf(cur);
      depth += 1;
    }
    return [...new Set(names)].filter((n) => typeof obj[n] === 'function' && /save/i.test(n)).sort();
  };
  const candidates = {
    editor: own(eda.dmt_EditorControl || {}),
    schDoc: own(eda.sch_Document || {}),
    file: own(eda.sys_FileManager || {}),
    project: own(eda.dmt_Project || {}),
  };
  let saved = null;
  const tries = [];
  const fns = [
    ['dmt_EditorControl', 'saveActiveDocument'],
    ['dmt_EditorControl', 'saveDocument'],
    ['dmt_EditorControl', 'save'],
    ['sch_Document', 'save'],
    ['sch_Document', 'saveDocument'],
  ];
  for (const [ns, fn] of fns) {
    const obj = eda[ns];
    if (obj && typeof obj[fn] === 'function') {
      try {
        const result = await obj[fn]();
        tries.push({ ns, fn, type: typeof result, keys: result && typeof result === 'object' ? Object.keys(result).slice(0, 12) : null, saved: result && result.saved });
        saved = result;
        break;
      } catch (e) {
        tries.push({ ns, fn, err: String(e && e.message || e).slice(0, 160) });
      }
    }
  }
  const src = String(await eda.sys_FileManager.getDocumentSource() || '');
  return {
    uuid: current.uuid,
    name: current.friendlyName,
    candidates,
    tries,
    savedType: saved == null ? null : typeof saved,
    srcLen: src.length,
    u20: src.includes('U20'),
    page: PAGE,
  };
})()
