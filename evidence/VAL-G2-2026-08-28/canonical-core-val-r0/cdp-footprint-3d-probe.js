(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const USB1_FP = '0c8e199e56e60728';
  const USB2_FP = '59bef7e87cff4cd580561703b62d8c19_001a257400b89df6';
  const out = {};
  try { await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT); } catch (e) { out.actErr = String(e && e.message || e); }
  await new Promise(r => setTimeout(r, 300));
  let fps = [];
  try { fps = await R.sys_FileManager.getDocumentFootprintSources(); }
  catch (e) { out.fpErr = String(e && e.message || e); }
  out.count = Array.isArray(fps) ? fps.length : null;
  const wanted = new Set([USB1_FP, USB2_FP]);
  out.hits = [];
  for (const row of (fps || [])) {
    if (!wanted.has(row.footprintUuid) && !(row.documentSource || '').includes('CX70M') && !(row.documentSource || '').includes('HYCW78')) continue;
    const src = row.documentSource || '';
    const lines = src.split('\n');
    const interesting = lines.filter(l => /3d|3D|model|MODEL|offset|transform|STEP|step|hirose|CX70|HYCW/i.test(l)).slice(0, 40);
    out.hits.push({
      footprintUuid: row.footprintUuid,
      srcLen: src.length,
      has3d: /3d|3D|model3D|MODEL3D/i.test(src),
      interesting,
      head: src.slice(0, 400),
    });
  }
  try {
    const info = await R.dmt_SelectControl.getCurrentDocumentInfo();
    out.doc = info;
  } catch (e) { out.docErr = String(e && e.message || e); }
  return out;
})()
