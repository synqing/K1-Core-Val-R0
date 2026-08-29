(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const tab = '59bef7e87cff4cd580561703b62d8c19@' + PROJECT;
  const modelUuid = '71aa35b92da84360b5d9e21f25c486f0';
  const personal = '27700277ef7a49e48a0293bece6b2993';
  const out = {};
  try { await R.dmt_EditorControl.activateDocument(tab); } catch (e) { out.activateErr = String(e && e.message || e); }
  await new Promise(r => setTimeout(r, 400));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  out.compCount = comps.length;
  const hits = [];
  for (const c of comps) {
    const des = c.getState_Designator && c.getState_Designator();
    const sid = c.getState_SupplierId && c.getState_SupplierId();
    const mid = c.getState_ManufacturerId && c.getState_ManufacturerId();
    const name = c.getState_Name && c.getState_Name();
    const model3d = c.getState_Model3D && c.getState_Model3D();
    const other = c.getState_OtherProperty && c.getState_OtherProperty();
    const id = c.getState_PrimitiveId && c.getState_PrimitiveId();
    const blob = [des, sid, mid, name, JSON.stringify(other || {})].join(' ');
    if (/C778726|CX70M|USB|TYPE-C|Type-C|Hirose|4800304000/i.test(blob)) {
      hits.push({ id, des, sid, mid, name, model3d, other });
    }
  }
  out.hits = hits;
  out.bind = [];
  for (const t of hits) {
    const c = comps.find(x => (x.getState_PrimitiveId && x.getState_PrimitiveId()) === t.id);
    const row = { id: t.id, des: t.des };
    if (!c) { row.err = 'missing'; out.bind.push(row); continue; }
    const prev = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    try {
      c.setState_OtherProperty({
        ...prev,
        '3D Model': modelUuid,
        '3D Model Title': 'USB_C_Hirose_CX_4800304000_v3',
        '3D Model Transform': prev['3D Model Transform'] || '0, 0, 0, 0, 0, 0, 0, 0, 0',
      });
      row.setOther = true;
    } catch (e) { row.setOtherErr = String(e && e.message || e); }
    try {
      if (typeof c.modify === 'function') {
        row.modify = await c.modify({ model3D: { libraryUuid: personal, uuid: modelUuid, name: 'USB_C_Hirose_CX_4800304000_v3' } });
      }
    } catch (e) { row.modifyErr = String(e && e.message || e); }
    row.modelAfter = c.getState_Model3D && c.getState_Model3D();
    row.otherAfter = c.getState_OtherProperty && c.getState_OtherProperty();
    out.bind.push(row);
  }
  out.ok = out.bind.some(b => (b.modelAfter && b.modelAfter.uuid === modelUuid) || (b.otherAfter && b.otherAfter['3D Model'] === modelUuid));
  return out;
})()
