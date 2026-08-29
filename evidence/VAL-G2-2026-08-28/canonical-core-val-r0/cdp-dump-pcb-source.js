(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const TAB = PCB + '@' + PROJECT;
  const out = {};
  try { await R.dmt_EditorControl.activateDocument(TAB); } catch (e) { out.activateErr = String(e && e.message || e); }
  await new Promise(r => setTimeout(r, 400));
  try { out.project = await R.dmt_Project.getCurrentProjectInfo(); } catch (e) { out.projectErr = String(e && e.message || e); }
  try { out.doc = await R.dmt_SelectControl.getCurrentDocumentInfo(); } catch (e) { out.docErr = String(e && e.message || e); }
  let source = '';
  try { source = await R.sys_FileManager.getDocumentSource(); } catch (e) {
    try { source = await R.sys_FileManager.getDocumentSource(PCB); } catch (e2) { out.sourceErr = String(e2 && e2.message || e2); }
  }
  const hash = (s) => {
    let h = 2166136261;
    for (let i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return s.length + ':' + (h >>> 0).toString(16).padStart(8, '0');
  };
  out.sourceHash = source ? hash(source) : null;
  out.characters = source ? source.length : 0;
  out.source = source || '';
  out.projectUuid = out.project && out.project.uuid;
  out.docUuid = out.doc && out.doc.uuid;
  return out;
})()
