(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const LIB = '0819f05c4eef4c71ace90d822a990e87';
  const YFLIP = 'e6946995a72f4deaa7b036359e4ff6e7';
  const TITLE = 'J1_GT-USB-7005A_yflip';
  const XF = '0, 74.803, 0, 0, 0, 0, 0, 0, 0';
  const TAB = PCB + '@' + PROJECT;
  const out = {};
  const doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  const already = doc && doc.uuid === PCB && doc.documentType === 3;
  if (!already) {
    try { await R.dmt_EditorControl.activateDocument(TAB); } catch (e) { out.actErr = String(e && e.message || e); }
    await new Promise(r => setTimeout(r, 400));
  }
  const inspect = (c) => {
    if (!c) return { missing: true };
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    return {
      des: c.getState_Designator && c.getState_Designator(),
      id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      model: other['3D Model'],
      title: other['3D Model Title'],
      xf: other['3D Model Transform'],
      model3d: c.getState_Model3D && c.getState_Model3D(),
    };
  };
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const u1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'U1');
  const u6 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'U6-RTC');
  const d1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'D1-PWR1');
  out.before = { u1: inspect(u1), u6: inspect(u6), d1: inspect(d1) };
  if (!u1 || u1.getState_SupplierId() !== 'C5250872' || u1.getState_ManufacturerId() !== 'GT-USB-7005A') {
    out.ok = false;
    out.err = 'U1 identity mismatch';
    return out;
  }
  const prev = (u1.getState_OtherProperty && u1.getState_OtherProperty()) || {};
  try {
    out.modify = await R.pcb_PrimitiveComponent.modify(u1, {
      otherProperty: {
        ...prev,
        '3D Model': YFLIP,
        '3D Model Title': TITLE,
        '3D Model Transform': XF,
      },
      model3D: { libraryUuid: LIB, uuid: YFLIP, name: TITLE },
    });
  } catch (e) {
    out.modifyErr = String(e && e.message || e);
    out.modify = await R.pcb_PrimitiveComponent.modify(u1, {
      otherProperty: {
        ...prev,
        '3D Model': YFLIP,
        '3D Model Title': TITLE,
        '3D Model Transform': XF,
      },
    });
  }
  try { out.saved = await R.pcb_Document.save(PCB); } catch (e) { out.saveErr = String(e && e.message || e); }
  await new Promise(r => setTimeout(r, 400));
  const again = await R.pcb_PrimitiveComponent.getAll();
  out.after = {
    u1: inspect(again.find(c => c.getState_Designator && c.getState_Designator() === 'U1')),
    u6: inspect(again.find(c => c.getState_Designator && c.getState_Designator() === 'U6-RTC')),
    d1: inspect(again.find(c => c.getState_Designator && c.getState_Designator() === 'D1-PWR1')),
  };
  const source = await R.sys_FileManager.getDocumentSource();
  const buf = new TextEncoder().encode(source);
  const digest = await crypto.subtle.digest('SHA-256', buf);
  const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
  out.sourceHash = source.length + ':' + hex.slice(0, 8);
  out.ok = out.after.u1.model === YFLIP
    && out.after.u1.xf === XF
    && out.after.u6.model === out.before.u6.model
    && out.after.u6.xf === out.before.u6.xf
    && out.after.d1.model === out.before.d1.model
    && out.after.d1.xf === out.before.d1.xf
    && out.after.u1.sid === 'C5250872';
  return out;
})()
