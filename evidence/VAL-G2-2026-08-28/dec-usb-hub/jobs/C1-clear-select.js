(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const TAB = PAGE + '@' + HUB;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const c1 = await eda.sch_PrimitiveComponent.get('e72');
  const c2 = await eda.sch_PrimitiveComponent.get('e108');
  try { await eda.sch_SelectControl.clearSelected(TAB); } catch (e) { /* ignore */ }
  try { await eda.sch_SelectControl.clearSelected(); } catch (e) { /* ignore */ }
  const afterClear = await eda.sch_SelectControl.getAllSelectedPrimitives_PrimitiveId(TAB);
  const sel = await eda.sch_SelectControl.doSelectPrimitives(['e72', 'e108'], TAB);
  const afterSel = await eda.sch_SelectControl.getAllSelectedPrimitives_PrimitiveId(TAB);
  const EC = eda.dmt_EditorControl;
  try { void EC.zoomToSelectedPrimitives(TAB); } catch (e) { /* fire-and-forget */ }
  return {
    proj: info.uuid,
    c1: { id: c1 && c1.id, name: c1 && c1.name, designator: c1 && c1.designator, x: c1 && c1.x, y: c1 && c1.y },
    c2: { id: c2 && c2.id, name: c2 && c2.name, designator: c2 && c2.designator, x: c2 && c2.x, y: c2 && c2.y },
    afterClearCount: (afterClear || []).length,
    sel,
    afterSel,
  };
})()
