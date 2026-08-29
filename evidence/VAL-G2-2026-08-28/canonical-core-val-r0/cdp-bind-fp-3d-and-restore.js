(async () => {
  const R = window._EXTAPI_ROOT_;
  const out = { titles: [] };
  try {
    const src = await R.sys_FileManager.getDocumentSource();
    out.srcType = typeof src;
    out.srcLen = typeof src === 'string' ? src.length : null;
    if (typeof src === 'string') {
      out.srcHits = {
        model3D: (src.match(/model3D/gi) || []).length,
        ATTR: (src.match(/\["ATTR"/g) || []).length,
      };
      out.srcInteresting = src.split('\n').filter(l => /3D|model|ATTR|COMPONENT/i.test(l)).slice(0, 30);
    }
  } catch (e) { out.srcErr = String(e && e.message || e); }

  const all = [...document.querySelectorAll('*')].filter(x => x.offsetParent !== null);
  out.threeD = all
    .map(x => ({ tag: x.tagName, title: x.getAttribute('title'), aria: x.getAttribute('aria-label'), text: String(x.textContent || '').trim().slice(0, 60) }))
    .filter(t => /3d|3D|Model Manager|模型/i.test([t.title, t.aria, t.text].join(' ')))
    .slice(0, 30);

  const click = (pred) => {
    const el = all.find(pred);
    if (!el) return false;
    el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    return true;
  };
  out.clickedModelBtn = click(x => String(x.getAttribute('title') || '') === '3D Model' || String(x.getAttribute('aria-label') || '') === '3D Model');

  return out;
})()
