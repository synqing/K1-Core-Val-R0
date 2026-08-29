(async () => {
  const R = window._EXTAPI_ROOT_;
  const SCH = '1435cb46f39e48c8a8aadbb84ca81603@64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19@64325d0e55e0435abd018defb0089a9b';
  const NXP = 'de5664fd2ea74aa082831cfa5b198edb';
  const HIROSE = '71aa35b92da84360b5d9e21f25c486f0';

  const inspectPcb = (c) => {
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    return {
      des: c.getState_Designator && c.getState_Designator(),
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      model3d: c.getState_Model3D && c.getState_Model3D(),
      title: other['3D Model Title'],
      model: other['3D Model'],
    };
  };

  const inspectSch = (c) => ({
    id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
    des: c.getState_Designator && c.getState_Designator(),
    sub: c.getState_SubPartName && c.getState_SubPartName(),
    sid: c.getState_SupplierId && c.getState_SupplierId(),
    mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
    x: c.getState_X && c.getState_X(),
    y: c.getState_Y && c.getState_Y(),
    rot: c.getState_Rotation && c.getState_Rotation(),
  });

  try { await R.dmt_EditorControl.activateDocument(SCH); } catch (e) {}
  const schAll = await R.sch_PrimitiveComponent.getAll();
  const sch = [];
  for (const c of schAll) {
    const des = c.getState_Designator && c.getState_Designator();
    const sub = c.getState_SubPartName && c.getState_SubPartName();
    const mid = c.getState_ManufacturerId && c.getState_ManufacturerId();
    if (/U6-RTC|MIMXRT1062/i.test([des, sub, mid].join(' '))) sch.push(inspectSch(c));
  }

  try { await R.dmt_EditorControl.activateDocument(PCB); } catch (e) {}
  const pcbAll = await R.pcb_PrimitiveComponent.getAll();
  const pcb = [];
  for (const c of pcbAll) {
    const des = c.getState_Designator && c.getState_Designator();
    if (des === 'U6-RTC' || des === 'USB1') pcb.push(inspectPcb(c));
  }

  const u6 = pcb.find((r) => r.des === 'U6-RTC');
  return {
    schUnits: sch.length,
    sch,
    pcb,
    nxpOnU6: !!(u6 && (u6.model === NXP || (u6.model3d && u6.model3d.uuid === NXP))),
    hiroseUuid: HIROSE,
  };
})()
