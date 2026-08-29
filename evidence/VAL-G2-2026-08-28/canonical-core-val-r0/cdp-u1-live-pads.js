(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const TAB = PCB + '@' + PROJECT;
  const out = { ok: false };
  try { await R.dmt_EditorControl.activateDocument(TAB); } catch (e) { out.actErr = String(e && e.message || e); }
  await new Promise(r => setTimeout(r, 400));
  out.doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  out.project = await R.dmt_Project.getCurrentProjectInfo();
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const inspect = (c) => {
    if (!c) return null;
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    return {
      des: c.getState_Designator && c.getState_Designator(),
      id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      fp: c.getState_FootprintName && c.getState_FootprintName(),
      x: c.getState_X && c.getState_X(),
      y: c.getState_Y && c.getState_Y(),
      rot: c.getState_Rotation && c.getState_Rotation(),
      layer: c.getState_Layer && c.getState_Layer(),
      model: other['3D Model'],
      title: other['3D Model Title'],
      xf: other['3D Model Transform'],
      model3d: c.getState_Model3D && c.getState_Model3D(),
    };
  };
  const u1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'U1');
  out.u1 = inspect(u1);
  out.u6 = inspect(comps.find(c => c.getState_Designator && c.getState_Designator() === 'U6-RTC'));
  out.d1 = inspect(comps.find(c => c.getState_Designator && c.getState_Designator() === 'D1-PWR1'));
  out.usb2 = inspect(comps.find(c => {
    const d = c.getState_Designator && c.getState_Designator();
    return d === 'USB2' || d === 'U2' || (d && String(d).startsWith('USB'));
  }));
  const pads = await R.pcb_PrimitivePad.getAll();
  const ux = out.u1 && out.u1.x;
  const uy = out.u1 && out.u1.y;
  const near = [];
  for (const p of pads || []) {
    const x = p.getState_X && p.getState_X();
    const y = p.getState_Y && p.getState_Y();
    if (x == null || y == null || ux == null) continue;
    const dx = x - ux;
    const dy = y - uy;
    if (Math.hypot(dx, dy) > 700) continue;
    const other = (p.getState_OtherProperty && p.getState_OtherProperty()) || {};
    near.push({
      id: p.getState_PrimitiveId && p.getState_PrimitiveId(),
      n: (p.getState_Number && p.getState_Number()) || (p.getState_PadNumber && p.getState_PadNumber()) || other.number,
      net: p.getState_Net && p.getState_Net(),
      x, y,
      dx, dy,
      hole: p.getState_Hole && p.getState_Hole(),
      shape: p.getState_Shape && p.getState_Shape(),
      w: p.getState_Width && p.getState_Width(),
      h: p.getState_Height && p.getState_Height(),
      rot: p.getState_Rotation && p.getState_Rotation(),
      layer: p.getState_Layer && p.getState_Layer(),
    });
  }
  near.sort((a, b) => (b.y - a.y) || (a.x - b.x));
  out.padCountAll = (pads || []).length;
  out.padsNear = near;

  const lines = await R.pcb_PrimitiveLine.getAll();
  const outline = [];
  for (const ln of lines || []) {
    const layer = ln.getState_Layer && ln.getState_Layer();
    const x1 = ln.getState_X1 && ln.getState_X1();
    const y1 = ln.getState_Y1 && ln.getState_Y1();
    const x2 = ln.getState_X2 && ln.getState_X2();
    const y2 = ln.getState_Y2 && ln.getState_Y2();
    if (x1 == null) continue;
    const midX = (x1 + x2) / 2;
    const midY = (y1 + y2) / 2;
    if (Math.hypot(midX - ux, midY - uy) > 900) continue;
    outline.push({ layer, x1, y1, x2, y2 });
  }
  out.outlineNear = outline;

  const source = await R.sys_FileManager.getDocumentSource();
  let h = 2166136261;
  for (let i = 0; i < source.length; i++) {
    h ^= source.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  out.sourceHash = source.length + ':' + (h >>> 0).toString(16).padStart(8, '0');
  out.ok = !!(out.u1 && out.u1.sid === 'C5250872' && out.u1.mid === 'GT-USB-7005A');
  return out;
})()
