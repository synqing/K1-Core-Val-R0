(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE) return { stop: true, reason: info && info.uuid === LIVE ? 'LIVE' : 'NO_PROJ', info };
  if (info.uuid !== HUB) return { stop: true, reason: 'WRONG', uuid: info.uuid };

  const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(eda.dmt_EditorControl)).filter((n) => /document|tab|open|activ/i.test(n));
  let tabs = null;
  try { tabs = await eda.dmt_EditorControl.getTabsBySplitScreenId('editor-window-main'); } catch (e) { tabs = { error: String(e && e.message || e) }; }

  let opened = null;
  try { opened = await eda.dmt_EditorControl.openDocument(PAGE); } catch (e) { opened = { error: String(e && e.message || e) }; }
  await new Promise((r) => setTimeout(r, 1500));
  let activated = null;
  try { activated = await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB); } catch (e) { activated = { error: String(e && e.message || e) }; }
  await new Promise((r) => setTimeout(r, 800));

  let pinIds = null;
  try { pinIds = { count: (await eda.sch_PrimitiveComponent.getAllPrimitiveId() || []).length }; }
  catch (e) { pinIds = { error: String(e && e.message || e) }; }

  return {
    proj: info.uuid,
    friendly: info.friendlyName || info.name,
    methods,
    tabs: Array.isArray(tabs) ? tabs.map((t) => ({ id: t.tabId || t.id, title: t.title })) : tabs,
    opened,
    activated,
    components: pinIds,
  };
})()
