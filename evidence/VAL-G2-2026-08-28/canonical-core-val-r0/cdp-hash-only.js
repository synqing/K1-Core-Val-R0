(async () => {
  const R = window._EXTAPI_ROOT_;
  const TAB = '59bef7e87cff4cd580561703b62d8c19@64325d0e55e0435abd018defb0089a9b';
  try { await R.dmt_EditorControl.activateDocument(TAB); } catch (e) {}
  await new Promise(r => setTimeout(r, 400));
  const source = await R.sys_FileManager.getDocumentSource();
  const buf = new TextEncoder().encode(source);
  const digest = await crypto.subtle.digest('SHA-256', buf);
  const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
  return { len: source.length, hash: source.length + ':' + hex.slice(0, 8) };
})()
