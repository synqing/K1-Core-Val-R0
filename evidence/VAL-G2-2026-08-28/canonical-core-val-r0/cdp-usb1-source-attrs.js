(async () => {
  const R = window._EXTAPI_ROOT_;
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  try { await R.dmt_EditorControl.activateDocument(PCB + '@64325d0e55e0435abd018defb0089a9b'); } catch (e) {}
  await new Promise(r => setTimeout(r, 300));
  const source = await R.sys_FileManager.getDocumentSource();
  const id = '19bbd06e9438ab5d';
  const hits = [];
  let idx = 0;
  while (true) {
    const i = source.indexOf(id, idx);
    if (i < 0) break;
    hits.push({ at: i, around: source.slice(Math.max(0, i - 80), Math.min(source.length, i + 400)) });
    idx = i + id.length;
    if (hits.length >= 8) break;
  }
  const tHits = [];
  idx = 0;
  while (true) {
    const i = source.indexOf('3D Model Transform', idx);
    if (i < 0) break;
    tHits.push(source.slice(Math.max(0, i - 120), Math.min(source.length, i + 180)));
    idx = i + 18;
    if (tHits.length >= 12) break;
  }
  return { idHits: hits.length, hits, transformSnippets: tHits };
})()
