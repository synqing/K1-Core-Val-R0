(() => {
  const all = [...document.querySelectorAll('*')].filter(x => x.offsetParent !== null);
  const hit = all.find(x => String(x.textContent || '').trim() === 'Click to Preview 3D')
    || all.find(x => x.tagName === 'BUTTON' && String(x.textContent || '').trim() === '3D');
  if (!hit) return { ok: false, reason: 'preview control not found' };
  const r = hit.getBoundingClientRect();
  hit.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  return { ok: true, tag: hit.tagName, text: String(hit.textContent || '').trim().slice(0, 40), x: r.left, y: r.top, w: r.width, h: r.height };
})()
