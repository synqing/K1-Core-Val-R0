(async () => {
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const home = document.querySelector(".home") || document.body;
  const t = (home.innerText || "").split("\n");
  const rows = t.filter((l) => /\[(Warn|Error|Fatal|Info)\]/.test(l) || /Warn\s*\(|Fatal|Finish Design Rule/.test(l));
  return { uuid: info.uuid, n: t.length, rows: rows.slice(0, 80), warnLines: t.filter((l) => l.includes("[Warn]")) };
})()
