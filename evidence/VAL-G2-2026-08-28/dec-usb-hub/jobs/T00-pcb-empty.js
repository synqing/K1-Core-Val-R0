(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  let pcbComp = null;
  let pcbVia = null;
  try {
    const src = await eda.sys_FileManager.getDocumentSource(PCB);
    pcbComp = typeof src === 'string' ? (src.match(/"compHead"/g) || []).length : null;
    pcbVia = typeof src === 'string' ? (src.match(/"via"/g) || src.match(/VIA/g) || []).length : null;
    return {
      proj: info.uuid,
      pcbUuid: PCB,
      sourceLen: typeof src === 'string' ? src.length : null,
      docTypeHint: typeof src === 'string' ? /"docType":"([^"]+)"/.exec(src)?.[1] : null,
      lookComp: typeof src === 'string' ? (src.includes('"components"') || src.includes('COMP')) : null,
      sample: typeof src === 'string' ? src.slice(0, 200) : src,
    };
  } catch (e) {
    return { proj: info.uuid, error: String(e && e.message || e) };
  }
})()
