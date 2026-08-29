(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const TAB = PAGE + '@' + HUB;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  try { await eda.sch_SelectControl.clearSelected(TAB); } catch (e) { /* ignore */ }
  const ids = ['ff12401c730641b7', '5cf017917b429da4', '0df3701fe687193c', 'c0d8ffdb09d7c8d8'];
  const sel = await eda.sch_SelectControl.doSelectPrimitives(['ff12401c730641b7'], TAB);
  try { void eda.dmt_EditorControl.zoomToSelectedPrimitives(TAB); } catch (e) { /* fire */ }
  return { proj: info.uuid, sel, ids };
})()
