(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const keys = [];
  for (const name of Object.getOwnPropertyNames(eda.dmt_Project || {})) {
    if (/export|download|save|epro|pack/i.test(name)) keys.push('dmt_Project.' + name);
  }
  for (const name of Object.getOwnPropertyNames(eda.sys_FileManager || {})) {
    if (/export|download|save|epro|pack|zip/i.test(name)) keys.push('sys_FileManager.' + name);
  }
  for (const name of Object.getOwnPropertyNames(eda.dmt_EditorControl || {})) {
    if (/export|download|epro/i.test(name)) keys.push('dmt_EditorControl.' + name);
  }
  let pcbIds = [];
  try {
    pcbIds = await eda.pcb_PrimitiveComponent.getAllPrimitiveId();
  } catch (e) {
    pcbIds = { err: String(e && e.message || e).slice(0, 80) };
  }
  return { proj: info.uuid, keys, pcbIds };
})()
