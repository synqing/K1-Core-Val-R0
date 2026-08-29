(async () => {
  const R = window._EXTAPI_ROOT_;
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const HIROSE = '71aa35b92da84360b5d9e21f25c486f0';
  const SYSTEM = '0819f05c4eef4c71ace90d822a990e87';
  const OFFICIAL = '4db9e6982d2c421c8c7ea67eaf304069';
  const TAB = '59bef7e87cff4cd580561703b62d8c19@64325d0e55e0435abd018defb0089a9b';
  const out = {};

  try { out.project = await R.dmt_Project.getCurrentProjectInfo(); } catch (e) { out.projectErr = String(e && e.message || e); }
  try { out.doc = await R.dmt_SelectControl.getCurrentDocumentInfo(); } catch (e) { out.docErr = String(e && e.message || e); }
  try { out.personalUuid = await R.lib_LibrariesList.getPersonalLibraryUuid(); } catch (e) { out.personalErr = String(e && e.message || e); }

  try { out.getClaimed = await R.lib_3DModel.get(HIROSE, PERSONAL); } catch (e) { out.getClaimedErr = String(e && e.message || e); }
  try { out.getClaimedNoLib = await R.lib_3DModel.get(HIROSE); } catch (e) { out.getClaimedNoLibErr = String(e && e.message || e); }
  try { out.searchHirose = await R.lib_3DModel.search('4800304000', PERSONAL, undefined, 20, 1); } catch (e) { out.searchHiroseErr = String(e && e.message || e); }
  try { out.searchUsbC = await R.lib_3DModel.search('USB_C_Hirose', PERSONAL, undefined, 20, 1); } catch (e) { out.searchUsbCErr = String(e && e.message || e); }
  try { out.searchUsb = await R.lib_3DModel.search('USB', PERSONAL, undefined, 20, 1); } catch (e) { out.searchUsbErr = String(e && e.message || e); }
  try { out.searchTypeC = await R.lib_3DModel.search('TYPE-C', PERSONAL, undefined, 20, 1); } catch (e) { out.searchTypeCErr = String(e && e.message || e); }

  try { out.officialDev = await R.lib_Device.get(OFFICIAL, SYSTEM); } catch (e) { out.officialDevErr = String(e && e.message || e); }
  try { out.personalCx = await R.lib_Device.search('CX70M-24P1', PERSONAL, undefined, undefined, 20, 1); } catch (e) { out.personalCxErr = String(e && e.message || e); }
  try { out.personalHiroseDev = await R.lib_Device.search('HIROSE', PERSONAL, undefined, undefined, 20, 1); } catch (e) { out.personalHiroseDevErr = String(e && e.message || e); }

  try { await R.dmt_EditorControl.activateDocument(TAB); } catch (e) { out.activateErr = String(e && e.message || e); }
  await new Promise(r => setTimeout(r, 400));

  const inspect = (c) => {
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    const keys = Object.keys(other).filter(k => /3[Dd]|Model|USB|C778|CX70|TYPE/i.test(k));
    const slim = {};
    for (const k of keys) slim[k] = other[k];
    return {
      id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
      des: c.getState_Designator && c.getState_Designator(),
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      name: c.getState_Name && c.getState_Name(),
      x: c.getState_X && c.getState_X(),
      y: c.getState_Y && c.getState_Y(),
      rot: c.getState_Rotation && c.getState_Rotation(),
      model3d: c.getState_Model3D && c.getState_Model3D(),
      other3d: slim,
      transform: other['3D Model Transform'],
      model: other['3D Model'],
      title: other['3D Model Title'],
    };
  };

  const comps = await R.pcb_PrimitiveComponent.getAll();
  out.compCount = comps.length;
  const usbRows = [];
  const siblingTypeC = [];
  for (const c of comps) {
    const row = inspect(c);
    if (row.des === 'USB1' || row.des === 'USB2') usbRows.push(row);
    const blob = JSON.stringify(row).toUpperCase();
    if (/TYPE-C|USB[_-]?C|C778726|CX70|TYPEC/.test(blob) && row.des !== 'USB1') {
      siblingTypeC.push(row);
    }
  }
  out.usbRows = usbRows;
  out.siblingTypeC = siblingTypeC.slice(0, 12);

  const transforms = {};
  for (const c of comps) {
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    const t = other['3D Model Transform'];
    const title = other['3D Model Title'] || '';
    if (!t) continue;
    if (/USB|TYPE|CX70|C778|CONN|BGA|1062|1061/i.test(title + ' ' + (c.getState_Designator && c.getState_Designator() || ''))) {
      transforms[c.getState_Designator && c.getState_Designator()] = {
        title,
        t,
        model: other['3D Model'],
        model3d: c.getState_Model3D && c.getState_Model3D(),
      };
    }
  }
  out.namedTransforms = transforms;

  return out;
})()
