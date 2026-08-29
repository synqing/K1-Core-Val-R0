(async () => {
  const R = window._EXTAPI_ROOT_;
  const TAB = '59bef7e87cff4cd580561703b62d8c19@64325d0e55e0435abd018defb0089a9b';
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const HIROSE = '71aa35b92da84360b5d9e21f25c486f0';
  const TITLE = 'USB_C_Hirose_CX_4800304000_v3';
  const NEW_T = '448.8179849815368,328.7394915521145,0,0,0,0,0,-66.733,-80.315';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  try { await R.dmt_EditorControl.activateDocument(TAB); } catch (e) {}
  await new Promise(r => setTimeout(r, 300));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const usb1 = comps.find(c => c.getState_Designator() === 'USB1');
  const usb2 = comps.find(c => c.getState_Designator() === 'USB2');
  const u6 = comps.find(c => c.getState_Designator() === 'U6-RTC');
  const inspect = (c) => {
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    return { des: c.getState_Designator(), sid: c.getState_SupplierId(), mid: c.getState_ManufacturerId(), transform: other['3D Model Transform'] };
  };
  if (usb1.getState_SupplierId() !== 'C778726') return { ok: false, identity: inspect(usb1) };
  const prev = usb1.getState_OtherProperty() || {};
  await R.pcb_PrimitiveComponent.modify(usb1, {
    otherProperty: { ...prev, '3D Model': HIROSE, '3D Model Title': TITLE, '3D Model Transform': NEW_T },
    model3D: { libraryUuid: PERSONAL, uuid: HIROSE, name: TITLE },
  });
  const saved = await R.pcb_Document.save(PCB);
  const again = await R.pcb_PrimitiveComponent.getAll();
  const a1 = again.find(c => c.getState_Designator() === 'USB1');
  const a2 = again.find(c => c.getState_Designator() === 'USB2');
  const a6 = again.find(c => c.getState_Designator() === 'U6-RTC');
  return {
    ok: inspect(a1).transform === NEW_T,
    saved,
    beforeUsb2: inspect(usb2),
    after: { usb1: inspect(a1), usb2: inspect(a2), u6: inspect(a6) },
  };
})()
