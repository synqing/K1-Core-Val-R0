(async () => {
  const R = window._EXTAPI_ROOT_;
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const SYSTEM = '0819f05c4eef4c71ace90d822a990e87';
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const out = {};
  const searches = [
    ['C778726', PERSONAL],
    ['CX70M', PERSONAL],
    ['USB-TYPE-C-SMD_CX70M', PERSONAL],
    ['C778726', SYSTEM],
    ['CX70M-24P1', SYSTEM],
    ['C778726', PROJECT],
  ];
  out.searches = [];
  for (const [q, lib] of searches) {
    try {
      const rows = await R.lib_Device.search(q, lib, undefined, 10, 1);
      out.searches.push({
        q, lib,
        n: (rows || []).length,
        rows: (rows || []).slice(0, 5).map(r => ({
          uuid: r.uuid, name: r.name, libraryUuid: r.libraryUuid,
          supplierId: r.supplierId, manufacturerId: r.manufacturerId,
          footprintUuid: r.footprintUuid, model3DUuid: r.model3DUuid,
          model3D: r.model3D, footprint: r.footprint,
        })),
      });
    } catch (e) {
      out.searches.push({ q, lib, err: String(e && e.message || e) });
    }
  }

  // USB1 primitive device accessors
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  try { await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT); } catch (e) {}
  await new Promise(r => setTimeout(r, 300));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const usb1 = comps.find(c => c.getState_Designator && c.getState_Designator() === 'USB1');
  const proto = usb1 ? Object.getOwnPropertyNames(Object.getPrototypeOf(usb1)).filter(k => /device|Device|foot|Foot|model|Model|Other/i.test(k)) : [];
  out.usb1Accessors = proto;
  if (usb1) {
    out.deviceRaw = usb1.getState_Device && usb1.getState_Device();
    out.component = usb1.getState_Component && usb1.getState_Component();
    out.other = usb1.getState_OtherProperty && usb1.getState_OtherProperty();
  }

  // Dialog still up?
  out.dialogText = [...document.querySelectorAll('[role="dialog"], .ant-modal, [class*="tips"]')]
    .filter(el => el.offsetParent !== null)
    .map(el => String(el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 200))
    .slice(0, 6);
  return out;
})()
