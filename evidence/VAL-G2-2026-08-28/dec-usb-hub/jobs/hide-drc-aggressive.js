(() => {
  const hidden = [];
  const vh = window.innerHeight || 900;
  for (const n of document.querySelectorAll('div,section,aside')) {
    const r = n.getBoundingClientRect();
    if (r.height < 80 || r.width < 200) continue;
    if (r.top < vh * 0.45) continue;
    const t = (n.innerText || '').slice(0, 120);
    const cls = (n.className || '').toString();
    if (/drc|fatal|warn|dock|bottom/i.test(t + cls) || r.top > vh * 0.55) {
      if (r.height > 120 && r.bottom > vh * 0.7) {
        n.style.display = 'none';
        n.style.height = '0px';
        n.style.maxHeight = '0px';
        hidden.push((cls || t).toString().slice(0, 60));
      }
    }
  }
  for (const n of document.querySelectorAll('[role="tab"],button,div')) {
    const t = (n.textContent || '').trim();
    if (t === 'DRC' || t === 'drc') {
      try { n.click(); hidden.push('clicked-drc-tab'); } catch (e) { /* ignore */ }
    }
  }
  return { hidden: hidden.slice(0, 25), count: hidden.length, vh };
})()
