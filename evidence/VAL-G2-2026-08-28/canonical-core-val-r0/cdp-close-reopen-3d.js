(async () => {
  const R = window._EXTAPI_ROOT_;
  const named = (obj) => {
    const keys = [];
    let p = obj;
    while (p && p !== Object.prototype && keys.length < 60) {
      for (const k of Object.getOwnPropertyNames(p)) {
        if (/close|Close|3d|3D|preview/i.test(k)) keys.push(k);
      }
      p = Object.getPrototypeOf(p);
    }
    return keys;
  };
  const out = { editor: named(R.dmt_EditorControl), pcb: named(R.pcb_Document) };
  const current = await R.dmt_SelectControl.getCurrentDocumentInfo();
  out.current = current;
  const tryClose = async (id) => {
    try {
      if (typeof R.dmt_EditorControl.closeDocument === 'function') {
        return { id, closeDocument: await R.dmt_EditorControl.closeDocument(id) };
      }
    } catch (e) { return { id, err: String(e && e.message || e) }; }
    return { id, err: 'no closeDocument' };
  };
  out.closeCurrent = await tryClose(current && current.tabId);
  out.close3d = await tryClose('3d-' + current.uuid);
  await new Promise(r => setTimeout(r, 400));
  try { await R.dmt_EditorControl.activateDocument('59bef7e87cff4cd580561703b62d8c19@64325d0e55e0435abd018defb0089a9b'); } catch (e) {}
  out.after = await R.dmt_SelectControl.getCurrentDocumentInfo();
  return out;
})()
