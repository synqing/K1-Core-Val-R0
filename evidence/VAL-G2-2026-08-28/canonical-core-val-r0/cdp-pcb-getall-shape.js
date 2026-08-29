(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const tab = '59bef7e87cff4cd580561703b62d8c19@' + PROJECT;
  try { await R.dmt_EditorControl.activateDocument(tab); } catch (e) {}
  await new Promise(r => setTimeout(r, 600));
  const raw = R.pcb_PrimitiveComponent.getAll();
  const out = {
    type: typeof raw,
    ctor: raw && raw.constructor && raw.constructor.name,
    isArray: Array.isArray(raw),
    keys: raw && typeof raw === 'object' ? Object.keys(raw).slice(0, 20) : null,
    proto: raw ? Object.getOwnPropertyNames(Object.getPrototypeOf(raw)).slice(0, 30) : null,
  };
  if (raw && typeof raw.then === 'function') {
    const v = await raw;
    out.awaitedType = typeof v;
    out.awaitedCtor = v && v.constructor && v.constructor.name;
    out.awaitedIsArray = Array.isArray(v);
    out.awaitedLen = Array.isArray(v) ? v.length : (v && v.length);
    if (Array.isArray(v) && v[0]) {
      out.firstMethods = Object.getOwnPropertyNames(Object.getPrototypeOf(v[0])).filter(k => /Designator|Supplier|Model|Name|Id|Other/i.test(k));
    }
  }
  try {
    const ids = R.pcb_PrimitiveComponent.getAllPrimitiveId();
    out.idsType = typeof ids;
    out.idsLen = ids && ids.length;
    out.idsSample = Array.isArray(ids) ? ids.slice(0, 8) : ids;
  } catch (e) { out.idsErr = String(e && e.message || e); }
  return out;
})()
