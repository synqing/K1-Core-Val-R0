(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  function sourceHash(source) {
    let hash = 2166136261;
    for (let i = 0; i < source.length; i += 1) {
      hash ^= source.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return source.length + ':' + (hash >>> 0).toString(16).padStart(8, '0');
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  const W = eda.sch_PrimitiveWire;
  const methods = Object.keys(W || {});
  const proto = Object.getOwnPropertyNames(Object.getPrototypeOf(W) || {}).filter((n) => /del|rem|des/i.test(n));
  const lift = [];
  for (const id of ['ebrw000226', 'ebrw000228', 'ebrw000203', 'ebrw000224']) {
    const row = { id };
    try {
      if (typeof W.delete === 'function') {
        row.delete = await W.delete(id);
      } else if (typeof W.deletePrimitive === 'function') {
        row.delete = await W.deletePrimitive(id);
      } else if (typeof W.remove === 'function') {
        row.delete = await W.remove(id);
      } else {
        row.noDelete = true;
      }
    } catch (e) {
      row.err = String(e && e.message || e).slice(0, 160);
    }
    lift.push(row);
  }
  const created = [];
  try {
    created.push({ tag: 'rdp', r: await W.create([[575, 4165, 640, 4165]], 'USB_DP_UP') });
  } catch (e) { created.push({ tag: 'rdp', err: String(e && e.message || e).slice(0, 160) }); }
  try {
    created.push({ tag: 'rdn', r: await W.create([[575, 4190, 640, 4190]], 'USB_DM_UP') });
  } catch (e) { created.push({ tag: 'rdn', err: String(e && e.message || e).slice(0, 160) }); }
  await eda.sch_Document.save();
  const source = await eda.sys_FileManager.getDocumentSource();
  return {
    proj: info.uuid,
    methods: methods.filter((n) => /del|rem|create|mod/i.test(n)),
    proto,
    lift,
    created,
    saved: true,
    sourceHash: sourceHash(source),
    hasDpUp: /USB_DP_UP/.test(source),
    hasDpRt: /USB_DP_RT/.test(source),
    hasDnRt: /USB_DN_RT/.test(source),
    d1: (await eda.sch_PrimitiveComponent.get('e252')).designator,
  };
})()
