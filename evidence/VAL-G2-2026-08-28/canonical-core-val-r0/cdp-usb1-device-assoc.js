(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const FP = '0c8e199e56e60728';
  const SEATED = '08b2bb7ecebd47fc8f45f08f001d782e';
  const TITLE = 'USB_C_Hirose_CX_4800304000_seated';
  const DEV = 'cdbd0653120da16e';
  const out = {};

  // Live USB1 device from the PCB instance, not a guessed UUID.
  try { await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT); } catch (e) {}
  await new Promise(r => setTimeout(r, 400));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const usb1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'USB1');
  const usb2 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'USB2');
  const u6 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'U6-RTC');
  const inspect = (c) => {
    if (!c) return null;
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    return {
      des: c.getState_Designator(),
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      device: c.getState_Device && c.getState_Device(),
      footprint: c.getState_Footprint && c.getState_Footprint(),
      model3d: c.getState_Model3D && c.getState_Model3D(),
      model: other['3D Model'],
      transform: other['3D Model Transform'],
    };
  };
  out.usb1 = inspect(usb1);
  out.usb2 = inspect(usb2);
  out.u6 = inspect(u6);
  if (!out.usb1 || out.usb1.sid !== 'C778726' || out.usb1.mid !== 'CX70M-24P1') {
    return { ok: false, err: 'identity', usb1: out.usb1 };
  }
  const deviceUuid = (out.usb1.device && out.usb1.device.uuid) || DEV;
  const deviceLib = (out.usb1.device && out.usb1.device.libraryUuid) || PROJECT;

  const getDev = async (uuid, lib) => {
    try { return { lib, item: await R.lib_Device.get(uuid, lib) }; }
    catch (e) { return { lib, err: String(e && e.message || e) }; }
  };
  out.devProject = await getDev(deviceUuid, PROJECT);
  out.devPersonal = await getDev(deviceUuid, PERSONAL);
  out.devGuess = await getDev(DEV, PERSONAL);
  out.devGuessProj = await getDev(DEV, PROJECT);

  try { out.searchCx = await R.lib_Device.search('CX70M-24P1', PERSONAL, undefined, 10, 1); }
  catch (e) { out.searchCxErr = String(e && e.message || e); }
  try { out.searchCxProj = await R.lib_Device.search('CX70M-24P1', PROJECT, undefined, 10, 1); }
  catch (e) { out.searchCxProjErr = String(e && e.message || e); }

  out.modifySrc = String(R.lib_Device.modify).slice(0, 800);
  return out;
})()
