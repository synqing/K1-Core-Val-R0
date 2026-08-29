(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const out = { tries: [] };
  const tryOpen = async (id) => {
    try {
      const tab = await R.dmt_EditorControl.openDocument(id);
      out.tries.push({ id, tab });
    } catch (e) {
      out.tries.push({ id, err: String(e && e.message || e) });
    }
  };
  await tryOpen('3d-' + PCB);
  await tryOpen('3d-' + PCB + '@' + PROJECT);
  await tryOpen(PCB + '-3d');
  await tryOpen('3D-' + PCB);
  await tryOpen('pcb3d-' + PCB);
  const named = [];
  let p = R.dmt_EditorControl;
  while (p && named.length < 80) {
    for (const k of Object.getOwnPropertyNames(p)) {
      if (/3d|3D|open|Open|preview|Preview|document|Document/i.test(k)) named.push(k);
    }
    p = Object.getPrototypeOf(p);
  }
  out.editorKeys = [...new Set(named)];
  const titles = [...document.querySelectorAll('[title],button,div,span,a,li')]
    .filter(el => el.offsetParent !== null)
    .map(el => (el.getAttribute('title') || el.textContent || '').trim())
    .filter(t => t && /3\s*D|三维|预览/.test(t) && t.length < 40);
  out.visible = [...new Set(titles)].slice(0, 40);
  try { out.current = await R.dmt_SelectControl.getCurrentDocumentInfo(); } catch (e) { out.current = String(e && e.message || e); }
  return out;
})()
