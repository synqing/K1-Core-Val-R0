(async () => {
  const R = window._EXTAPI_ROOT_;
  let current = null;
  try {
    const c = await R.dmt_SelectControl.getCurrentDocumentInfo();
    current = {
      tabId: c.tabId, documentType: c.documentType, uuid: c.uuid,
      name: c.name, title: c.title, projectUuid: c.projectUuid,
    };
  } catch (e) { current = String(e && e.message || e); }
  let docs = [];
  try {
    const all = await R.dmt_EditorControl.getAllOpenedDocumentsInfo();
    docs = (all || []).map(d => ({
      tabId: d.tabId, documentType: d.documentType, uuid: d.uuid,
      name: d.name, title: d.title,
    }));
  } catch (e) { docs = [{ err: String(e && e.message || e) }]; }
  const titles = [...document.querySelectorAll('[title]')].filter(el => el.offsetParent !== null)
    .map(el => el.getAttribute('title'))
    .filter(t => t && /3D|Preview|Export|PCB|USB/.test(t))
    .slice(0, 40);
  const dialogText = [...document.querySelectorAll('[role="dialog"], .ant-modal, .el-dialog')]
    .filter(el => el.offsetParent !== null)
    .map(el => (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 200));
  return { current, docs, titles, dialogText };
})()
