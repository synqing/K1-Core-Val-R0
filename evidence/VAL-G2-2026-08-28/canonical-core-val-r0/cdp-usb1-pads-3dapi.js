(async () => {
  const R = window._EXTAPI_ROOT_;
  const TAB = '59bef7e87cff4cd580561703b62d8c19@64325d0e55e0435abd018defb0089a9b';
  try { await R.dmt_EditorControl.activateDocument(TAB); } catch (e) {}
  await new Promise(r => setTimeout(r, 300));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const usb1 = comps.find(c => c.getState_Designator() === 'USB1');
  const usb2 = comps.find(c => c.getState_Designator() === 'USB2');
  const padsOf = (c) => {
    const pads = (c.getState_Pads && c.getState_Pads()) || [];
    return pads.map(p => ({
      n: p.getState_PadNumber && p.getState_PadNumber(),
      x: p.getState_X && p.getState_X(),
      y: p.getState_Y && p.getState_Y(),
      hole: p.getState_Hole && p.getState_Hole(),
      shape: p.getState_Shape && p.getState_Shape(),
      w: p.getState_Width && p.getState_Width(),
      h: p.getState_Height && p.getState_Height(),
    }));
  };
  const proto = (obj) => obj ? Object.getOwnPropertyNames(Object.getPrototypeOf(obj)).sort() : [];
  return {
    usb1: {
      x: usb1.getState_X(), y: usb1.getState_Y(), rot: usb1.getState_Rotation(),
      pads: padsOf(usb1),
    },
    usb2: {
      x: usb2.getState_X(), y: usb2.getState_Y(), rot: usb2.getState_Rotation(),
    },
    api: Object.keys(R).sort(),
    lib3d: proto(R.lib_3DModel),
    libFp: proto(R.lib_Footprint),
    pcbComp: proto(R.pcb_PrimitiveComponent).filter(k => /3d|3D|model|Model|modif|Other|Foot/i.test(k)),
    fileMgr: proto(R.sys_FileManager).filter(k => /3d|3D|foot|Foot|source|Source/i.test(k)),
  };
})()
