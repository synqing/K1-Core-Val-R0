(() => {
  const hidden = [];
  const nodes = document.querySelectorAll('[class*="drc"], [class*="Drc"], [class*="bottom-panel"], [class*="BottomPanel"]');
  for (const n of nodes) {
    n.style.display = 'none';
    hidden.push((n.className || '').toString().slice(0, 80));
  }
  const footer = document.querySelector('.bottom-panel, .drc-panel, #drc-panel');
  if (footer) { footer.style.display = 'none'; hidden.push('footer'); }
  return { hidden: hidden.slice(0, 20), count: hidden.length };
})()
