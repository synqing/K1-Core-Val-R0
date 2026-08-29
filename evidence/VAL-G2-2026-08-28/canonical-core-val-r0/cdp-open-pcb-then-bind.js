(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const SYSTEM = '0819f05c4eef4c71ace90d822a990e87';
  const USB1_ID = '19bbd06e9438ab5d';
  const USB1_FP = '0c8e199e56e60728';
  const USB1_DEV = 'cdbd0653120da16e';
  const SEATED = '08b2bb7ecebd47fc8f45f08f001d782e';
  const out = { steps: [] };
  const note = (label, extra) => { out.steps.push({ label, ...extra }); };

  out.beforeDoc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  out.editorKeys = Object.keys(R.dmt_EditorControl || {}).sort();
  out.fileKeys = Object.keys(R.sys_FileManager || {}).sort();

  let tab;
  try {
    tab = await R.dmt_EditorControl.openDocument(PCB);
    note('openDocument-pcb', { tab });
  } catch (e) {
    note('openDocument-pcb', { err: String(e && e.message || e) });
  }
  try {
    await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT);
    note('activate-pcb-tab', { ok: true });
  } catch (e) {
    note('activate-pcb-tab', { err: String(e && e.message || e) });
  }
  await new Promise(r => setTimeout(r, 1200));
  out.doc = await R.dmt_SelectControl.getCurrentDocumentInfo();

  if (!out.doc || out.doc.uuid !== PCB) {
    try {
      const tabs = await R.dmt_EditorControl.getAllOpenedDocumentsInfo();
      out.opened = tabs;
      note('opened-docs', { count: Array.isArray(tabs) ? tabs.length : 0 });
    } catch (e) {
      note('opened-docs', { err: String(e && e.message || e) });
    }
  }

  const hashOf = async () => {
    const source = await R.sys_FileManager.getDocumentSource();
    const buf = new TextEncoder().encode(source);
    const digest = await crypto.subtle.digest('SHA-256', buf);
    const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
    return { sourceHash: source.length + ':' + hex.slice(0, 8), sourceLen: source.length, source };
  };

  let hashed;
  try { hashed = await hashOf(); } catch (e) { out.hashErr = String(e && e.message || e); }
  if (hashed) {
    out.sourceHash = hashed.sourceHash;
    out.sourceLen = hashed.sourceLen;
    const source = hashed.source;
    out.hasSeated = source.includes(SEATED);
    out.hasOld = source.includes('71aa35b92da84360b5d9e21f25c486f0');
    out.hasUsb2Model = source.includes('0513051d44a0486b835661f1b78cdeb9');
    out.hasUsb1Fp = source.includes(USB1_FP);
    out.hasUsb1InstFp = source.includes(PCB + '_' + USB1_ID);
    out.hasUsb1Id = source.includes(USB1_ID);
    const grab = (needle) => source.split('\n').filter(l => l.includes(needle)).slice(0, 6).map(l => l.slice(0, 360));
    out.usb1IdLines = grab(USB1_ID);
    out.usb2DesLines = grab('"USB2"');
    out.model3dLines = source.split('\n').filter(l => /"model3D"|"3D Model"/.test(l)).slice(0, 8).map(l => l.slice(0, 360));
  }

  const tryGet = async (ids) => {
    try { return { ok: true, items: await R.pcb_PrimitiveComponent.get(ids) }; }
    catch (e) { return { ok: false, err: String(e && e.message || e) }; }
  };
  out.getUsb1 = await tryGet([USB1_ID]);
  out.getUsb2 = await tryGet(['001a257400b89df6']);

  const slimComp = (c) => {
    if (!c) return null;
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    return {
      id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
      des: c.getState_Designator && c.getState_Designator(),
      sid: c.getState_SupplierId && c.getState_SupplierId(),
      mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
      x: c.getState_X && c.getState_X(),
      y: c.getState_Y && c.getState_Y(),
      rot: c.getState_Rotation && c.getState_Rotation(),
      component: c.getState_Component && c.getState_Component(),
      device: c.getState_Device && c.getState_Device(),
      footprint: c.getState_Footprint && c.getState_Footprint(),
      model3d: c.getState_Model3D && c.getState_Model3D(),
      model: other['3D Model'],
      title: other['3D Model Title'],
      transform: other['3D Model Transform'],
    };
  };
  if (out.getUsb1.ok) out.usb1 = slimComp(Array.isArray(out.getUsb1.items) ? out.getUsb1.items[0] : out.getUsb1.items);
  if (out.getUsb2.ok) out.usb2 = slimComp(Array.isArray(out.getUsb2.items) ? out.getUsb2.items[0] : out.getUsb2.items);
  delete out.getUsb1.items;
  delete out.getUsb2.items;

  const getDev = async (label, uuid, lib) => {
    try {
      const item = await R.lib_Device.get(uuid, lib);
      if (!item) return { label, lib, empty: true };
      return {
        label, lib,
        uuid: item.uuid, name: item.name, libraryUuid: item.libraryUuid,
        association: item.association,
        propertyKeys: item.property ? Object.keys(item.property) : [],
        other3d: item.property && item.property.otherProperty
          ? Object.fromEntries(Object.entries(item.property.otherProperty).filter(([k]) => /3D|model|Model|Footprint/.test(k)))
          : null,
      };
    } catch (e) { return { label, lib, err: String(e && e.message || e) }; }
  };
  out.usb1DevProject = await getDev('usb1-project', USB1_DEV, PROJECT);
  out.usb1DevPersonal = await getDev('usb1-personal', USB1_DEV, PERSONAL);
  out.usb2DevProject = await getDev('usb2-project', '98dfb99cf775e204', PROJECT);

  const getFp = async (label, uuid, lib) => {
    try {
      const item = await R.lib_Footprint.get(uuid, lib);
      if (!item) return { label, lib, empty: true };
      return {
        label, lib,
        uuid: item.uuid, name: item.name, libraryUuid: item.libraryUuid, libraryType: item.libraryType,
        keys: Object.keys(item),
        model3D: item.model3D || item.model3d || null,
        association: item.association || null,
      };
    } catch (e) { return { label, lib, err: String(e && e.message || e) }; }
  };
  out.usb1FpProject = await getFp('usb1-fp-project', USB1_FP, PROJECT);
  out.usb1FpPersonal = await getFp('usb1-fp-personal', USB1_FP, PERSONAL);
  out.usb1InstFp = await getFp('usb1-inst-fp', PCB + '_' + USB1_ID, PROJECT);
  out.usb2FpProject = await getFp('usb2-fp-project', PCB + '_001a257400b89df6', PROJECT);
  out.usb2FpPersonal = await getFp('usb2-fp-personal', PCB + '_001a257400b89df6', PERSONAL);

  const getModel = async (label, uuid, lib) => {
    try {
      const item = await R.lib_3DModel.get(uuid, lib);
      return item ? { label, lib, uuid: item.uuid, name: item.name, libraryUuid: item.libraryUuid, desc: item.description } : { label, lib, empty: true };
    } catch (e) { return { label, lib, err: String(e && e.message || e) }; }
  };
  out.seatedPersonal = await getModel('seated-personal', SEATED, PERSONAL);
  out.seatedSystem = await getModel('seated-system', SEATED, SYSTEM);
  out.seatedProject = await getModel('seated-project', SEATED, PROJECT);
  out.usb2ModelSystem = await getModel('usb2-system', '0513051d44a0486b835661f1b78cdeb9', SYSTEM);

  out.api = {
    lib_Device: Object.keys(R.lib_Device || {}).sort(),
    lib_Footprint: Object.keys(R.lib_Footprint || {}).sort(),
    lib_3DModel: Object.keys(R.lib_3DModel || {}).sort(),
    extra: Object.keys(R || {}).filter(k => /3d|3D|model|Model|foot|Foot|device|Device/i.test(k)).sort(),
  };
  return out;
})()
