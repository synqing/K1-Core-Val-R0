(async () => {
  const R = window._EXTAPI_ROOT_;
  const personal = '27700277ef7a49e48a0293bece6b2993';
  const system = '0819f05c4eef4c71ace90d822a990e87';
  const deviceUuid = '4db9e6982d2c421c8c7ea67eaf304069';
  const out = { ok: true };
  try { out.device = await R.lib_Device.get(deviceUuid, system); } catch (e) { out.deviceErr = String(e && e.message || e); }
  try { out.search3dHirose = await R.lib_3DModel.search('Hirose', personal, undefined, 20, 1); } catch (e) { out.search3dHiroseErr = String(e && e.message || e); }
  try { out.search3dUsb = await R.lib_3DModel.search('USB', personal, undefined, 20, 1); } catch (e) { out.search3dUsbErr = String(e && e.message || e); }
  try { out.search3dCx = await R.lib_3DModel.search('CX70', personal, undefined, 20, 1); } catch (e) { out.search3dCxErr = String(e && e.message || e); }
  try { out.search3d4800 = await R.lib_3DModel.search('4800304000', personal, undefined, 20, 1); } catch (e) { out.search3d4800Err = String(e && e.message || e); }
  try { out.classif = await R.lib_Classification.getList(personal); } catch (e) {
    out.classifErr = String(e && e.message || e);
    out.classifKeys = R.lib_Classification ? Object.getOwnPropertyNames(Object.getPrototypeOf(R.lib_Classification)) : null;
  }
  const named = (obj) => obj ? Object.getOwnPropertyNames(Object.getPrototypeOf(obj)).filter(k => k !== 'constructor') : null;
  out.footprintMethods = named(R.lib_Footprint);
  out.classifMethods = named(R.lib_Classification);
  try {
    const comps = typeof R.pcb_PrimitiveComponent?.getAll === 'function' ? R.pcb_PrimitiveComponent.getAll() : null;
    out.compCount = Array.isArray(comps) ? comps.length : null;
    if (Array.isArray(comps)) {
      const hits = [];
      for (const c of comps) {
        const sid = c.getState_SupplierId && c.getState_SupplierId();
        const mid = c.getState_ManufacturerId && c.getState_ManufacturerId();
        const des = c.getState_Designator && c.getState_Designator();
        const name = c.getState_Name && c.getState_Name();
        if (/C778726|CX70M|USB/i.test(String(sid||'') + String(mid||'') + String(des||'') + String(name||''))) {
          let model3d;
          try { model3d = c.getState_Model3D && c.getState_Model3D(); } catch (e) { model3d = String(e && e.message || e); }
          hits.push({ id: c.getId ? c.getId() : undefined, des, sid, mid, name, model3d });
        }
      }
      out.usbHits = hits;
    }
  } catch (e) { out.pcbErr = String(e && e.message || e); }
  return out;
})()
