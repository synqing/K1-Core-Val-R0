(async () => {
  const R = window._EXTAPI_ROOT_;
  const personal = '27700277ef7a49e48a0293bece6b2993';
  const dest = '7e7eac39cf44433b9710c4ae4afab424';
  const usbClass = {
    libraryUuid: personal,
    libraryType: '3',
    primaryClassificationUuid: '0c6123eef9994a71a80f19a1170c44f0',
    secondaryClassificationUuid: '4d4524b7560c4cd5a3bf20676566ece5',
  };
  const out = { searches: {} };
  const trySearch = async (label, fn) => {
    try { out.searches[label] = await fn(); }
    catch (e) { out.searches[label] = String(e && e.message || e); }
  };
  await trySearch('empty', () => R.lib_Device.search('', personal, undefined, 20, 1));
  await trySearch('CX70', () => R.lib_Device.search('CX70', personal, undefined, 20, 1));
  await trySearch('C778726', () => R.lib_Device.search('C778726', personal, undefined, 20, 1));
  await trySearch('HIROSE', () => R.lib_Device.search('HIROSE', personal, undefined, 20, 1));
  await trySearch('usbClass', () => R.lib_Device.search('CX70M-24P1', personal, usbClass, 20, 1));
  await trySearch('get', () => R.lib_Device.get(dest, personal));
  try {
    out.fileMgr = Object.getOwnPropertyNames(Object.getPrototypeOf(R.sys_FileManager)).filter(k => k !== 'constructor');
  } catch (e) { out.fileMgrErr = String(e && e.message || e); }

  const clickTitle = (want) => {
    const nodes = [...document.querySelectorAll('[title],button,[aria-label]')].filter(x => x.offsetParent !== null);
    const hit = nodes.find(x => String(x.getAttribute('title') || x.getAttribute('aria-label') || '') === want);
    if (!hit) return { ok: false, want };
    hit.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    return { ok: true, want };
  };
  out.click2d = clickTitle('2D Preview');
  return out;
})()
