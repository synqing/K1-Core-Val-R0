(() => {
  const all = [...document.querySelectorAll('*')].filter(x => x.offsetParent !== null);
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
  }).filter(t => t.h >= 10 && t.h <= 36 && t.w >= 40 && t.w <= 280 && /^(Personal|User|Mine|My Library|spectrasynq|Personal Models|System)$/i.test(t.text));
  const personal = items.find(t => /personal|mine|my library|spectrasynq/i.test(t.text) && t.text !== 'System');
  const models = items.find(t => t.text === 'Personal Models');
  const click = (item) => {
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
  return { items, clickedPersonal: click(personal), clickedModels: click(models), personal, models };
})()
