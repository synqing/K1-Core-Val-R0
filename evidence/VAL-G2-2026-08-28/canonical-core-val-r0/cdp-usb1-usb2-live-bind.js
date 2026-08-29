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
  const out = { project: PROJECT, pcb: PCB };

  try { await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT); } catch (e) {
    out.activateErr = String(e && e.message || e);
  }
  await new Promise(r => setTimeout(r, 500));
  out.doc = await R.dmt_SelectControl.getCurrentDocumentInfo();

  const source = await R.sys_FileManager.getDocumentSource();
  const buf = new TextEncoder().encode(source);
  const digest = await crypto.subtle.digest('SHA-256', buf);
  const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
  out.sourceHash = source.length + ':' + hex.slice(0, 8);
  out.sourceLen = source.length;

  const pickSource = (des) => {
    const lines = source.split('\n');
    const hits = [];
    for (const line of lines) {
      if (line.includes('"' + des + '"') || (des === 'USB1' && (line.includes(USB1_ID) || line.includes(USB1_FP) || line.includes(SEATED)))) {
        if (/COMPONENT|ATTR|model3D|3D Model|FOOTPRINT|DEVICE/i.test(line)) {
          hits.push(line.slice(0, 420));
        }
      }
    }
    return hits.slice(0, 12);
  };
  out.usb1SourceHits = pickSource('USB1');
  out.usb2SourceHits = pickSource('USB2');
  out.hasSeated = source.includes(SEATED);
  out.hasOld = source.includes('71aa35b92da84360b5d9e21f25c486f0');
  out.hasUsb2Model = source.includes('0513051d44a0486b835661f1b78cdeb9');
  out.hasUsb1Fp = source.includes(USB1_FP);
  out.hasUsb1InstFp = source.includes(PCB + '_' + USB1_ID);

  const comps = await R.pcb_PrimitiveComponent.getAll();
  const row = async (des) => {
    const c = comps.find(x => x.getState_Designator && x.getState_Designator() === des);
    if (!c) return { des, missing: true };
    const other = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
    const keys = Object.getOwnPropertyNames(c).concat(Object.getOwnPropertyNames(Object.getPrototypeOf(c) || {}));
    const modelMethods = keys.filter(k => /model|Model|3[Dd]|foot|Foot|comp|Comp|device|Device/.test(k)).sort();
    return {
      des,
      id: c.getState_PrimitiveId && c.getState_PrimitiveId(),
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
      other3d: Object.fromEntries(Object.entries(other).filter(([k]) => /3D|model|Model|Footprint|Device/.test(k))),
      modelMethods,
    };
  };
  out.usb1 = await row('USB1');
  out.usb2 = await row('USB2');
  out.u6 = await row('U6-RTC');

  const getDev = async (label, uuid, lib) => {
    try { return { label, lib, item: await R.lib_Device.get(uuid, lib) }; }
    catch (e) { return { label, lib, err: String(e && e.message || e), raw: e && (e.message || e.toString || JSON.stringify(e)) }; }
  };
  out.usb1DevProject = await getDev('usb1-project', USB1_DEV, PROJECT);
  out.usb1DevPersonal = await getDev('usb1-personal', USB1_DEV, PERSONAL);
  if (out.usb2.component && out.usb2.component.uuid) {
    out.usb2DevProject = await getDev('usb2-project', out.usb2.component.uuid, out.usb2.component.libraryUuid || PROJECT);
  }

  const getFp = async (label, uuid, lib) => {
    try {
      const item = await R.lib_Footprint.get(uuid, lib);
      const keys = item ? Object.keys(item) : [];
      const slim = item ? {
        uuid: item.uuid, name: item.name, libraryUuid: item.libraryUuid, libraryType: item.libraryType,
        description: item.description, keys,
        model3D: item.model3D || item.model3d || item.association,
        other: item.otherProperty || item.property || null,
      } : null;
      return { label, lib, slim };
    } catch (e) {
      return { label, lib, err: String(e && e.message || e) };
    }
  };
  out.usb1FpProject = await getFp('usb1-fp-project', USB1_FP, PROJECT);
  out.usb1FpPersonal = await getFp('usb1-fp-personal', USB1_FP, PERSONAL);
  out.usb1InstFp = await getFp('usb1-inst-fp', PCB + '_' + USB1_ID, PROJECT);
  if (out.usb2.footprint && out.usb2.footprint.uuid) {
    out.usb2FpProject = await getFp('usb2-fp-project', out.usb2.footprint.uuid, out.usb2.footprint.libraryUuid || PROJECT);
    out.usb2FpPersonal = await getFp('usb2-fp-personal', out.usb2.footprint.uuid, PERSONAL);
  }

  const getModel = async (label, uuid, lib) => {
    try {
      const item = await R.lib_3DModel.get(uuid, lib);
      return { label, lib, uuid: item && item.uuid, name: item && item.name, libraryUuid: item && item.libraryUuid, desc: item && item.description };
    } catch (e) {
      return { label, lib, err: String(e && e.message || e) };
    }
  };
  out.seatedPersonal = await getModel('seated-personal', SEATED, PERSONAL);
  out.seatedSystem = await getModel('seated-system', SEATED, SYSTEM);
  out.seatedProject = await getModel('seated-project', SEATED, PROJECT);
  if (out.usb2.model) {
    out.usb2ModelSystem = await getModel('usb2-system', out.usb2.model, SYSTEM);
    out.usb2ModelPersonal = await getModel('usb2-personal', out.usb2.model, PERSONAL);
  }

  out.api = {
    lib_Device: Object.keys(R.lib_Device || {}).sort(),
    lib_Footprint: Object.keys(R.lib_Footprint || {}).sort(),
    lib_3DModel: Object.keys(R.lib_3DModel || {}).sort(),
    pcb_Primitive: Object.keys(R.pcb_Primitive || {}).sort(),
    pcb_Document: Object.keys(R.pcb_Document || {}).sort(),
    extra: Object.keys(R || {}).filter(k => /3d|3D|model|Model|foot|Foot|device|Device/i.test(k)).sort(),
  };

  try {
    out.usb2File = await R.sys_FileManager.getFootprintFileByFootprintUuid(out.usb2.footprint.uuid, PROJECT, 'elibz2');
    if (out.usb2File) out.usb2File = { name: out.usb2File.name, size: out.usb2File.size, type: out.usb2File.type };
  } catch (e) { out.usb2FileErr = String(e && e.message || e); }
  try {
    out.usb1File = await R.sys_FileManager.getFootprintFileByFootprintUuid(USB1_FP, PROJECT, 'elibz2');
    if (out.usb1File) out.usb1File = { name: out.usb1File.name, size: out.usb1File.size, type: out.usb1File.type };
  } catch (e) { out.usb1FileErr = String(e && e.message || e); }

  return out;
})()
