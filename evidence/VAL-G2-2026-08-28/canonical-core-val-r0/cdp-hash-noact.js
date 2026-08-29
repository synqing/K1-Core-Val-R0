(async () => {
  const R = window._EXTAPI_ROOT_;
  const source = await R.sys_FileManager.getDocumentSource();
  const buf = new TextEncoder().encode(source);
  const digest = await crypto.subtle.digest('SHA-256', buf);
  const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
  const doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  return { sourceHash: source.length + ':' + hex.slice(0, 8), chars: source.length, docUuid: doc && doc.uuid };
})()
