(async () => {
  const R = window._EXTAPI_ROOT_;
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  try { await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT); } catch (e) {}
  await new Promise(r => setTimeout(r, 400));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const u1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'U1');
  if (!u1) return { err: 'no U1' };
  const ox = u1.getState_X();
  const oy = u1.getState_Y();
  const rot = u1.getState_Rotation && u1.getState_Rotation();
  let pads = [];
  try {
    pads = await R.pcb_PrimitivePad.getAll();
  } catch (e) {
    try { pads = u1.getState_Pads ? u1.getState_Pads() : []; } catch (e2) {}
  }
  const mine = [];
  for (const p of pads) {
    const owner = (p.getState_OwnerPrimitiveId && p.getState_OwnerPrimitiveId())
      || (p.getState_ComponentId && p.getState_ComponentId())
      || (p.getState_ParentId && p.getState_ParentId());
    const name = (p.getState_Name && p.getState_Name()) || (p.getState_PadNumber && p.getState_PadNumber());
    const x = p.getState_X && p.getState_X();
    const y = p.getState_Y && p.getState_Y();
    const shape = p.getState_Shape && p.getState_Shape();
    const hole = p.getState_Hole && p.getState_Hole();
    if (owner === u1.getState_PrimitiveId() || (name && String(name).match(/^[AB]?\d+$/))) {
      mine.push({ name, x, y, dx: x - ox, dy: y - oy, shape, hole, owner });
    }
  }
  const near = mine.filter(p => Math.hypot(p.dx, p.dy) < 400);
  near.sort((a,b) => a.dy - b.dy || a.dx - b.dx);
  return {
    u1: { id: u1.getState_PrimitiveId(), ox, oy, rot, sid: u1.getState_SupplierId(), mid: u1.getState_ManufacturerId() },
    padCount: pads.length,
    nearCount: near.length,
    near: near.slice(0, 40),
  };
})()
