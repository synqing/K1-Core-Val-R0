(async () => {
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const items = [];
  const seen = new Set();
  const walk = (root) => {
    const t = (root.innerText || "").trim();
    if (!t || t.length > 500) return;
    if (!/\[(Warn|Error|Fatal|Info)\]/.test(t)) return;
    if (seen.has(t)) return;
    seen.add(t);
    items.push(t);
  };
  document.querySelectorAll("div,li,span,p,pre,td").forEach(walk);
  const counts = {};
  for (const t of items) {
    const m = t.match(/\[(Warn|Error|Fatal|Info)\]/);
    const k = m ? m[1] : "other";
    counts[k] = (counts[k] || 0) + 1;
  }
  return {
    uuid: info.uuid,
    counts,
    warns: items.filter((t) => t.includes("[Warn]")),
    errors: items.filter((t) => t.includes("[Error]") || t.includes("[Fatal]")),
    infos_sample: items.filter((t) => t.includes("[Info]")).slice(0, 20),
    info_count: items.filter((t) => t.includes("[Info]")).length,
  };
})()
