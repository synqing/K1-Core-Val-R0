(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const SYSTEM = '0819f05c4eef4c71ace90d822a990e87';
  const SEATED = '08b2bb7ecebd47fc8f45f08f001d782e';
  const FP = '0c8e199e56e60728';
  const TAB = PCB + '@' + PROJECT;
  const out = { project: PROJECT, pcb: PCB };

  const hashOf = async (source) => {
    const buf = new TextEncoder().encode(source);
    const digest = await crypto.subtle.digest('SHA-256', buf);
    const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
    return source.length + ':' + hex.slice(0, 8);
  };

  try { await R.dmt_EditorControl.activateDocument(TAB); } catch (e) { out.activateErr = String(e && e.message || e); }
  await new Promise(r => setTimeout(r, 500));

  out.doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  out.projectInfo = await R.dmt_Project.getCurrentProjectInfo();
  const source = await R.sys_FileManager.getDocumentSource();
  out.sourceHash = await hashOf(source);
  out.sourceLen = source.length;
  out.hasSeated = source.includes(SEATED);
  out.hasOldHirose = source.includes('71aa35b92da84360b5d9e21f25c486f0');
  out.hasFp = source.includes(FP);
  out.hasUsb2Model = source.includes('0513051d44a0486b835661f1b78cdeb9');

  const comps = await R.pcb_PrimitiveComponent.getAll();
  const pick = (des) => {
    const c = comps.find(x => x.getState_Designator && x.getState_Designator() === des);
    if (!c) return { des, missing: true };
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    return {
      des,
      id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      x: c.getState_X && c.getState_X(),
      y: c.getState_Y && c.getState_Y(),
      rot: c.getState_Rotation && c.getState_Rotation(),
      model3d: c.getState_Model3D && c.getState_Model3D(),
      transform: other['3D Model Transform'],
      model: other['3D Model'],
      title: other['3D Model Title'],
      footprint: c.getState_Footprint && c.getState_Footprint(),
      device: c.getState_Device && c.getState_Device(),
    };
  };
  out.usb1 = pick('USB1');
  out.usb2 = pick('USB2');
  out.u6 = pick('U6-RTC');

  try { out.fpGetPersonal = await R.lib_Footprint.get(FP, PERSONAL); }
  catch (e) { out.fpGetPersonalErr = String(e && e.message || e); }
  try { out.fpGetProject = await R.lib_Footprint.get(FP, PROJECT); }
  catch (e) { out.fpGetProjectErr = String(e && e.message || e); }
  try { out.fpGetSystem = await R.lib_Footprint.get(FP, SYSTEM); }
  catch (e) { out.fpGetSystemErr = String(e && e.message || e); }

  const usb2Fp = out.usb2 && out.usb2.footprint && out.usb2.footprint.uuid;
  if (usb2Fp) {
    try { out.usb2FpGetPersonal = await R.lib_Footprint.get(usb2Fp, PERSONAL); }
    catch (e) { out.usb2FpGetPersonalErr = String(e && e.message || e); }
    try { out.usb2FpGetProject = await R.lib_Footprint.get(usb2Fp, PROJECT); }
    catch (e) { out.usb2FpGetProjectErr = String(e && e.message || e); }
    try { out.usb2FpGetSystem = await R.lib_Footprint.get(usb2Fp, SYSTEM); }
    catch (e) { out.usb2FpGetSystemErr = String(e && e.message || e); }
  }

  try { out.seatedModel = await R.lib_3DModel.get(SEATED, PERSONAL); }
  catch (e) { out.seatedModelErr = String(e && e.message || e); }
  try { out.seatedModelSystem = await R.lib_3DModel.get(SEATED, SYSTEM); }
  catch (e) { out.seatedModelSystemErr = String(e && e.message || e); }

  try {
    const fps = await R.sys_FileManager.getDocumentFootprintSources();
    out.fpSourcesCount = Array.isArray(fps) ? fps.length : null;
    out.fpSourcesIds = Array.isArray(fps) ? fps.map(x => x && x.footprintUuid).slice(0, 20) : null;
    const hit = Array.isArray(fps) ? fps.find(x => x && x.footprintUuid === FP) : null;
    if (hit && hit.documentSource) {
      out.usb1FpSourceHash = await hashOf(hit.documentSource);
      out.usb1FpSourceHas3D = /3D Model/.test(hit.documentSource);
      out.usb1FpSourceHasSeated = hit.documentSource.includes(SEATED);
      out.usb1FpSourceHead = hit.documentSource.slice(0, 400);
    }
  } catch (e) { out.fpSourcesErr = String(e && e.message || e); }

  const fileMeta = async (fpUuid, lib) => {
    try {
      const f = await R.sys_FileManager.getFootprintFileByFootprintUuid(fpUuid, lib, 'elibz2');
      if (!f) return { ok: false, lib, empty: true };
      return { ok: true, lib, name: f.name, size: f.size, type: f.type };
    } catch (e) {
      return { ok: false, lib, err: String(e && e.message || e) };
    }
  };
  out.usb1FpFilePersonal = await fileMeta(FP, PERSONAL);
  out.usb1FpFileProject = await fileMeta(FP, PROJECT);
  if (usb2Fp) {
    out.usb2FpFilePersonal = await fileMeta(usb2Fp, PERSONAL);
    out.usb2FpFileProject = await fileMeta(usb2Fp, PROJECT);
    out.usb2FpFileSystem = await fileMeta(usb2Fp, SYSTEM);
  }

  try {
    const tabs = await R.dmt_EditorControl.getAllEditorTabsInfo();
    out.tabs = (tabs || []).map(t => ({
      tabId: t.tabId || t.id,
      uuid: t.uuid,
      name: t.name || t.title,
      documentType: t.documentType,
      parentProjectUuid: t.parentProjectUuid,
    }));
  } catch (e) { out.tabsErr = String(e && e.message || e); }

  out.identityOk = out.usb1 && out.usb1.sid === 'C778726' && out.usb1.mid === 'CX70M-24P1'
    && out.usb1.footprint && out.usb1.footprint.uuid === FP;
  return out;
})()
