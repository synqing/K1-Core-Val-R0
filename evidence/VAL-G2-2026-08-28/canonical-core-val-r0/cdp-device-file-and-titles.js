(async () => {
  const R = window._EXTAPI_ROOT_;
  const personal = '27700277ef7a49e48a0293bece6b2993';
  const dest = '7e7eac39cf44433b9710c4ae4afab424';
  const out = {};
  try { out.listed = await R.lib_Device.search('', personal, undefined, 5, 1); } catch (e) { out.listedErr = String(e && e.message || e); }
  if (Array.isArray(out.listed) && out.listed[0]) {
    const d = out.listed[0];
    out.listItem = {
      uuid: d.uuid,
      name: d.name,
      keys: Object.keys(d),
      model3D: d.model3D,
      model3DUuid: d.model3DUuid,
      model3DName: d.model3DName,
      supplierId: d.supplierId,
      manufacturerId: d.manufacturerId,
    };
  }
  try {
    const file = await R.sys_FileManager.getDeviceFileByDeviceUuid(dest, personal);
    out.fileType = file && file.constructor && file.constructor.name;
    out.fileName = file && file.name;
    out.fileSize = file && file.size;
    if (file && typeof file.text === 'function') {
      const text = await file.text();
      out.fileLen = text.length;
      out.fileHits = {
        model3D: (text.match(/model3D/gi) || []).length,
        hirose: (text.match(/Hirose|4800304000|71aa35b9/g) || []).length,
      };
      const idx = text.search(/model3D|3D Model|71aa35b9|4800304000/i);
      out.fileAround = idx >= 0 ? text.slice(Math.max(0, idx - 120), idx + 240) : text.slice(0, 400);
    }
  } catch (e) { out.fileErr = String(e && e.message || e); }

  const titles = [...document.querySelectorAll('[title],button,[aria-label]')]
    .filter(x => x.offsetParent !== null)
    .map(x => ({
      title: x.getAttribute('title'),
      aria: x.getAttribute('aria-label'),
      text: String(x.textContent || '').trim().slice(0, 40),
    }))
    .filter(t => t.title || t.aria || /3d|2d|preview|model/i.test(t.text));
  out.visible3d = titles.slice(0, 50);
  return out;
})()
