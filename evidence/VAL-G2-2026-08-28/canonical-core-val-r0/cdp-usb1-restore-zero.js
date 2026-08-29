(async () => {
  const R = window._EXTAPI_ROOT_;
  const TAB = '59bef7e87cff4cd580561703b62d8c19@64325d0e55e0435abd018defb0089a9b';
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const HIROSE = '71aa35b92da84360b5d9e21f25c486f0';
  const TITLE = 'USB_C_Hirose_CX_4800304000_v3';
  const DEV = '7e7eac39cf44433b9710c4ae4afab424';
  const NEW_T = '0, 0, 0, 0, 0, 0, 0, 0, 0';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  try { await R.dmt_EditorControl.activateDocument(TAB); } catch (e) {}
  await new Promise(r => setTimeout(r, 300));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const usb1 = comps.find(c => c.getState_Designator() === 'USB1');
  const usb2 = comps.find(c => c.getState_Designator() === 'USB2');
  const u6 = comps.find(c => c.getState_Designator() === 'U6-RTC');
  const inspect = (c) => {
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    return {
      des: c.getState_Designator(),
      sid: c.getState_SupplierId(),
      mid: c.getState_ManufacturerId(),
      transform: other['3D Model Transform'],
      model: other['3D Model'],
    };
  };
  if (!usb1 || usb1.getState_SupplierId() !== 'C778726') return { ok: false, identity: usb1 && inspect(usb1) };
  const prev = usb1.getState_OtherProperty() || {};
  const before = { usb1: inspect(usb1), usb2: inspect(usb2), u6: inspect(u6) };
  let device = { skipped: true };
  try {
    device = {
      ok: await R.lib_Device.modify(
        DEV,
        PERSONAL,
        undefined,
        null,
        { model3D: { uuid: HIROSE, libraryUuid: PERSONAL } },
        undefined,
        {
          otherProperty: {
            '3D Model': HIROSE,
            '3D Model Title': TITLE,
            '3D Model Transform': NEW_T,
          },
        },
      ),
    };
  } catch (e) {
    device = { ok: false, err: String(e && e.message || e) };
  }
  const modify = await R.pcb_PrimitiveComponent.modify(usb1, {
    otherProperty: {
      ...prev,
      '3D Model': HIROSE,
      '3D Model Title': TITLE,
      '3D Model Transform': NEW_T,
    },
    model3D: { libraryUuid: PERSONAL, uuid: HIROSE, name: TITLE },
  });
  const saved = await R.pcb_Document.save(PCB);
  const again = await R.pcb_PrimitiveComponent.getAll();
  const a1 = again.find(c => c.getState_Designator() === 'USB1');
  const a2 = again.find(c => c.getState_Designator() === 'USB2');
  const a6 = again.find(c => c.getState_Designator() === 'U6-RTC');
  let deviceAfter = null;
  try {
    const d = await R.lib_Device.get(DEV, PERSONAL);
    deviceAfter = d && d.property && d.property.otherProperty
      ? d.property.otherProperty['3D Model Transform']
      : null;
  } catch (e) {
    deviceAfter = String(e && e.message || e);
  }
  const after = { usb1: inspect(a1), usb2: inspect(a2), u6: inspect(a6) };
  return {
    ok: after.usb1.transform === NEW_T
      && after.usb2.transform === before.usb2.transform
      && after.u6.transform === before.u6.transform,
    saved,
    modify,
    device,
    deviceAfter,
    before,
    after,
  };
})()
