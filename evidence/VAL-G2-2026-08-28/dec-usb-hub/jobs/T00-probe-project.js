(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  if (!eda) return { stop: true, reason: 'NO_EXTAPI' };
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  let info = null;
  try { info = await eda.dmt_Project.getCurrentProjectInfo(); } catch (e) { info = { error: String(e && e.message || e) }; }
  const proj = info && info.uuid;
  let opened = null;
  if (proj !== HUB && proj !== LIVE) {
    try {
      opened = await eda.dmt_Project.openProject(HUB);
    } catch (e) {
      opened = { error: String(e && e.message || e) };
    }
    await new Promise((r) => setTimeout(r, 4000));
    try { info = await eda.dmt_Project.getCurrentProjectInfo(); } catch (e) { info = { error: String(e && e.message || e) }; }
  }
  if (info && info.uuid === LIVE) return { stop: true, reason: 'LIVE_FOCUSED', info, opened };
  let activated = null;
  try {
    activated = await eda.dmt_EditorControl.activateDocument('1435cb46f39e48c8a8aadbb84ca81603@41c8e6523576456582ea35958b3684ed');
  } catch (e) {
    activated = { error: String(e && e.message || e) };
  }
  await new Promise((r) => setTimeout(r, 1500));
  let doc = null;
  try {
    doc = eda.dmt_EditorControl.getCurrentDocumentUuid
      ? await eda.dmt_EditorControl.getCurrentDocumentUuid()
      : null;
  } catch (e) { doc = { error: String(e && e.message || e) }; }
  return {
    proj: info && info.uuid,
    friendly: info && (info.friendlyName || info.name),
    opened,
    activated,
    doc,
    hubOk: (info && info.uuid) === HUB,
  };
})()
