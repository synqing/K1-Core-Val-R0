(async () => {
  const R = window._EXTAPI_ROOT_;
  const tab = '59bef7e87cff4cd580561703b62d8c19@64325d0e55e0435abd018defb0089a9b';
  try { await R.dmt_EditorControl.activateDocument(tab); } catch (e) {}
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const modelUuid = 'de5664fd2ea74aa082831cfa5b198edb';
  const hits = [];
  for (const c of comps) {
    const des = c.getState_Designator && c.getState_Designator();
    const sid = c.getState_SupplierId && c.getState_SupplierId();
    const mid = c.getState_ManufacturerId && c.getState_ManufacturerId();
    if (!/U6|RT1062|C3216699|MIMXRT1062/i.test([des, sid, mid].join(' '))) continue;
    hits.push({
      des, sid, mid,
      model3d: c.getState_Model3D && c.getState_Model3D(),
      title: (c.getState_OtherProperty && c.getState_OtherProperty() || {})['3D Model Title'],
    });
  }
  const targets = hits.filter(h => /U6/i.test(String(h.des || '')) || /C3216699|MIMXRT1062/i.test(String(h.sid || '') + String(h.mid || '')));
  const bound = [];
  for (const c of comps) {
    const des = c.getState_Designator && c.getState_Designator();
    const sid = c.getState_SupplierId && c.getState_SupplierId();
    const mid = c.getState_ManufacturerId && c.getState_ManufacturerId();
    const isU6 = /^U6(-RTC)?$/i.test(String(des || '')) || /C3216699/.test(String(sid || '')) || /MIMXRT1062DVJ6B/.test(String(mid || ''));
    if (!isU6) continue;
    const prev = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    c.setState_OtherProperty({
      ...prev,
      '3D Model': modelUuid,
      '3D Model Title': 'MIMXRT1061DVJ6B',
      '3D Model Transform': prev['3D Model Transform'] || '0, 0, 0, 0, 0, 0, 0, 0, 0',
    });
    const other = c.getState_OtherProperty() || {};
    bound.push({
      des, sid, mid,
      model: other['3D Model'],
      title: other['3D Model Title'],
      model3d: c.getState_Model3D && c.getState_Model3D(),
    });
  }
  return { ok: bound.some(b => b.model === modelUuid), hits, bound };
})()
