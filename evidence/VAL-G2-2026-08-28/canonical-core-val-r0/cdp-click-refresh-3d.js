(() => {
  const nodes = [...document.querySelectorAll('[title],button,[aria-label]')].filter(x => x.offsetParent !== null);
  const hits = nodes
    .map(x => ({
      title: x.getAttribute('title') || '',
      aria: x.getAttribute('aria-label') || '',
      text: (x.textContent || '').trim().slice(0, 40),
      tag: x.tagName,
    }))
    .filter(x => /refresh|rebuild|reload|刷新/i.test(x.title + x.aria + x.text));
  const refresh = nodes.find(x => {
    const t = String(x.getAttribute('title') || x.getAttribute('aria-label') || '').trim();
    return t === 'Refresh' || t === '刷新';
  });
  if (refresh) {
    refresh.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    return { ok: true, hits };
  }
  return { ok: false, hits };
})()
