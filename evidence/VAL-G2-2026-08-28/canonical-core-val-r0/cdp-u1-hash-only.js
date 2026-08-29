(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  try { await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT); } catch (e) {}
  await new Promise(r => setTimeout(r, 300));
  const doc2 = await R.dmt_SelectControl.getCurrentDocumentInfo();
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const u1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'U1');
  const other = (u1.getState_OtherProperty && u1.getState_OtherProperty()) || {};
  const source = await R.sys_FileManager.getDocumentSource();
  const buf = new TextEncoder().encode(source);
  const digest = await crypto.subtle.digest('SHA-256', buf);
  const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
  return {
    docBefore: doc,
    docAfter: doc2,
    sourceHash: source.length + ':' + hex.slice(0, 8),
    u1: {
      sid: u1.getState_SupplierId && u1.getState_SupplierId(),
      mid: u1.getState_ManufacturerId && u1.getState_ManufacturerId(),
      model: other['3D Model'],
      title: other['3D Model Title'],
      xf: other['3D Model Transform'],
      model3d: u1.getState_Model3D && u1.getState_Model3D(),
    },
  };
})()
