(async () => {
  const R = window._EXTAPI_ROOT_;
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  try { await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT); } catch (e) {}
  await new Promise(r => setTimeout(r, 400));
  const inspect = (c) => {
    if (!c) return null;
    const props = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    const get = (k) => props[k];
    return {
      des: c.getState_Designator && c.getState_Designator(),
      id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      model: get('3D Model'),
      title: get('3D Model Title'),
      xf: get('3D Model Transform'),
      model3d: c.getState_Model3D ? c.getState_Model3D() : null,
    };
  };
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const source = await R.sys_FileManager.getDocumentSource();
  const buf = new TextEncoder().encode(source);
  const digest = await crypto.subtle.digest('SHA-256', buf);
  const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
  return {
    sourceHash: source.length + ':' + hex.slice(0, 8),
    u1: inspect(comps.find(c => c.getState_Designator && c.getState_Designator() === 'U1')),
    u6: inspect(comps.find(c => c.getState_Designator && c.getState_Designator() === 'U6-RTC')),
    d1: inspect(comps.find(c => c.getState_Designator && c.getState_Designator() === 'D1-PWR1')),
    usb1: !!comps.find(c => c.getState_Designator && c.getState_Designator() === 'USB1'),
  };
})()
