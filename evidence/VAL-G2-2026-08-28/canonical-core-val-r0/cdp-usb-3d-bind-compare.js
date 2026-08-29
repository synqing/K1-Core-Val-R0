(async () => {
  const R = window._EXTAPI_ROOT_;
  const TAB = '59bef7e87cff4cd580561703b62d8c19@64325d0e55e0435abd018defb0089a9b';
  try { await R.dmt_EditorControl.activateDocument(TAB); } catch (e) {}
  await new Promise(r => setTimeout(r, 400));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const pick = async (des) => {
    const c = comps.find(x => x.getState_Designator() === des);
    if (!c) return { des, missing: true };
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    const keys = [];
    let p = c;
    while (p && keys.length < 120) {
      for (const k of Object.getOwnPropertyNames(p)) {
        if (/3d|3D|model|Model|other|Other|foot|Foot|device|Device/i.test(k)) keys.push(k);
      }
      p = Object.getPrototypeOf(p);
    }
    let modelGet = null;
    try {
      const m = c.getState_Model3D && c.getState_Model3D();
      if (m && m.uuid) {
        modelGet = {
          personal: await R.lib_3DModel.get(m.uuid, '27700277ef7a49e48a0293bece6b2993').catch(e => String(e && e.message || e)),
          system: await R.lib_3DModel.get(m.uuid, m.libraryUuid).catch(e => String(e && e.message || e)),
          bare: await R.lib_3DModel.get(m.uuid).catch(e => String(e && e.message || e)),
        };
      }
    } catch (e) { modelGet = String(e && e.message || e); }
    return {
      des,
      id: c.getState_PrimitiveId(),
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      rot: c.getState_Rotation && c.getState_Rotation(),
      x: c.getState_X && c.getState_X(),
      y: c.getState_Y && c.getState_Y(),
      model3d: c.getState_Model3D && c.getState_Model3D(),
      transform: other['3D Model Transform'],
      model: other['3D Model'],
      title: other['3D Model Title'],
      footprint: c.getState_Footprint && c.getState_Footprint(),
      device: c.getState_Device && c.getState_Device(),
      otherKeys: Object.keys(other),
      methodish: [...new Set(keys)].slice(0, 80),
      modelGet,
    };
  };
  const usb1 = await pick('USB1');
  const usb2 = await pick('USB2');
  const u6 = await pick('U6-RTC');
  const source = await R.sys_FileManager.getDocumentSource();
  const libHits = {
    system: source.includes('0819f05c4eef4c71ace90d822a990e87'),
    personal: source.includes('27700277ef7a49e48a0293bece6b2993'),
    hirose: source.includes('71aa35b92da84360b5d9e21f25c486f0'),
  };
  return { usb1, usb2, u6, libHits, sourceLen: source.length };
})()
