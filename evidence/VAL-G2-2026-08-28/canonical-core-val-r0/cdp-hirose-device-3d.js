(async () => {
  const R = window._EXTAPI_ROOT_;
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const OFFICIAL = '4db9e6982d2c421c8c7ea67eaf304069';
  const out = {};
  try { out.personalDev = await R.lib_Device.get('7e7eac39cf44433b9710c4ae4afab424', PERSONAL); } catch (e) { out.personalDev = String(e && e.message || e); }
  try { out.official = await R.lib_Device.get(OFFICIAL); } catch (e) { out.official = String(e && e.message || e); }
  try { out.lcsc = await R.lib_Device.getByLcscIds('C778726'); } catch (e) { out.lcsc = String(e && e.message || e); }
  try {
    const s = await R.lib_3DModel.search('TYPE-C', '0819f05c4eef4c71ace90d822a990e87', undefined, 8, 1);
    out.systemTypeC = (s || []).map(x => ({ uuid: x.uuid, name: x.name, libraryUuid: x.libraryUuid }));
  } catch (e) { out.systemTypeC = String(e && e.message || e); }
  try {
    const s = await R.lib_Device.search('USB-C', undefined, undefined, undefined, 8, 1);
    out.devSearch = (s || []).slice(0, 8).map(x => ({
      uuid: x.uuid, name: x.name, lcsc: x.lcscPartNumber || x.supplierId,
      libraryUuid: x.libraryUuid, has3d: !!(x.model3D || x.model3d),
    }));
  } catch (e) { out.devSearch = String(e && e.message || e); }
  const slim = (d) => {
    if (!d || typeof d !== 'object') return d;
    const keys = Object.keys(d);
    const modelish = {};
    for (const k of keys) {
      if (/3d|3D|model|Model|transform|Transform|foot|Foot|lcsc|LCSC|name|uuid|title/i.test(k)) {
        modelish[k] = d[k];
      }
    }
    return { keys: keys.slice(0, 60), modelish };
  };
  return {
    personalSlim: slim(out.personalDev),
    officialSlim: slim(out.official),
    lcscType: Array.isArray(out.lcsc) ? out.lcsc.slice(0, 3).map(slim) : slim(out.lcsc),
    systemTypeC: out.systemTypeC,
    devSearch: out.devSearch,
  };
})()
