(async () => {
  const R = window._EXTAPI_ROOT_;
  const tab = '59bef7e87cff4cd580561703b62d8c19@64325d0e55e0435abd018defb0089a9b';
  try { await R.dmt_EditorControl.activateDocument(tab); } catch (e) {}
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const modelUuid = '71aa35b92da84360b5d9e21f25c486f0';
  let usb1;
  for (const c of comps) {
    const des = c.getState_Designator && c.getState_Designator();
    if (des !== 'USB1') continue;
    const prev = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    c.setState_OtherProperty({
      ...prev,
      '3D Model': modelUuid,
      '3D Model Title': 'USB_C_Hirose_CX_4800304000_v3',
      '3D Model Transform': prev['3D Model Transform'] || '0, 0, 0, 0, 0, 0, 0, 0, 0',
    });
    const other = c.getState_OtherProperty() || {};
    usb1 = {
      des,
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      model3d: c.getState_Model3D && c.getState_Model3D(),
      title: other['3D Model Title'],
      model: other['3D Model'],
    };
  }
  return { ok: !!(usb1 && usb1.model === modelUuid), usb1 };
})()
