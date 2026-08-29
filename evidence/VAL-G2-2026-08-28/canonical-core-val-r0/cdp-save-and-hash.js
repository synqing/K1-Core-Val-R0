(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const hash = (s) => {
    let h = 2166136261;
    for (let i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return s.length + ':' + (h >>> 0).toString(16).padStart(8, '0');
  };
  const out = { saves: {} };
  const tryCall = async (label, fn) => {
    try { out.saves[label] = await fn(); } catch (e) { out.saves[label] = 'ERR ' + String(e && e.message || e); }
  };
  if (R.dmt_Project) {
    await tryCall('project.save', () => R.dmt_Project.save(PROJECT));
    await tryCall('project.saveCurrent', () => R.dmt_Project.save());
  }
  if (R.dmt_EditorControl) {
    await tryCall('editor.save', () => R.dmt_EditorControl.save());
    await tryCall('editor.saveDocument', () => R.dmt_EditorControl.saveDocument(PCB));
  }
  if (R.pcb_Document) {
    await tryCall('pcb.save', () => R.pcb_Document.save(PCB));
    await tryCall('pcb.saveEmpty', () => R.pcb_Document.save());
  }
  await new Promise(r => setTimeout(r, 500));
  let source = '';
  try { source = await R.sys_FileManager.getDocumentSource(); } catch (e) {
    try { source = await R.sys_FileManager.getDocumentSource(PCB); } catch (e2) { out.sourceErr = String(e2 && e2.message || e2); }
  }
  out.sourceHash = source ? hash(source) : null;
  out.characters = source ? source.length : 0;
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const c = comps.find(x => x.getState_Designator() === 'USB1');
  const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
  out.usb1Transform = other['3D Model Transform'];
  return out;
})()
