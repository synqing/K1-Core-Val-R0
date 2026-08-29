(async () => {
  const R = window._EXTAPI_ROOT_;
  const tab = '59bef7e87cff4cd580561703b62d8c19@64325d0e55e0435abd018defb0089a9b';
  try { await R.dmt_EditorControl.activateDocument(tab); } catch (e) {}
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const HIROSE = '71aa35b92da84360b5d9e21f25c486f0';
  const NXP = 'de5664fd2ea74aa082831cfa5b198edb';
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const named = (obj) => obj ? Object.getOwnPropertyNames(Object.getPrototypeOf(obj)).filter(k => /modif|Model|Other|done/i.test(k)) : [];
  const out = { methods: named(R.pcb_PrimitiveComponent), rows: [] };

  const inspect = (c) => {
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    return {
      id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
      des: c.getState_Designator && c.getState_Designator(),
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      model3d: c.getState_Model3D && c.getState_Model3D(),
      title: other['3D Model Title'],
      model: other['3D Model'],
    };
  };

  let u6, usb1;
  for (const c of comps) {
    const des = c.getState_Designator && c.getState_Designator();
    if (des === 'U6-RTC') u6 = c;
    if (des === 'USB1') usb1 = c;
  }
  out.before = { u6: u6 && inspect(u6), usb1: usb1 && inspect(usb1) };

  const tryModify = async (c, label, modelUuid, title, extra) => {
    const row = { label };
    const id = c.getState_PrimitiveId && c.getState_PrimitiveId();
    const prev = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    const nextOther = {
      ...prev,
      '3D Model': modelUuid,
      '3D Model Title': title,
      '3D Model Transform': prev['3D Model Transform'] || '0, 0, 0, 0, 0, 0, 0, 0, 0',
    };
    try {
      row.classModify = await R.pcb_PrimitiveComponent.modify(id, {
        otherProperty: nextOther,
        model3D: { libraryUuid: PERSONAL, uuid: modelUuid, name: title },
      });
    } catch (e) {
      row.classModifyErr = String(e && e.message || e);
      try {
        row.classModify2 = await R.pcb_PrimitiveComponent.modify({
          id,
          otherProperty: nextOther,
          model3D: { libraryUuid: PERSONAL, uuid: modelUuid, name: title },
        });
      } catch (e2) { row.classModify2Err = String(e2 && e2.message || e2); }
    }
    if (typeof c.modify === 'function') {
      try {
        row.instModify = await c.modify({
          otherProperty: nextOther,
          model3D: { libraryUuid: PERSONAL, uuid: modelUuid, name: title },
        });
      } catch (e) { row.instModifyErr = String(e && e.message || e); }
    }
    if (extra) Object.assign(row, extra);
    row.after = inspect(c);
    return row;
  };

  if (u6) out.rows.push(await tryModify(u6, 'U6-RTC', NXP, 'MIMXRT1061DVJ6B'));
  if (usb1) {
    const other = (usb1.getState_OtherProperty && usb1.getState_OtherProperty()) || {};
    if (other['3D Model'] !== HIROSE) {
      out.rows.push(await tryModify(usb1, 'USB1', HIROSE, 'USB_C_Hirose_CX_4800304000_v3'));
    } else {
      out.rows.push({ label: 'USB1', already: inspect(usb1) });
    }
  }

  const again = await R.pcb_PrimitiveComponent.getAll();
  const reread = {};
  for (const c of again) {
    const des = c.getState_Designator && c.getState_Designator();
    if (des === 'U6-RTC' || des === 'USB1') reread[des] = inspect(c);
  }
  out.reread = reread;
  out.ok = reread['U6-RTC'] && (reread['U6-RTC'].model === NXP || (reread['U6-RTC'].model3d && reread['U6-RTC'].model3d.uuid === NXP));
  return out;
})()
