(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  try { await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT); } catch (e) {}
  await new Promise(r => setTimeout(r, 500));
  const source = await R.sys_FileManager.getDocumentSource();
  const buf = new TextEncoder().encode(source);
  const digest = await crypto.subtle.digest('SHA-256', buf);
  const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const inspect = (c) => {
    if (!c) return { missing: true };
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    return {
      des: c.getState_Designator && c.getState_Designator(),
      id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      x: c.getState_X && c.getState_X(),
      y: c.getState_Y && c.getState_Y(),
      rot: c.getState_Rotation && c.getState_Rotation(),
      component: c.getState_Component && c.getState_Component(),
      footprint: c.getState_Footprint && c.getState_Footprint(),
      model3d: c.getState_Model3D && c.getState_Model3D(),
      model: other['3D Model'],
      title: other['3D Model Title'],
      xf: other['3D Model Transform'],
    };
  };
  const byDes = (d) => inspect(comps.find(c => c.getState_Designator && c.getState_Designator() === d));
  const usbish = comps.filter(c => {
    const des = c.getState_Designator && c.getState_Designator();
    const mid = c.getState_ManufacturerId && c.getState_ManufacturerId();
    const sid = c.getState_SupplierId && c.getState_SupplierId();
    const fp = c.getState_Footprint && c.getState_Footprint();
    return /USB|CX70|HYCW|7005|TYPE-C|Hirose/i.test([des, mid, sid, fp && fp.name].join(' '));
  }).map(inspect);
  return {
    doc: await R.dmt_SelectControl.getCurrentDocumentInfo(),
    sourceHash: source.length + ':' + hex.slice(0, 8),
    sourceLen: source.length,
    USB1: byDes('USB1'),
    USB2: byDes('USB2'),
    U1: byDes('U1'),
    U6: byDes('U6-RTC'),
    usbish,
    needles: {
      USB1: source.includes('USB1'),
      CX70M: source.includes('CX70M'),
      C778726: source.includes('C778726'),
      U1: source.includes('"U1"'),
    },
  };
})()
