(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  try { await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT); } catch (e) {}
  await new Promise(r => setTimeout(r, 400));
  const doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const u1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'U1');
  if (!u1) return { ok: false, err: 'no U1' };
  const other = (u1.getState_OtherProperty && u1.getState_OtherProperty()) || {};
  const cx = u1.getState_X();
  const cy = u1.getState_Y();
  const rot = u1.getState_Rotation ? u1.getState_Rotation() : null;
  const layer = u1.getState_Layer ? u1.getState_Layer() : null;
  const padRefs = (u1.getState_Pads && u1.getState_Pads()) || [];
  const ids = padRefs.map(p => p.primitiveId || p.id).filter(Boolean);
  let padObjs = [];
  try { padObjs = await R.pcb_PrimitivePad.get(ids); } catch (e) { padObjs = []; }
  const rad = (-(rot || 0) * Math.PI) / 180;
  const cos = Math.cos(rad);
  const sin = Math.sin(rad);
  const pads = (padObjs || []).map((p, i) => {
    const x = p.getState_X ? p.getState_X() : null;
    const y = p.getState_Y ? p.getState_Y() : null;
    const dx = x - cx;
    const dy = y - cy;
    return {
      id: p.getState_PrimitiveId ? p.getState_PrimitiveId() : ids[i],
      n: p.getState_PadNumber ? p.getState_PadNumber() : (padRefs[i] && padRefs[i].padNumber),
      net: p.getState_Net ? p.getState_Net() : (padRefs[i] && padRefs[i].net),
      x,
      y,
      localX: dx * cos - dy * sin,
      localY: dx * sin + dy * cos,
      hole: p.getState_Hole ? p.getState_Hole() : null,
      holeRot: p.getState_HoleRotation ? p.getState_HoleRotation() : null,
      shape: p.getState_Pad ? p.getState_Pad() : (p.getState_Shape ? p.getState_Shape() : null),
      rot: p.getState_Rotation ? p.getState_Rotation() : null,
    };
  });
  pads.sort((a, b) => (a.localY - b.localY) || (a.localX - b.localX));

  const board = {};
  try {
    const regions = await R.pcb_PrimitiveRegion.getAll();
    board.regions = (regions || []).map(r => ({
      name: r.getState_RegionName && r.getState_RegionName(),
      type: r.getState_RuleType && r.getState_RuleType(),
      poly: r.getState_ComplexPolygon && r.getState_ComplexPolygon(),
    })).slice(0, 20);
  } catch (e) { board.regionErr = String(e && e.message || e); }
  try {
    const lines = await R.pcb_PrimitiveLine.getAll();
    const outline = (lines || []).filter(l => {
      const layerId = l.getState_Layer && l.getState_Layer();
      return layerId === 10 || layerId === 11 || layerId === 'BOARD_OUTLINE' || layerId === 12;
    }).slice(0, 40).map(l => ({
      layer: l.getState_Layer && l.getState_Layer(),
      x1: l.getState_StartX ? l.getState_StartX() : (l.getState_X && l.getState_X()),
      y1: l.getState_StartY ? l.getState_StartY() : (l.getState_Y && l.getState_Y()),
      x2: l.getState_EndX && l.getState_EndX(),
      y2: l.getState_EndY && l.getState_EndY(),
    }));
    board.outlineSample = outline;
    board.lineCount = (lines || []).length;
  } catch (e) { board.lineErr = String(e && e.message || e); }
  try {
    const polys = await R.pcb_PrimitivePolyline.getAll();
    board.polylines = (polys || []).slice(0, 15).map(p => ({
      layer: p.getState_Layer && p.getState_Layer(),
      name: p.getState_Name && p.getState_Name(),
      pts: p.getState_Points ? p.getState_Points() : (p.getState_Path && p.getState_Path()),
    }));
  } catch (e) { board.polyErr = String(e && e.message || e); }

  const source = await R.sys_FileManager.getDocumentSource();
  const buf = new TextEncoder().encode(source);
  const digest = await crypto.subtle.digest('SHA-256', buf);
  const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');

  const inspect = (c) => {
    if (!c) return null;
    const o = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    return {
      des: c.getState_Designator && c.getState_Designator(),
      id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      x: c.getState_X && c.getState_X(),
      y: c.getState_Y && c.getState_Y(),
      rot: c.getState_Rotation && c.getState_Rotation(),
      model: o['3D Model'],
      title: o['3D Model Title'],
      xf: o['3D Model Transform'],
    };
  };

  return {
    ok: true,
    doc,
    sourceHash: source.length + ':' + hex.slice(0, 8),
    u1: {
      id: u1.getState_PrimitiveId && u1.getState_PrimitiveId(),
      sid: u1.getState_SupplierId && u1.getState_SupplierId(),
      mid: u1.getState_ManufacturerId && u1.getState_ManufacturerId(),
      x: cx,
      y: cy,
      rot,
      layer,
      model: other['3D Model'],
      title: other['3D Model Title'],
      xf: other['3D Model Transform'],
      model3d: u1.getState_Model3D && u1.getState_Model3D(),
      padCount: pads.length,
    },
    pads,
    others: {
      u6: inspect(comps.find(c => c.getState_Designator && c.getState_Designator() === 'U6-RTC')),
      d1: inspect(comps.find(c => c.getState_Designator && c.getState_Designator() === 'D1-PWR1')),
    },
    board,
  };
})()
