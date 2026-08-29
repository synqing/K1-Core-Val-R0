(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  function sourceHash(source) {
    let hash = 2166136261;
    for (let i = 0; i < source.length; i += 1) hash ^= source.charCodeAt(i);
    return source.length + ':' + (hash >>> 0).toString(16).padStart(8, '0');
  }
  const src = await eda.sys_FileManager.getDocumentSource();
  return {
    proj: info.uuid,
    hash: sourceHash(src),
    components: ((await eda.sch_PrimitiveComponent.getAllPrimitiveId()) || []).length,
    wires: ((await eda.sch_PrimitiveWire.getAllPrimitiveId()) || []).length,
    u21: !!(await eda.sch_PrimitiveComponent.get('fb7c84f0a582bd9c').catch(() => null)),
    r85: !!(await eda.sch_PrimitiveComponent.get('5cf017917b429da4').catch(() => null)),
    j6: !!(await eda.sch_PrimitiveComponent.get('e98163').catch(() => null)),
  };
})()
