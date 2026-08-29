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
  const wireIds = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  const want = ['fd3dd96d58a6e4c4', 'f030c09f4f3caf10'];
  const present = {};
  for (const id of want) present[id] = (wireIds || []).includes(id);
  const methods = Object.keys(eda.sch_PrimitiveWire || {}).slice(0, 40);
  let byPrim = null;
  try {
    const p = await eda.sch_Primitive.getPrimitiveByPrimitiveId('fd3dd96d58a6e4c4');
    byPrim = p ? { type: typeof p, keys: Object.keys(p).slice(0, 20), hasGetState: typeof p.getState } : null;
  } catch (e) {
    byPrim = { err: String(e && e.message || e).slice(0, 160) };
  }
  const source = await eda.sys_FileManager.getDocumentSource();
  const comps = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const island = (source.match(/fd3dd96d58a6e4c4|f030c09f4f3caf10/g) || []).length;
  return {
    proj: info.uuid,
    sourceHash: sourceHash(source),
    components: (comps || []).length,
    wires: (wireIds || []).length,
    present,
    methods,
    byPrim,
    islandMentions: island,
  };
})()
