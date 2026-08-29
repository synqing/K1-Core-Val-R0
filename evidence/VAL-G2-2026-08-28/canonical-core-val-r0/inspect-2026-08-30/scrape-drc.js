(async () => {
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  let check = null;
  try {
    const r = eda.sch_Drc.check(true, true, true);
    check = { fired: true, type: typeof r };
  } catch (e) {
    check = { err: String(e && e.message || e) };
  }
  await new Promise((r) => setTimeout(r, 1500));
  const texts = [];
  for (const n of document.querySelectorAll("div,section,aside,span,li,p")) {
    const t = (n.innerText || "").trim();
    if (t.length > 30 && /fatal|warn|error|pin|net|component|drc/i.test(t) && t.length < 8000) {
      texts.push({ cls: String(n.className || "").slice(0, 80), n: t.length, t: t.slice(0, 4000) });
    }
  }
  texts.sort((a, b) => b.n - a.n);
  return { uuid: info.uuid, name: info.name || info.friendlyName, check, hits: texts.slice(0, 6) };
})()
