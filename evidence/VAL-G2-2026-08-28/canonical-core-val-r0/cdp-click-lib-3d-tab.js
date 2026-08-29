(() => {
  const all = [...document.querySelectorAll('li,button,span,div')].filter(x => x.offsetParent !== null);
  const items = all.map(x => {
    const r = x.getBoundingClientRect();
    return {
      tag: x.tagName,
      text: String(x.textContent || '').trim(),
      title: x.getAttribute('title'),
      w: Math.round(r.width),
      h: Math.round(r.height),
      x: Math.round(r.left),
      y: Math.round(r.top),
    };
  }).filter(t => t.h >= 8 && t.h <= 40 && t.w >= 20 && t.w <= 200 && /^(3D|3D Model|3D Preview|Personal Models|Click to Preview 3D)$/i.test(t.text));
  const tab = items.find(t => t.tag === 'LI' && t.text === '3D Model')
    || items.find(t => t.tag === 'SPAN' && t.text === '3D Model' && t.h >= 12);
  const btn = items.find(t => t.tag === 'BUTTON' && t.text === '3D');
  const clickAt = (item) => {
    if (!item) return false;
    const el = all.find(x => {
      const r = x.getBoundingClientRect();
      return x.tagName === item.tag && String(x.textContent || '').trim() === item.text
        && Math.round(r.left) === item.x && Math.round(r.top) === item.y;
    });
    if (!el) return false;
    el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    return true;
  };
  return { items, clickedTab: clickAt(tab), clickedBtn: clickAt(btn), tab, btn };
})()
