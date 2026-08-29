(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  try { await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT); } catch (e) {}
  await new Promise(r => setTimeout(r, 400));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const u1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'U1');
  const pads = u1 && u1.getState_Pads && u1.getState_Pads();
  const nearby = [];
  if (u1) {
    const x = u1.getState_X();
    const y = u1.getState_Y();
    for (const c of comps) {
      const dx = (c.getState_X() || 0) - x;
      const dy = (c.getState_Y() || 0) - y;
      if (Math.hypot(dx, dy) < 800) {
        nearby.push({
          des: c.getState_Designator && c.getState_Designator(),
          id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
          mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
          sid: c.getState_SupplierId && c.getState_SupplierId(),
          x: c.getState_X && c.getState_X(),
          y: c.getState_Y && c.getState_Y(),
          fp: c.getState_Footprint && c.getState_Footprint() && c.getState_Footprint().name,
        });
      }
    }
  }
  const source = await R.sys_FileManager.getDocumentSource();
  const u1Lines = source.split('\n').filter(l => l.includes('0f194aaf30bc2e32') || l.includes('GT-USB-7005A') || l.includes('0e0bf75fdf55a316') || /"U1"/.test(l)).slice(0, 8).map(l => l.slice(0, 420));
  return {
    doc: await R.dmt_SelectControl.getCurrentDocumentInfo(),
    padCount: pads ? pads.length : 0,
    pads: (pads || []).map(p => ({ id: p.primitiveId, net: p.net, n: p.padNumber })),
    nearby: nearby.sort((a,b) => a.des.localeCompare(b.des)),
    u1Lines,
  };
})()
