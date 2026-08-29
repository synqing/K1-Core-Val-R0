(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const TAB = PAGE + '@' + HUB;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  try { await eda.sch_SelectControl.clearSelected(TAB); } catch (e) { /* ignore */ }
  const ids = ['b027c9ae9b996415', '2b96fee724a60013', '955e9ad023078e73'];
  const sel = await eda.sch_SelectControl.doSelectPrimitives(ids, TAB);
  try { void eda.dmt_EditorControl.zoomToSelectedPrimitives(TAB); } catch (e) { /* fire */ }
  return { proj: info.uuid, sel };
})()
