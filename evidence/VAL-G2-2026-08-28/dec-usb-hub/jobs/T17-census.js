(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  function sourceHash(source) {
    let hash = 2166136261;
    for (let i = 0; i < source.length; i += 1) {
      hash ^= source.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return source.length + ':' + (hash >>> 0).toString(16).padStart(8, '0');
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  await eda.sch_Document.save();
  const source = await eda.sys_FileManager.getDocumentSource();
  let wires = 0;
  let comps = 0;
  for (const chunk of source.split('\n')) {
    if (chunk.includes('"type":"WIRE"')) wires += 1;
    if (chunk.includes('"type":"COMPONENT"')) comps += 1;
  }
  return { proj: info.uuid, saved: true, sourceHash: sourceHash(source), comps, wires };
})()
