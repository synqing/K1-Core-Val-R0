(async () => {
  const R = window._EXTAPI_ROOT_;
  const tab = '59bef7e87cff4cd580561703b62d8c19@64325d0e55e0435abd018defb0089a9b';
  const modelUuid = '71aa35b92da84360b5d9e21f25c486f0';
  const title = 'USB_C_Hirose_CX_4800304000_v3';
  const personal = '27700277ef7a49e48a0293bece6b2993';
  const out = { touched: [] };
  try { await R.dmt_EditorControl.activateDocument(tab); } catch (e) { out.activateErr = String(e && e.message || e); }
  await new Promise(r => setTimeout(r, 300));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const c = comps.find(x => (x.getState_Designator && x.getState_Designator()) === 'USB1');
  if (!c) return { ok: false, err: 'no USB1' };
  const sid = c.getState_SupplierId && c.getState_SupplierId();
  const mid = c.getState_ManufacturerId && c.getState_ManufacturerId();
  if (sid !== 'C778726' || mid !== 'CX70M-24P1') {
    return { ok: false, identityFail: { sid, mid } };
  }
  const prev = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
  await R.pcb_PrimitiveComponent.modify(c, {
    otherProperty: {
      ...prev,
      '3D Model': modelUuid,
      '3D Model Title': title,
      '3D Model Transform': prev['3D Model Transform'] || '0, 0, 0, 0, 0, 0, 0, 0, 0',
    },
    model3D: { libraryUuid: personal, uuid: modelUuid, name: title },
  });
  out.touched.push('USB1');
  const fresh = await R.pcb_PrimitiveComponent.get(c.getState_PrimitiveId());
  const other = (fresh.getState_OtherProperty && fresh.getState_OtherProperty()) || {};
  out.usb1 = {
    model3d: fresh.getState_Model3D && fresh.getState_Model3D(),
    other3d: {
      model: other['3D Model'],
      title: other['3D Model Title'],
      transform: other['3D Model Transform'],
    },
  };
  out.ok = out.usb1.other3d.model === modelUuid && out.usb1.other3d.title === title;
  return out;
})()
