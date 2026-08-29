(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const source = await eda.sys_FileManager.getDocumentSource();
  const idx = source.indexOf('004d113915448a0a');
  const protHits = [];
  let from = 0;
  while (protHits.length < 8) {
    const i = source.indexOf('5V_PROTECTED', from);
    if (i < 0) break;
    protHits.push({ i, around: source.slice(Math.max(0, i - 80), i + 80) });
    from = i + 12;
  }
  const gndNear = source.includes('"5V_PROTECTED"');
  return {
    proj: info.uuid,
    len: source.length,
    nl: (source.match(/\n/g) || []).length,
    pipes: (source.match(/\|\|/g) || []).length,
    c120idx: idx,
    c120around: idx >= 0 ? source.slice(idx - 60, idx + 200) : null,
    protCount: (source.match(/5V_PROTECTED/g) || []).length,
    protHits,
    gndQuoted: gndNear,
    sampleStart: source.slice(0, 180),
  };
})()
