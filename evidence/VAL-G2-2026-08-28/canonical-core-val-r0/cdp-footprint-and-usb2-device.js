(async () => {
  const R = window._EXTAPI_ROOT_;
  const slim = (d) => {
    if (!d || typeof d !== 'object') return d;
    const out = { keys: Object.keys(d) };
    for (const k of out.keys) {
      if (/3d|3D|model|transform|assoc|property|foot|uuid|name|lcsc/i.test(k)) out[k] = d[k];
    }
    return out;
  };
  const fp = {};
  try { fp.project = await R.lib_Footprint.get('0c8e199e56e60728', '64325d0e55e0435abd018defb0089a9b'); } catch (e) { fp.project = String(e && e.message || e); }
  try { fp.official = await R.lib_Footprint.get('44616f94c6914e79972b7923414e99c1'); } catch (e) { fp.official = String(e && e.message || e); }
  let usb2dev = null;
  try { usb2dev = await R.lib_Device.getByLcscIds('C3034184'); } catch (e) { usb2dev = String(e && e.message || e); }
  let personal = null;
  try { personal = await R.lib_Device.get('7e7eac39cf44433b9710c4ae4afab424', '27700277ef7a49e48a0293bece6b2993'); } catch (e) { personal = String(e && e.message || e); }
  const assoc = personal && personal.association;
  const prop = personal && personal.property;
  return {
    fpProject: slim(fp.project),
    fpOfficial: slim(fp.official),
    usb2dev: Array.isArray(usb2dev) ? usb2dev.map(slim) : slim(usb2dev),
    personalAssoc: assoc,
    personalProp: prop,
    personalKeys: personal && Object.keys(personal),
  };
})()
