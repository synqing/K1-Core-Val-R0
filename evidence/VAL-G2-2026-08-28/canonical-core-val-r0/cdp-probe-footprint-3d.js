(async () => {
  const R = window._EXTAPI_ROOT_;
  const personal = '27700277ef7a49e48a0293bece6b2993';
  const fp = '279f06324aa142578b6ff40a12f66d9b';
  const named = (obj, re) => {
    const out = [];
    if (!obj) return out;
    let proto = obj;
    const seen = new Set();
    while (proto && proto !== Object.prototype && out.length < 80) {
      for (const k of Object.getOwnPropertyNames(proto)) {
        if (seen.has(k)) continue;
        seen.add(k);
        if (re.test(k)) out.push(k);
      }
      proto = Object.getPrototypeOf(proto);
    }
    return out;
  };
  const out = {
    root3d: named(R, /3d|3D|Model|Footprint|lib_/i),
    fpGet: null,
  };
  try { out.fpGet = await R.lib_Footprint.get(fp, personal); } catch (e) { out.fpGetErr = String(e && e.message || e); }
  if (out.fpGet) {
    out.fpKeys = Object.keys(out.fpGet);
    const s = JSON.stringify(out.fpGet);
    out.fpHasModel = /model3|3D Model|3d/i.test(s);
    out.fpSnippet = s.slice(0, 2500);
  }
  try {
    const src = out.fpGet && (out.fpGet.source || out.fpGet.documentSource || out.fpGet.data);
    out.sourceType = typeof src;
    if (typeof src === 'string') {
      out.sourceHits = {
        model3D: (src.match(/model3D/g) || []).length,
        Model3D: (src.match(/Model3D/g) || []).length,
        '3D Model': (src.match(/3D Model/g) || []).length,
        ATTR: (src.match(/\"ATTR\"/g) || []).length,
      };
    }
  } catch (e) { out.srcErr = String(e && e.message || e); }
  return out;
})()
