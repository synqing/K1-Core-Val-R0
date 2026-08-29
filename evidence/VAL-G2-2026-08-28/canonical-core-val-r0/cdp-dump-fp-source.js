(async () => {
  const R = window._EXTAPI_ROOT_;
  const tab = '279f06324aa142578b6ff40a12f66d9b@27700277ef7a49e48a0293bece6b2993';
  const out = {};
  try { out.ctx = await (R.dmt_EditorControl && R.sys_DesignSpace && true); } catch (e) {}
  try {
    out.source = await R.sys_FileManager.getDocumentSource(tab.split('@')[0]);
  } catch (e) {
    out.sourceErr = String(e && e.message || e);
    try { out.source2 = await R.sys_FileManager.getDocumentSource(); } catch (e2) { out.source2Err = String(e2 && e2.message || e2); }
  }
  const src = typeof out.source === 'string' ? out.source : (out.source && out.source.source);
  out.srcType = typeof src;
  out.srcLen = typeof src === 'string' ? src.length : null;
  if (typeof src === 'string') {
    out.hits = {
      model3D: (src.match(/model3D/gi) || []).length,
      ATTR: (src.match(/\["ATTR"/g) || []).length,
      threeD: (src.match(/3D/g) || []).length,
    };
    const lines = src.split('\n').filter(l => /3D|model|MODEL|Height/i.test(l));
    out.interesting = lines.slice(0, 40);
    out.head = src.slice(0, 800);
  }
  return out;
})()
