(async () => {
  const R = window._EXTAPI_ROOT_;
  const personal = '27700277ef7a49e48a0293bece6b2993';
  const dest = '7e7eac39cf44433b9710c4ae4afab424';
  const modelUuid = '71aa35b92da84360b5d9e21f25c486f0';
  const official = '4db9e6982d2c421c8c7ea67eaf304069';
  const system = '0819f05c4eef4c71ace90d822a990e87';
  const out = {};

  try {
    out.usbClass = await R.lib_Classification.getIndexByName(personal, '3', 'Connectors', 'USB Connectors');
  } catch (e) { out.usbClassErr = String(e && e.message || e); }

  if (out.usbClass) {
    try {
      out.reclass = await R.lib_Device.modify(dest, personal, undefined, out.usbClass);
    } catch (e) { out.reclassErr = String(e && e.message || e); }
  }

  try {
    out.modelReclass = await R.lib_3DModel.modify(
      modelUuid, personal, undefined,
      { libraryUuid: personal, libraryType: '5', primaryClassificationUuid: 'dcfcb5e86e39474a9511e7c34cacd3d1' },
    );
  } catch (e) { out.modelReclassErr = String(e && e.message || e); }

  try { out.device = await R.lib_Device.get(dest, personal); } catch (e) { out.deviceErr = String(e && e.message || e); }
  try { out.model = await R.lib_3DModel.get(modelUuid, personal); } catch (e) { out.modelErr = String(e && e.message || e); }
  try { out.search = await R.lib_Device.search('CX70M-24P1', personal, undefined, 10, 1); } catch (e) { out.searchErr = String(e && e.message || e); }
  try { out.official = await R.lib_Device.get(official, system); } catch (e) { out.officialErr = String(e && e.message || e); }
  try { out.search3d = await R.lib_3DModel.search('USB_C_Hirose', personal, undefined, 5, 1); } catch (e) { out.search3dErr = String(e && e.message || e); }

  const other = out.device && out.device.property && out.device.property.otherProperty;
  out.ok = !!(other && other['3D Model'] === modelUuid && other['3D Model Title']);
  return {
    ok: out.ok,
    usbClass: out.usbClass,
    reclass: out.reclass,
    reclassErr: out.reclassErr,
    modelReclass: out.modelReclass,
    modelReclassErr: out.modelReclassErr,
    classification: out.device && out.device.classification,
    other3d: other && {
      model: other['3D Model'],
      title: other['3D Model Title'],
      transform: other['3D Model Transform'],
      supplier: other['Supplier Part'],
      mpn: other['Manufacturer Part'],
    },
    search: out.search,
    official3d: out.official && out.official.property && out.official.property.otherProperty && {
      model: out.official.property.otherProperty['3D Model'],
      title: out.official.property.otherProperty['3D Model Title'],
    },
    model: out.model && { uuid: out.model.uuid, name: out.model.name, classification: out.model.classification },
    search3d: out.search3d,
  };
})()
