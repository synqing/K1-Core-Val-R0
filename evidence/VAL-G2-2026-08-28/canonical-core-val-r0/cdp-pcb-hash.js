(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  try { await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT); } catch (e) {}
  await new Promise(r => setTimeout(r, 400));
  const source = await R.sys_FileManager.getDocumentSource();
  const buf = new TextEncoder().encode(source);
  const digest = await crypto.subtle.digest('SHA-256', buf);
  const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
  return {
    doc: await R.dmt_SelectControl.getCurrentDocumentInfo(),
    sourceHash: source.length + ':' + hex.slice(0, 8),
    hasUSB1: source.includes('USB1'),
    hasCX70: source.includes('CX70M'),
    hasU1: source.includes('"U1"'),
    hasGT: source.includes('GT-USB-7005A'),
    hasC5250872: source.includes('C5250872'),
    hasSeated: source.includes('08b2bb7ecebd47fc8f45f08f001d782e'),
  };
})()
