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
  const closed = [];
  try {
    if (eda.dmt_EditorControl.closeBottomPanel) {
      await eda.dmt_EditorControl.closeBottomPanel();
      closed.push('closeBottomPanel');
    }
  } catch (e) {
    closed.push('closeBottomPanel-fail');
  }
  try {
    if (eda.dmt_EditorControl.setPanelVisible) {
      await eda.dmt_EditorControl.setPanelVisible('drc', false);
      closed.push('setPanelVisible-drc');
    }
  } catch (e) {
    closed.push('setPanelVisible-fail');
  }
  const ids = [
    '125f3f5842b2d308',
    '22c6a17a7dbbd174',
    'dac528b1bfdc76ab',
    '252b7a11c6b4da53',
    '6b258885a490d64b',
    'e8e13777e6daf227',
  ];
  try {
    await eda.sch_SelectControl.doSelectPrimitives(ids, TAB);
    await eda.dmt_EditorControl.zoomToSelectedPrimitives(TAB);
    closed.push('zoomed');
  } catch (e) {
    closed.push('zoom-fail:' + String(e && e.message || e).slice(0, 80));
  }
  return { proj: info.uuid, closed };
})()
