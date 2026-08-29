(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
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
  await eda.sch_Document.save();
  const source = await eda.sys_FileManager.getDocumentSource();
  let comps = 0;
  let wires = 0;
  let pages = 0;
  for (const chunk of source.split('\n')) {
    if (chunk.includes('"type":"COMPONENT"')) comps += 1;
    if (chunk.includes('"type":"WIRE"')) wires += 1;
    if (chunk.includes('"type":"PAGE"') || chunk.includes('"itemType":"Schematic Page"')) pages += 1;
  }
  const j6 = await eda.sch_PrimitiveComponent.get('e98163').catch(() => null);
  const j6st = j6 && (j6.getState ? j6.getState() : j6);
  const j6pins = j6 ? await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId('e98163') : [];
  let pcb = { error: 'not-read' };
  try {
    const pcbSrc = await eda.sys_FileManager.getDocumentSource(PCB);
    pcb = {
      len: typeof pcbSrc === 'string' ? pcbSrc.length : null,
      comps: typeof pcbSrc === 'string' ? (pcbSrc.match(/"type":"COMPONENT"/g) || []).length : null,
      vias: typeof pcbSrc === 'string' ? (pcbSrc.match(/"type":"VIA"/g) || []).length : null,
    };
  } catch (e) {
    pcb = { error: String(e && e.message || e).slice(0, 200) };
  }
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    comps,
    wires,
    sourceHasJ7: source.includes('J7-ESP'),
    j6: j6st ? { id: 'e98163', name: j6st.designator || j6st.name, x: j6st.x, y: j6st.y, pins: (j6pins || []).length } : null,
    pcb,
    sheets: 1,
  };
})()
