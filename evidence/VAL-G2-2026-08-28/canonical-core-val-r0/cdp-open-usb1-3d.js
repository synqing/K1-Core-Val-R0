(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const out = { tabs: [], clicks: [] };
  try { out.docs = await R.dmt_EditorControl.getAllOpenedDocumentsInfo(); } catch (e) { out.docsErr = String(e && e.message || e); }
  try { out.current = await R.dmt_SelectControl.getCurrentDocumentInfo(); } catch (e) { out.currentErr = String(e && e.message || e); }
  const named = (obj) => {
    const keys = [];
    let p = obj;
    while (p && p !== Object.prototype && keys.length < 80) {
      for (const k of Object.getOwnPropertyNames(p)) {
        if (/3d|3D|preview|Preview|open/i.test(k)) keys.push(k);
      }
      p = Object.getPrototypeOf(p);
    }
    return keys;
  };
  out.editor3d = named(R.dmt_EditorControl);
  out.pcbDoc3d = named(R.pcb_Document);
  out.header3d = named(R.sys_HeaderMenu);
  const tryOpen = async (id) => {
    try { return { id, tab: await R.dmt_EditorControl.openDocument(id) }; }
    catch (e) { return { id, err: String(e && e.message || e) }; }
  };
  out.try3d = await tryOpen('3d-' + PCB);
  out.try3dAt = await tryOpen('3d-' + PCB + '@' + PROJECT);
  out.tryPcb3d = await tryOpen(PCB + '-3d');
  await new Promise(r => setTimeout(r, 400));
  try { out.after = await R.dmt_SelectControl.getCurrentDocumentInfo(); } catch (e) { out.afterErr = String(e && e.message || e); }

  const titles = [...document.querySelectorAll('[title],button,div,span')]
    .filter(el => el.offsetParent !== null)
    .map(el => (el.getAttribute('title') || el.textContent || '').trim())
    .filter(t => /3[Dd]|Preview|预览/.test(t))
    .slice(0, 40);
  out.visible3dTitles = titles;

  const fitSel = [...document.querySelectorAll('[title]')].find(x =>
    x.offsetParent !== null && String(x.getAttribute('title') || '').startsWith('Fit Selection View'));
  out.hasFit = !!fitSel;

  try {
    await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT);
    await new Promise(r => setTimeout(r, 200));
    if (R.pcb_SelectControl && R.pcb_SelectControl.doSelectPrimitives) {
      R.pcb_SelectControl.doSelectPrimitives(['19bbd06e9438ab5d'], PCB + '@' + PROJECT);
      out.selected = true;
    }
  } catch (e) { out.selectErr = String(e && e.message || e); }

  return out;
})()
