(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  const fm = [];
  for (const name of Object.getOwnPropertyNames(eda.sys_FileManager || {})) {
    fm.push(name);
  }
  const proj = [];
  for (const name of Object.getOwnPropertyNames(eda.dmt_Project || {})) {
    if (/export|import|open|convert|download|save|epro|pack|file/i.test(name)) proj.push(name);
  }
  return {
    uuid: current && current.uuid,
    friendlyName: current && current.friendlyName,
    fileManager: fm.sort(),
    projectKeys: proj.sort(),
  };
})()
