(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const TAB = PAGE + '@' + HUB;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  try { await eda.sch_SelectControl.clearSelected(TAB); } catch (e) { /* ignore */ }
  try { eda.dmt_EditorControl.zoomTo(-200, 3000, 250); } catch (e) { /* ignore */ }
  return { proj: info.uuid };
})()
