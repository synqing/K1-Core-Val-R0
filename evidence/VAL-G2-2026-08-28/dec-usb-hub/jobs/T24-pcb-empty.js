(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  await eda.dmt_EditorControl.activateDocument(PCB + '@' + HUB);
  let comps = null;
  let vias = null;
  let err = null;
  try {
    comps = ((await eda.pcb_PrimitiveComponent.getAllPrimitiveId()) || []).length;
  } catch (e) {
    err = String(e && e.message || e).slice(0, 160);
  }
  try {
    vias = ((await eda.pcb_PrimitiveVia.getAllPrimitiveId()) || []).length;
  } catch (e) {
    err = (err ? err + ' | ' : '') + String(e && e.message || e).slice(0, 160);
  }
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  const after = await eda.dmt_Project.getCurrentProjectInfo();
  return {
    proj: after.uuid,
    pcbComps: comps,
    pcbVias: vias,
    err,
    backOnHub: after.uuid === HUB,
  };
})()
