(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const FP = '0e0bf75fdf55a316';
  try { await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT); } catch (e) {}
  await new Promise(r => setTimeout(r, 500));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const u1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'U1');
  const cx = u1.getState_X();
  const cy = u1.getState_Y();
  const rot = u1.getState_Rotation();
  const rawPads = u1.getState_Pads && u1.getState_Pads();
  const padProto = rawPads && rawPads[0] ? Object.getOwnPropertyNames(Object.getPrototypeOf(rawPads[0])) : [];
  const padKeys = rawPads && rawPads[0] ? Object.keys(rawPads[0]) : [];
  let allPads = [];
  try { allPads = await R.pcb_PrimitivePad.getAll(); } catch (e) { allPads = { err: String(e && e.message || e) }; }
  const nearPads = Array.isArray(allPads) ? allPads.filter(p => {
    const x = p.getState_X && p.getState_X();
    const y = p.getState_Y && p.getState_Y();
    return typeof x === 'number' && Math.hypot(x - cx, y - cy) < 700;
  }).map(p => ({
    id: p.getState_PrimitiveId && p.getState_PrimitiveId(),
    n: p.getState_PadNumber && p.getState_PadNumber(),
    x: p.getState_X && p.getState_X(),
    y: p.getState_Y && p.getState_Y(),
    hole: p.getState_Hole && p.getState_Hole(),
    pad: p.getState_Pad && p.getState_Pad(),
    rot: p.getState_Rotation && p.getState_Rotation(),
    layer: p.getState_Layer && p.getState_Layer(),
  })) : [];
  let fp = null;
  try { fp = await R.lib_Footprint.get(FP); } catch (e) { fp = { err: String(e && e.message || e) }; }
  const fpKeys = fp && !fp.err ? Object.keys(fp) : [];
  let polys = [];
  try {
    const raw = await R.pcb_PrimitivePolyline.getAll();
    polys = (raw || []).filter(p => (p.getState_Layer && p.getState_Layer()) === 11).map(p => {
      const proto = Object.getOwnPropertyNames(Object.getPrototypeOf(p)).filter(k => /point|path|x|y|poly|coord/i.test(k));
      const out = { proto };
      for (const k of proto) {
        try { out[k] = typeof p[k] === 'function' ? p[k]() : p[k]; } catch (e) { out[k] = String(e && e.message || e); }
      }
      return out;
    });
  } catch (e) { polys = { err: String(e && e.message || e) }; }
  const source = await R.sys_FileManager.getDocumentSource();
  const buf = new TextEncoder().encode(source);
  const digest = await crypto.subtle.digest('SHA-256', buf);
  const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
  return {
    sourceHash: source.length + ':' + hex.slice(0, 8),
    u1: { cx, cy, rot, rawPadCount: rawPads ? rawPads.length : null, padProto, padKeys, sample: rawPads && rawPads[0] },
    allPadCount: Array.isArray(allPads) ? allPads.length : allPads,
    nearPads,
    fpKeys,
    fpName: fp && (fp.name || fp.title || fp.uuid),
    fpErr: fp && fp.err,
    outlinePolys: polys,
  };
})()
