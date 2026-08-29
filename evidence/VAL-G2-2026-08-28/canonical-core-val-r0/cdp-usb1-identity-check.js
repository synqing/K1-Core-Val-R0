(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  try { await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT); } catch (e) {}
  await new Promise(r => setTimeout(r, 500));
  const hash = (s) => {
    let h = 2166136261;
    for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
    return s.length + ':' + (h >>> 0).toString(16).padStart(8, '0');
  };
  const source = await R.sys_FileManager.getDocumentSource();
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const pick = (des) => {
    const c = comps.find(x => x.getState_Designator && x.getState_Designator() === des);
    if (!c) return { des, missing: true };
    const other = c.getState_OtherProperty() || {};
    return {
      des,
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      component: c.getState_Component && c.getState_Component(),
      footprint: c.getState_Footprint && c.getState_Footprint(),
      model3d: c.getState_Model3D && c.getState_Model3D(),
      model: other['3D Model'],
      title: other['3D Model Title'],
      transform: other['3D Model Transform'],
    };
  };
  return {
    sourceHash: hash(source),
    doc: await R.dmt_SelectControl.getCurrentDocumentInfo(),
    usb1: pick('USB1'),
    usb2: pick('USB2'),
    u6: pick('U6-RTC'),
  };
})()
