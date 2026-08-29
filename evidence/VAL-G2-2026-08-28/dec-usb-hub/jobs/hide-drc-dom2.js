(() => {
  const hidden = [];
  const sels = [
    '.bottom-panel', '.dock-bottom', '.x-dock-bottom',
    '[class*="bottomPanel"]', '[class*="BottomDock"]',
    '[class*="drc-result"]', '[class*="DrcResult"]',
    '[class*="message-panel"]', '[class*="log-panel"]',
  ];
  for (const sel of sels) {
    for (const n of document.querySelectorAll(sel)) {
      n.style.display = 'none';
      n.style.height = '0';
      hidden.push(sel);
    }
  }
  for (const n of document.querySelectorAll('div')) {
    const t = (n.innerText || '').slice(0, 80);
    if (t.includes('Fatal Error') && t.includes('Warn') && n.getBoundingClientRect().height > 200) {
      n.style.display = 'none';
      hidden.push('fatal-block:' + t.slice(0, 40));
    }
  }
  return { hidden: hidden.slice(0, 30), count: hidden.length };
})()
