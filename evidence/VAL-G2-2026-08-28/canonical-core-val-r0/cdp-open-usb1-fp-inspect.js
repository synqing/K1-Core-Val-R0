(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const SYSTEM = '0819f05c4eef4c71ace90d822a990e87';
  const FP = '0c8e199e56e60728';
  const USB2_FP = '59bef7e87cff4cd580561703b62d8c19_001a257400b89df6';
  const OFFICIAL_FP = '44616f94c6914e79972b7923414e99c1';
  const out = { tries: [] };

  const proto = (obj) => obj ? Object.getOwnPropertyNames(Object.getPrototypeOf(obj)).sort() : [];
  out.libFp = proto(R.lib_Footprint);
  out.editor = proto(R.dmt_EditorControl).filter(k => /open|Open|lib|Lib|tab|Tab|save|Save|close|Close/i.test(k));

  const tryOpen = async (label, fn) => {
    const row = { label };
    try {
      row.result = await fn();
      row.ok = true;
    } catch (e) {
      row.ok = false;
      row.err = String(e && e.message || e);
    }
    out.tries.push(row);
    return row;
  };

  await tryOpen('openInEditor-personal', () => R.lib_Footprint.openInEditor(FP, PERSONAL));
  if (!out.tries[out.tries.length - 1].ok) {
    await tryOpen('openInEditor-project', () => R.lib_Footprint.openInEditor(FP, PROJECT));
  }
  if (!out.tries.some(t => t.ok)) {
    await tryOpen('openLibraryDocument-personal', () =>
      R.dmt_EditorControl.openLibraryDocument(PERSONAL, '4', FP));
  }

  await new Promise(r => setTimeout(r, 800));
  try { out.doc = await R.dmt_SelectControl.getCurrentDocumentInfo(); }
  catch (e) { out.docErr = String(e && e.message || e); }

  try {
    const src = await R.sys_FileManager.getDocumentSource();
    out.activeSourceLen = src ? src.length : 0;
    out.activeDocType = src && src.includes('"docType":"FOOTPRINT"') ? 'FOOTPRINT' : (src && src.includes('"docType":"PCB"') ? 'PCB' : 'other');
    out.activeHas3D = !!(src && /3D Model/.test(src));
    out.activeHasSeated = !!(src && src.includes('08b2bb7ecebd47fc8f45f08f001d782e'));
    out.activeHead = src ? src.slice(0, 500) : null;
    const types = [];
    if (src) {
      const re = /\{"type":"([A-Z0-9_]+)"/g;
      let m;
      const c = {};
      while ((m = re.exec(src))) c[m[1]] = (c[m[1]] || 0) + 1;
      out.activeTypes = c;
    }
  } catch (e) { out.activeSourceErr = String(e && e.message || e); }

  try {
    const fps = await R.sys_FileManager.getDocumentFootprintSources();
    out.fpSourcesNow = Array.isArray(fps) ? fps.length : null;
  } catch (e) { out.fpSourcesNowErr = String(e && e.message || e); }

  // official CX70M donor footprint
  try { out.officialFpGet = await R.lib_Footprint.get(OFFICIAL_FP, SYSTEM); }
  catch (e) { out.officialFpGetErr = String(e && e.message || e); }
  try {
    const f = await R.sys_FileManager.getFootprintFileByFootprintUuid(OFFICIAL_FP, SYSTEM, 'elibz2');
    out.officialFpFile = f ? { name: f.name, size: f.size } : { empty: true };
  } catch (e) { out.officialFpFileErr = String(e && e.message || e); }

  // device for USB1
  try {
    const comps = await R.pcb_PrimitiveComponent.getAll();
    out.pcbCompsWhileFpOpen = Array.isArray(comps) ? comps.length : null;
  } catch (e) { out.pcbCompsErr = String(e && e.message || e); }

  out.panel = proto(R.sys_PanelControl);
  out.fileMgr = proto(R.sys_FileManager).filter(k => /3d|3D|foot|Foot|source|Source|save|Save|lib|Lib/i.test(k));
  out.pcbDoc = proto(R.pcb_Document).filter(k => /3d|3D|model|Model|save|Save|rebuild|Rebuild|refresh|Refresh/i.test(k));

  const titles = [...document.querySelectorAll('[title],button,[aria-label]')]
    .filter(x => x.offsetParent !== null)
    .map(x => x.getAttribute('title') || x.getAttribute('aria-label') || x.textContent)
    .filter(t => t && /3D|Model|Footprint|Apply|Offset|Preview/i.test(String(t)))
    .map(t => String(t).replace(/\s+/g, ' ').trim().slice(0, 80))
    .slice(0, 40);
  out.visible3dTitles = [...new Set(titles)];

  return out;
})()
