(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const ORIG = '7e3f17b4e5b64384aaa03075cd65e3e3';
  const YFLIP = 'e6946995a72f4deaa7b036359e4ff6e7';
  try { await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT); } catch (e) {}
  await new Promise(r => setTimeout(r, 400));
  const inspect = (c) => {
    if (!c) return null;
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    return {
      des: c.getState_Designator && c.getState_Designator(),
      id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      model: other['3D Model'],
      title: other['3D Model Title'],
      xf: other['3D Model Transform'],
      model3d: c.getState_Model3D && c.getState_Model3D(),
    };
  };
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const getModel = async (uuid) => {
    const out = { uuid };
    try { out.personal = await R.lib_3DModel.get(uuid, PERSONAL); }
    catch (e) { out.personalErr = String(e && e.message || e); }
    try { out.bare = await R.lib_3DModel.get(uuid); }
    catch (e) { out.bareErr = String(e && e.message || e); }
    return out;
  };
  const source = await R.sys_FileManager.getDocumentSource();
  const buf = new TextEncoder().encode(source);
  const digest = await crypto.subtle.digest('SHA-256', buf);
  const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
  return {
    ok: true,
    sourceHash: source.length + ':' + hex.slice(0, 8),
    doc: await R.dmt_SelectControl.getCurrentDocumentInfo(),
    u1: inspect(comps.find(c => c.getState_Designator && c.getState_Designator() === 'U1')),
    u6: inspect(comps.find(c => c.getState_Designator && c.getState_Designator() === 'U6-RTC')),
    d1: inspect(comps.find(c => c.getState_Designator && c.getState_Designator() === 'D1-PWR1')),
    usb2: inspect(comps.find(c => c.getState_Designator && c.getState_Designator() === 'USB2')),
    original: await getModel(ORIG),
    yflip: await getModel(YFLIP),
  };
})()
