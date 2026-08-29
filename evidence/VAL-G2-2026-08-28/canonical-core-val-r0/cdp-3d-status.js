(async () => {
  const R = window._EXTAPI_ROOT_;
  const dialogs = [...document.querySelectorAll('div,span,button,[role="dialog"]')]
    .filter(el => el.offsetParent !== null)
    .map(el => (el.getAttribute('title') || el.textContent || '').trim())
    .filter(t => /export|3d file|cancel|save as|dialog/i.test(t))
    .slice(0, 30);
  let current = null;
  try { current = await R.dmt_SelectControl.getCurrentDocumentInfo(); } catch (e) { current = String(e); }
  let docs = null;
  try {
    docs = await R.dmt_EditorControl.getOpenedDocuments();
  } catch (e) {
    docs = { err: String(e && e.message || e) };
  }
  const titles = [...document.querySelectorAll('[title]')].filter(el => el.offsetParent !== null)
    .map(el => el.getAttribute('title'))
    .filter(t => t && /3D|Preview|PCB|USB/i.test(t))
    .slice(0, 40);
  return { current, docs, titles, dialogs };
})()
