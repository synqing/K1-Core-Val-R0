(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const TAB = PAGE + '@' + HUB;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  await eda.dmt_EditorControl.activateDocument(TAB);
  try { await eda.dmt_EditorControl.closeBottomPanel(); } catch (e) { /* ok */ }
  try { await eda.sch_SelectControl.clearSelected(); } catch (e) { /* ok */ }
  const ids = [
    '125f3f5842b2d308',
    '22c6a17a7dbbd174',
    'dac528b1bfdc76ab',
    '252b7a11c6b4da53',
    '6b258885a490d64b',
  ];
  await eda.sch_SelectControl.doSelectPrimitives(ids, TAB);
  try { eda.dmt_EditorControl.zoomToSelectedPrimitives(TAB); } catch (e) { /* fire */ }
  try { eda.dmt_EditorControl.zoomTo(1500, 1100, 700, TAB); } catch (e) { /* fire */ }
  return { proj: info.uuid, selected: ids };
})()
