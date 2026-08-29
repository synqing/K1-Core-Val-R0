(() => {
  const nodes = [...document.querySelectorAll('[title],button,[aria-label]')].filter(x => x.offsetParent !== null);
  const hit = nodes.find(x => String(x.getAttribute('title') || x.getAttribute('aria-label') || '') === '3D Preview')
    || nodes.find(x => String(x.getAttribute('title') || '') === '3D Model');
  if (!hit) return { ok: false, reason: '3D Preview not found' };
  const r = hit.getBoundingClientRect();
  hit.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  return { ok: true, title: hit.getAttribute('title') || hit.getAttribute('aria-label'), x: r.left + r.width / 2, y: r.top + r.height / 2 };
})()
