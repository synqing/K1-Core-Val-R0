(async () => {
  const R = window._EXTAPI_ROOT_;
  const named = (obj) => obj ? Object.getOwnPropertyNames(Object.getPrototypeOf(obj)).filter(k => k !== 'constructor') : null;
  const out = { pcbMethods: named(R.pcb_PrimitiveComponent), selectMethods: named(R.pcb_SelectControl) };
  const candidates = ['getAll', 'getAllComponents', 'getComponents', 'getPrimitives', 'getPrimitiveList', 'query'];
  for (const k of candidates) {
    out['has_' + k] = typeof (R.pcb_PrimitiveComponent && R.pcb_PrimitiveComponent[k]) === 'function';
  }
  try {
    const src = await R.sys_FileManager.getDocumentSource();
    out.srcType = typeof src;
    out.srcLen = typeof src === 'string' ? src.length : null;
    if (typeof src === 'string') {
      out.hits = {
        C778726: (src.match(/C778726/g) || []).length,
        CX70M: (src.match(/CX70M/g) || []).length,
        USB: (src.match(/USB-TYPE-C|USB_C|Type-C/g) || []).length,
        model3D: (src.match(/model3D|3D Model/g) || []).length,
      };
      const lines = src.split('\n');
      out.usbcLines = lines.filter(l => /C778726|CX70M|USB-TYPE-C|USB\?|USB1|USB2/i.test(l)).slice(0, 30);
    }
  } catch (e) { out.srcErr = String(e && e.message || e); }
  return out;
})()
