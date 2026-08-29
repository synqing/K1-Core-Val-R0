(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const SCH = '1435cb46f39e48c8a8aadbb84ca81603';
  const out = {};

  try { await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT); } catch (e) {}
  await new Promise(r => setTimeout(r, 400));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const u1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'U1');
  const other = u1 ? (u1.getState_OtherProperty() || {}) : {};
  out.u1 = u1 ? {
    des: u1.getState_Designator(),
    id: u1.getState_PrimitiveId(),
    sid: u1.getState_SupplierId(),
    mid: u1.getState_ManufacturerId(),
    x: u1.getState_X(),
    y: u1.getState_Y(),
    rot: u1.getState_Rotation(),
    component: u1.getState_Component && u1.getState_Component(),
    device: u1.getState_Device && u1.getState_Device(),
    footprint: u1.getState_Footprint && u1.getState_Footprint(),
    model3d: u1.getState_Model3D && u1.getState_Model3D(),
    model: other['3D Model'],
    title: other['3D Model Title'],
    xf: other['3D Model Transform'],
    otherKeys: Object.keys(other),
  } : { missing: true };

  const usbish = [];
  for (const c of comps) {
    const des = c.getState_Designator && c.getState_Designator();
    const mid = c.getState_ManufacturerId && c.getState_ManufacturerId();
    const sid = c.getState_SupplierId && c.getState_SupplierId();
    const fp = c.getState_Footprint && c.getState_Footprint();
    if (/USB|CX70|HYCW|7005|TYPE-C|Type-C|Hirose/i.test([des, mid, sid, fp && fp.name].join(' '))) {
      usbish.push({ des, id: c.getState_PrimitiveId && c.getState_PrimitiveId(), sid, mid, fp });
    }
  }
  out.pcbUsbish = usbish;

  try { out.boards = await R.dmt_Board.getAllBoardsInfo(); } catch (e) { out.boardsErr = String(e && e.message || e); }
  try { out.pcbs = await R.dmt_Pcb.getAllPcbsInfo(); } catch (e) { out.pcbsErr = String(e && e.message || e); }
  try { out.project = await R.dmt_Project.getCurrentProjectInfo(); } catch (e) { out.projectErr = String(e && e.message || e); }

  try { await R.dmt_EditorControl.activateDocument(SCH + '@' + PROJECT); } catch (e) {}
  await new Promise(r => setTimeout(r, 600));
  out.schDoc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  let schComps = [];
  try { schComps = await R.sch_PrimitiveComponent.getAll(); }
  catch (e) { out.schGetAllErr = String(e && e.message || e); }
  const schRows = [];
  for (const c of schComps || []) {
    const des = c.getState_Designator && c.getState_Designator();
    const name = c.getState_Name && c.getState_Name();
    const sid = c.getState_SupplierId && c.getState_SupplierId();
    const mid = c.getState_ManufacturerId && c.getState_ManufacturerId();
    if (/USB|CX70|HYCW|7005|C778726|C3034184|C5250872|U1$|USB1|USB2/i.test([des, name, sid, mid].join(' '))) {
      schRows.push({ des, name, sid, mid, id: c.getState_PrimitiveId && c.getState_PrimitiveId() });
    }
  }
  out.schUsbish = schRows;
  out.schCount = (schComps || []).length;
  try {
    const src = await R.sys_FileManager.getDocumentSource();
    out.schNeedles = {
      USB1: src.includes('USB1'), USB2: src.includes('USB2'), CX70M: src.includes('CX70M'),
      C778726: src.includes('C778726'), GTUSB: src.includes('GT-USB-7005A'), C5250872: src.includes('C5250872'),
    };
  } catch (e) { out.schSrcErr = String(e && e.message || e); }

  try { await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT); } catch (e) {}
  return out;
})()
