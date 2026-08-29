(async () => {
  const R = window._EXTAPI_ROOT_;
  const TAB = '59bef7e87cff4cd580561703b62d8c19@64325d0e55e0435abd018defb0089a9b';
  try { await R.dmt_EditorControl.activateDocument(TAB); } catch (e) {}
  await new Promise(r => setTimeout(r, 300));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const c = comps.find(x => (x.getState_Designator && x.getState_Designator()) === 'USB1');
  if (!c) return { ok: false, err: 'no USB1' };
  const id = c.getState_PrimitiveId();
  const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
  let pads = [];
  try {
    const raw = await R.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(id);
    pads = (raw || []).map(p => ({
      num: p.getState_PadNumber && p.getState_PadNumber(),
      name: p.getState_Name && p.getState_Name(),
      x: p.getState_X && p.getState_X(),
      y: p.getState_Y && p.getState_Y(),
      w: p.getState_Width && p.getState_Width(),
      h: p.getState_Height && p.getState_Height(),
      hole: p.getState_HoleWidth && p.getState_HoleWidth(),
      holeH: p.getState_HoleHeight && p.getState_HoleHeight(),
      type: p.getState_PadType && p.getState_PadType(),
    }));
  } catch (e) {
    pads = { err: String(e && e.message || e) };
  }
  return {
    ok: true,
    id,
    des: c.getState_Designator(),
    sid: c.getState_SupplierId && c.getState_SupplierId(),
    mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
    x: c.getState_X && c.getState_X(),
    y: c.getState_Y && c.getState_Y(),
    rot: c.getState_Rotation && c.getState_Rotation(),
    model3d: c.getState_Model3D && c.getState_Model3D(),
    transform: other['3D Model Transform'],
    model: other['3D Model'],
    title: other['3D Model Title'],
    padCount: Array.isArray(pads) ? pads.length : 0,
    pads,
  };
})()
