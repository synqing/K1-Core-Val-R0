(async () => {
  const R = window._EXTAPI_ROOT_;
  const TAB = '59bef7e87cff4cd580561703b62d8c19@64325d0e55e0435abd018defb0089a9b';
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const HIROSE = '71aa35b92da84360b5d9e21f25c486f0';
  const TITLE = 'USB_C_Hirose_CX_4800304000_v3';
  const NEW_T = '448.8179849815368,328.7394915521145,145.27529755949973,0,0,0,0,0,-80.315';
  const out = {};
  try { await R.dmt_EditorControl.activateDocument(TAB); } catch (e) { out.activateErr = String(e && e.message || e); }
  await new Promise(r => setTimeout(r, 300));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const named = (obj) => obj ? Object.getOwnPropertyNames(Object.getPrototypeOf(obj)).filter(k => /save/i.test(k)) : [];
  out.saveMethods = {
    project: named(R.dmt_Project),
    editor: named(R.dmt_EditorControl),
    file: named(R.sys_FileManager),
  };
  const usb1 = comps.find(c => (c.getState_Designator && c.getState_Designator()) === 'USB1');
  const usb2 = comps.find(c => (c.getState_Designator && c.getState_Designator()) === 'USB2');
  const u6 = comps.find(c => (c.getState_Designator && c.getState_Designator()) === 'U6-RTC');
  if (!usb1) return { ok: false, err: 'no USB1' };
  const sid = usb1.getState_SupplierId && usb1.getState_SupplierId();
  const mid = usb1.getState_ManufacturerId && usb1.getState_ManufacturerId();
  if (sid !== 'C778726' || mid !== 'CX70M-24P1') return { ok: false, identityFail: { sid, mid } };
  const inspect = (c) => {
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    return {
      id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
      des: c.getState_Designator && c.getState_Designator(),
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      model: other['3D Model'],
      title: other['3D Model Title'],
      transform: other['3D Model Transform'],
      model3d: c.getState_Model3D && c.getState_Model3D(),
    };
  };
  out.before = { usb1: inspect(usb1), usb2: usb2 && inspect(usb2), u6: u6 && inspect(u6) };
  const prev = (usb1.getState_OtherProperty && usb1.getState_OtherProperty()) || {};
  try {
    out.modify = await R.pcb_PrimitiveComponent.modify(usb1, {
      otherProperty: {
        ...prev,
        '3D Model': HIROSE,
        '3D Model Title': TITLE,
        '3D Model Transform': NEW_T,
      },
      model3D: { libraryUuid: PERSONAL, uuid: HIROSE, name: TITLE },
    });
  } catch (e) {
    out.modifyErr = String(e && e.message || e);
    try {
      out.modify2 = await R.pcb_PrimitiveComponent.modify(usb1.getState_PrimitiveId(), {
        otherProperty: {
          ...prev,
          '3D Model': HIROSE,
          '3D Model Title': TITLE,
          '3D Model Transform': NEW_T,
        },
      });
    } catch (e2) { out.modify2Err = String(e2 && e2.message || e2); }
  }
  const trySave = async (label, fn) => {
    try { out[label] = await fn(); } catch (e) { out[label + 'Err'] = String(e && e.message || e); }
  };
  if (R.dmt_Project && typeof R.dmt_Project.saveProject === 'function') {
    await trySave('saveProject', () => R.dmt_Project.saveProject());
  }
  if (R.dmt_EditorControl && typeof R.dmt_EditorControl.saveActiveDocument === 'function') {
    await trySave('saveActive', () => R.dmt_EditorControl.saveActiveDocument());
  }
  if (R.sys_FileManager && typeof R.sys_FileManager.saveDocument === 'function') {
    await trySave('saveDocument', () => R.sys_FileManager.saveDocument());
  }
  const again = await R.pcb_PrimitiveComponent.getAll();
  const a1 = again.find(c => (c.getState_Designator && c.getState_Designator()) === 'USB1');
  const a2 = again.find(c => (c.getState_Designator && c.getState_Designator()) === 'USB2');
  const a6 = again.find(c => (c.getState_Designator && c.getState_Designator()) === 'U6-RTC');
  out.after = { usb1: a1 && inspect(a1), usb2: a2 && inspect(a2), u6: a6 && inspect(a6) };
  out.ok = !!(out.after.usb1 && out.after.usb1.transform === NEW_T && out.after.usb1.sid === 'C778726');
  out.usb2Unchanged = out.before.usb2 && out.after.usb2 && out.before.usb2.transform === out.after.usb2.transform;
  out.u6Unchanged = out.before.u6 && out.after.u6 && out.before.u6.transform === out.after.u6.transform;
  return out;
})()
