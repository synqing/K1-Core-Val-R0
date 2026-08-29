(() => {
  const all = [...document.querySelectorAll('li')].filter(x => x.offsetParent !== null);
  const hit = all.find(x => String(x.textContent || '').trim() === 'Personal');
  if (!hit) return { ok: false, texts: all.map(x => String(x.textContent||'').trim()).filter(Boolean).slice(0, 40) };
  const r = hit.getBoundingClientRect();
  hit.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  return { ok: true, x: r.left, y: r.top, w: r.width, h: r.height };
})()
