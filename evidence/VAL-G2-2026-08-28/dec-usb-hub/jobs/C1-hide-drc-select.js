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
  const keys = Object.keys(eda.dmt_EditorControl || {});
  closed.push({ editorKeys: keys.filter((k) => /panel|drc|bottom|dock|zoom/i.test(k)) });
  for (const name of ['closeBottomPanel', 'hideBottomPanel', 'closePanel']) {
    try {
      if (eda.dmt_EditorControl[name]) {
        await eda.dmt_EditorControl[name]();
        closed.push(name);
      }
    } catch (e) {
      closed.push(name + '-fail');
    }
  }
  try {
    if (eda.dmt_EditorControl.setPanelVisible) {
      await eda.dmt_EditorControl.setPanelVisible('drc', false);
      closed.push('setPanelVisible-drc-false');
    }
  } catch (e) {
    closed.push('setPanelVisible-fail');
  }
  await eda.sch_SelectControl.doSelectPrimitives(['e72', 'e108'], TAB);
  let selected = null;
  try {
    selected = await eda.sch_SelectControl.getSelectedPrimitiveIds(TAB);
  } catch (e) {
    try {
      selected = await eda.sch_SelectControl.getSelectedPrimitives(TAB);
    } catch (e2) {
      selected = String(e2 && e2.message || e2).slice(0, 80);
    }
  }
  try {
    void eda.dmt_EditorControl.zoomToSelectedPrimitives(TAB);
    closed.push('zoom-fired');
  } catch (e) {
    closed.push('zoom-fail');
  }
  const c1 = await eda.sch_PrimitiveComponent.get('e72');
  const c2 = await eda.sch_PrimitiveComponent.get('e108');
  const s1 = c1.getState ? c1.getState() : c1;
  const s2 = c2.getState ? c2.getState() : c2;
  return {
    proj: info.uuid,
    closed,
    selected,
    c1: { designator: s1.designator, name: s1.name, x: s1.x, y: s1.y },
    c2: { designator: s2.designator, name: s2.name, x: s2.x, y: s2.y },
  };
})()
