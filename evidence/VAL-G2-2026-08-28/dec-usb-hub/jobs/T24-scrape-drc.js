(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  for (const n of document.querySelectorAll('div,section,aside')) {
    if (n.style && n.style.display === 'none') n.style.display = '';
    if (n.style && n.style.height === '0px') n.style.height = '';
  }
  try { await eda.sch_Drc.check(true, true, true); } catch (e) { /* ignore */ }
  const texts = [];
  const sel = [
    '[class*="drc"]', '[class*="Drc"]', '[class*="DRC"]',
    '[class*="error-list"]', '[class*="result"]',
  ];
  for (const s of sel) {
    for (const n of document.querySelectorAll(s)) {
      const t = (n.innerText || '').trim();
      if (t.length > 40 && /fatal|warn|error|pin|net|component/i.test(t)) {
        texts.push({ cls: String(n.className).slice(0, 80), n: t.length, t: t.slice(0, 2000) });
      }
    }
  }
  texts.sort((a, b) => b.n - a.n);
  return { proj: info.uuid, hits: texts.slice(0, 8) };
})()
