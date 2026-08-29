(async () => {
  const R = window._EXTAPI_ROOT_;
  const personal = '27700277ef7a49e48a0293bece6b2993';
  const footprint = '279f06324aa142578b6ff40a12f66d9b';
  const named = (obj) => obj ? Object.getOwnPropertyNames(Object.getPrototypeOf(obj)).filter(k => k !== 'constructor') : null;
  const out = { footprintMethods: named(R.lib_Footprint), editorKeys: named(R.dmt_EditorControl) };
  try {
    out.opened = await R.lib_Footprint.openInEditor(footprint, personal);
  } catch (e) { out.openErr = String(e && e.message || e); }
  return out;
})()
