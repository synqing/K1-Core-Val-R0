(async () => {
  const R = window._EXTAPI_ROOT_ || window.eda || window.EDA;
  if (!R) return { ok: false, reason: 'no EDA root', keys: Object.keys(window).filter(k => /eda|EXTAPI/i.test(k)).slice(0, 30) };
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
  const libs = {};
  try { libs.personal = await R.lib_LibrariesList.getPersonalLibraryUuid(); } catch (e) { libs.personalErr = String(e && e.message || e); }
  try { libs.project = await R.lib_LibrariesList.getProjectLibraryUuid(); } catch (e) { libs.projectErr = String(e && e.message || e); }
  try { libs.favorite = await R.lib_LibrariesList.getFavoriteLibraryUuid(); } catch (e) { libs.favoriteErr = String(e && e.message || e); }
  try { libs.system = await R.lib_LibrariesList.getSystemLibraryUuid(); } catch (e) { libs.systemErr = String(e && e.message || e); }
  const unit = R.esys_Unit || R.ESYS_Unit || null;
  return {
    ok: true,
    rootKeys3d: named(R, /3d|3D|Model|lib_/i).slice(0, 60),
    hasLib3D: !!R.lib_3DModel,
    lib3DMethods: named(R.lib_3DModel, /./),
    libDeviceMethods: named(R.lib_Device, /copy|modify|get|create|search|lcsc/i),
    pcbComp3d: named(R.pcb_PrimitiveComponent, /Model|3d|3D|Footprint|Component/i),
    libs,
    unitKeys: unit ? Object.keys(unit) : null,
    unitMm: unit && (unit.MILLIMETER || unit.mm || null),
  };
})()
