(async () => {
  const PROJECT = "64325d0e55e0435abd018defb0089a9b";
  const PAGE = "1435cb46f39e48c8a8aadbb84ca81603";
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const doc = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  if (info.uuid !== PROJECT || doc.uuid !== PAGE) {
    return { stop: true, reason: "identity", project: info.uuid, doc: doc.uuid, name: info.friendlyName || info.name };
  }

  let check = null;
  try {
    check = await eda.sch_Drc.check(true, false, true);
  } catch (e) {
    check = { err: String(e && e.message || e) };
  }

  await new Promise((r) => setTimeout(r, 800));

  const items = [];
  const seen = new Set();
  document.querySelectorAll("div,li,span,p,pre,td").forEach((root) => {
    const t = (root.innerText || "").trim();
    if (!t || t.length > 500) return;
    if (!/\[(Warn|Error|Fatal|Info)\]/.test(t)) return;
    if (seen.has(t)) return;
    seen.add(t);
    items.push(t);
  });
  const counts = {};
  for (const t of items) {
    const m = t.match(/\[(Warn|Error|Fatal|Info)\]/);
    const k = m ? m[1] : "other";
    counts[k] = (counts[k] || 0) + 1;
  }

  let netlistKeys = null;
  try {
    netlistKeys = Object.keys(eda.sch_Netlist || {}).slice(0, 30);
  } catch (e) {
    netlistKeys = String(e);
  }

  return {
    project: info.uuid,
    name: info.friendlyName || info.name,
    doc: doc.uuid,
    title: document.title,
    check,
    drc_counts: counts,
    warns: items.filter((t) => t.includes("[Warn]")),
    errors: items.filter((t) => t.includes("[Error]") || t.includes("[Fatal]")),
    info_count: items.filter((t) => t.includes("[Info]")).length,
    infos_sample: items.filter((t) => t.includes("[Info]")).slice(0, 25),
    netlistKeys,
  };
})()
