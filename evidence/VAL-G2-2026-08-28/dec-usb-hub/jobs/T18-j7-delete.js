(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  function sourceHash(source) {
    let hash = 2166136261;
    for (let i = 0; i < source.length; i += 1) {
      hash ^= source.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return source.length + ':' + (hash >>> 0).toString(16).padStart(8, '0');
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  const j7 = await eda.sch_PrimitiveComponent.get('e8334').catch(() => null);
  const j1 = await eda.sch_PrimitiveComponent.get('ea47c20de228fa3a').catch(() => null);
  const j7st = j7 && (j7.getState ? j7.getState() : j7);
  const j1st = j1 && (j1.getState ? j1.getState() : j1);
  if (!j1st) return { stop: true, reason: 'J1_MISSING' };
  const j7name = j7st ? (j7st.designator || j7st.name || '').toString() : '';
  if (j7st && !j7name.includes('J7')) return { stop: true, reason: 'J7_ID_MISMATCH', j7name };
  if (j7st) await eda.sch_PrimitiveComponent.delete('e8334');
  await eda.sch_Document.save();
  const afterJ7 = await eda.sch_PrimitiveComponent.get('e8334').catch(() => null);
  const afterJ1 = await eda.sch_PrimitiveComponent.get('ea47c20de228fa3a').catch(() => null);
  const source = await eda.sys_FileManager.getDocumentSource();
  let comps = 0;
  let wires = 0;
  for (const chunk of source.split('\n')) {
    if (chunk.includes('"type":"COMPONENT"')) comps += 1;
    if (chunk.includes('"type":"WIRE"')) wires += 1;
  }
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    j7Before: j7st ? { id: 'e8334', name: j7name, x: j7st.x, y: j7st.y } : { id: 'e8334', alreadyGone: true },
    j7After: afterJ7 ? 'STILL_PRESENT' : 'GONE',
    j1After: afterJ1 ? 'PRESENT' : 'GONE',
    sourceHasJ7Id: source.includes('e8334'),
    sourceHasJ7Des: source.includes('J7-ESP'),
    comps,
    wires,
  };
})()
