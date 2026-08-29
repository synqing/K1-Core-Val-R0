(async () => {
  const R = window._EXTAPI_ROOT_;
  const TAB = '59bef7e87cff4cd580561703b62d8c19@64325d0e55e0435abd018defb0089a9b';
  const USB1_FP = '0c8e199e56e60728';
  const USB2_FP = '59bef7e87cff4cd580561703b62d8c19_001a257400b89df6';
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  try { await R.dmt_EditorControl.activateDocument(TAB); } catch (e) {}
  await new Promise(r => setTimeout(r, 300));
  const out = {};
  const tryGet = async (label, uuid, lib) => {
    const row = { uuid, lib };
    try { row.file = await R.sys_FileManager.getFootprintFileByFootprintUuid(uuid); }
    catch (e) { row.fileErr = String(e && e.message || e); }
    try { row.fp = await R.lib_Footprint.get(uuid, lib); }
    catch (e) { row.fpErr = String(e && e.message || e); }
    const src = typeof row.file === 'string' ? row.file
      : (row.file && (row.file.documentSource || row.file.source || row.file.data)) || '';
    if (typeof src === 'string' && src) {
      row.srcLen = src.length;
      row.has3d = /3d|3D|MODEL/i.test(src);
      row.interesting = src.split('\n').filter(l => /3d|3D|MODEL|offset|transform|hirose|CX70|HYCW/i.test(l)).slice(0, 50);
      row.head = src.slice(0, 500);
    } else {
      row.fileType = typeof row.file;
      row.fileKeys = row.file && typeof row.file === 'object' ? Object.keys(row.file) : null;
    }
    out[label] = row;
  };
  await tryGet('usb1_project', USB1_FP, PROJECT);
  await tryGet('usb1_personal', USB1_FP, PERSONAL);
  await tryGet('usb2_project', USB2_FP, PROJECT);
  return out;
})()
