(async () => {
  const R = window._EXTAPI_ROOT_;
  const out = {};
  try {
    const src = await R.sys_FileManager.getDocumentSource();
    out.srcType = typeof src;
    out.srcLen = typeof src === 'string' ? src.length : (src && JSON.stringify(src).length);
    const text = typeof src === 'string' ? src : JSON.stringify(src || {});
    out.hits = {
      model3D: (text.match(/model3D/gi) || []).length,
      ATTR: (text.match(/\["ATTR"/g) || []).length,
      threeD: (text.match(/3D/g) || []).length,
      COMPONENT: (text.match(/\["COMPONENT"/g) || []).length,
    };
    out.interesting = text.split('\n').filter(l => /3D|model|MODEL|Height|ATTR/i.test(l)).slice(0, 50);
    out.head = text.slice(0, 600);
  } catch (e) {
    out.srcErr = String(e);
  }

  const nodes = [...document.querySelectorAll('[title],button,[aria-label]')].filter(x => x.offsetParent !== null);
  const btn = nodes.find(x => String(x.getAttribute('title') || x.getAttribute('aria-label') || '') === '3D Model');
  if (btn) {
    btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    out.clicked3dModel = true;
  } else {
    out.clicked3dModel = false;
    out.titles = nodes.map(x => x.getAttribute('title') || x.getAttribute('aria-label')).filter(Boolean).slice(0, 40);
  }
  return out;
})()
