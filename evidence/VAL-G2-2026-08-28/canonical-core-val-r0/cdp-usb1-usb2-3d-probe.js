(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const SYSTEM = '0819f05c4eef4c71ace90d822a990e87';
  const TAB = PCB + '@' + PROJECT;
  const out = { project: PROJECT, pcb: PCB };

  try { await R.dmt_EditorControl.activateDocument(TAB); } catch (e) { out.activateErr = String(e && e.message || e); }
  await new Promise(r => setTimeout(r, 400));

  out.apiEditor = Object.keys(R.dmt_EditorControl || {}).sort();

  const source = await R.sys_FileManager.getDocumentSource();
  const crypto = window.crypto || self.crypto;
  const buf = new TextEncoder().encode(source);
  const digest = await crypto.subtle.digest('SHA-256', buf);
  const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
  out.sourceHash = source.length + ':' + hex.slice(0, 8);
  out.sourceLen = source.length;
  out.hasHirose = source.includes('71aa35b92da84360b5d9e21f25c486f0');
  out.hasFootprintNote = source.includes('0c8e199e56e60728');

  const comps = await R.pcb_PrimitiveComponent.getAll();
  const pick = async (des) => {
    const c = comps.find(x => x.getState_Designator && x.getState_Designator() === des);
    if (!c) return { des, missing: true };
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    const device = c.getState_Device && c.getState_Device();
    const footprint = c.getState_Footprint && c.getState_Footprint();
    const model3d = c.getState_Model3D && c.getState_Model3D();
    const row = {
      des,
      id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      name: c.getState_Name && c.getState_Name(),
      x: c.getState_X && c.getState_X(),
      y: c.getState_Y && c.getState_Y(),
      rot: c.getState_Rotation && c.getState_Rotation(),
      model3d,
      transform: other['3D Model Transform'],
      model: other['3D Model'],
      title: other['3D Model Title'],
      device,
      footprint,
      otherKeys: Object.keys(other),
    };
    if (device && device.uuid) {
      try { row.deviceGetPersonal = await R.lib_Device.get(device.uuid, device.libraryUuid || PERSONAL); }
      catch (e) { row.deviceGetPersonalErr = String(e && e.message || e); }
      try { row.deviceGetSystem = await R.lib_Device.get(device.uuid, SYSTEM); }
      catch (e) { row.deviceGetSystemErr = String(e && e.message || e); }
    }
    if (footprint && footprint.uuid) {
      try { row.fpGet = await R.lib_Footprint.get(footprint.uuid, footprint.libraryUuid || PERSONAL); }
      catch (e) { row.fpGetErr = String(e && e.message || e); }
      try { row.fpGetPersonal = await R.lib_Footprint.get(footprint.uuid, PERSONAL); }
      catch (e) { row.fpGetPersonalErr = String(e && e.message || e); }
    }
    if (model3d && model3d.uuid) {
      try { row.modelGet = await R.lib_3DModel.get(model3d.uuid, model3d.libraryUuid || PERSONAL); }
      catch (e) { row.modelGetErr = String(e && e.message || e); }
    }
    return row;
  };

  out.usb1 = await pick('USB1');
  out.usb2 = await pick('USB2');
  out.u6 = await pick('U6');
  if (out.u6.missing) out.u6rtc = await pick('U6-RTC');

  try { out.personal3d = await R.lib_3DModel.search('USB_C_Hirose', PERSONAL, undefined, 10, 1); }
  catch (e) { out.personal3dErr = String(e && e.message || e); }
  try { out.personalCx = await R.lib_Device.search('CX70M-24P1', PERSONAL, undefined, 10, 1); }
  catch (e) { out.personalCxErr = String(e && e.message || e); }

  const apiKeys = [];
  for (const k of Object.keys(R || {})) {
    if (/3d|3D|model|Model|foot|Foot/i.test(k)) apiKeys.push(k);
  }
  out.apiKeys = apiKeys.sort();
  return out;
})()
