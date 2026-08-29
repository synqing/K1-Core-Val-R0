(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const out = {};
  out.doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  if (!out.doc || out.doc.uuid !== PCB) {
    try { await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT); } catch (e) {}
    await new Promise(r => setTimeout(r, 800));
    out.doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  }

  let comps = [];
  try { comps = await R.pcb_PrimitiveComponent.getAll(); }
  catch (e) { out.getAllErr = String(e && e.message || e); }

  const rows = [];
  for (const c of comps || []) {
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    rows.push({
      des: c.getState_Designator && c.getState_Designator(),
      id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      fp: c.getState_Footprint && c.getState_Footprint(),
      model3d: c.getState_Model3D && c.getState_Model3D(),
      model: other['3D Model'],
      title: other['3D Model Title'],
      xf: other['3D Model Transform'],
    });
  }
  out.count = rows.length;
  out.usb = rows.filter(r => /USB|CX70|HYCW|C778726|C3034184|Hirose|TYPE-C/i.test(JSON.stringify(r)));
  out.designators = rows.map(r => r.des).filter(Boolean).sort();
  out.connectors = rows.filter(r => /USB|J\d|CON|CX|HYCW/i.test(String(r.des || '') + String(r.mid || '') + String(r.sid || '')));

  const source = await R.sys_FileManager.getDocumentSource();
  const buf = new TextEncoder().encode(source);
  const digest = await crypto.subtle.digest('SHA-256', buf);
  const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
  out.sourceHash = source.length + ':' + hex.slice(0, 8);
  const needles = ['USB1', 'USB2', 'C778726', 'CX70M', 'C3034184', 'HYCW78', '08b2bb7e', '0c8e199e', '19bbd06e', '0513051d', 'Hirose', 'TYPE-C'];
  out.needles = {};
  for (const n of needles) out.needles[n] = source.includes(n);
  out.usbLines = source.split('\n').filter(l => /USB1|USB2|C778726|CX70M|HYCW78|C3034184/.test(l)).slice(0, 10).map(l => l.slice(0, 400));
  return out;
})()
