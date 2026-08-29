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
  const bad = 'ab940e6e68a4806f';
  let deleted = false;
  try {
    await eda.sch_PrimitiveWire.delete(bad);
    deleted = true;
  } catch (e) {
    deleted = String(e && e.message || e).slice(0, 160);
  }
  const afterIds = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  const stillBad = (afterIds || []).includes(bad);
  const created = [];
  try {
    const flag = await eda.sch_PrimitiveComponent.createNetFlag('Ground', 'GND', 595, 750);
    const st = flag && (flag.getState ? flag.getState() : flag);
    created.push({ tag: 'cfg-gnd-flag', ok: true, id: st && st.primitiveId });
  } catch (e) {
    created.push({ tag: 'cfg-gnd-flag', ok: false, err: String(e && e.message || e).slice(0, 160) });
  }
  try {
    const w = await eda.sch_PrimitiveWire.create([570, 750, 595, 750], 'GND');
    const st = w && (w.getState ? w.getState() : w);
    created.push({ tag: 'p14-to-gnd-flag', ok: true, id: st && st.primitiveId, net: st && st.net });
  } catch (e) {
    created.push({ tag: 'p14-to-gnd-flag', ok: false, err: String(e && e.message || e).slice(0, 160) });
  }
  try {
    const w = await eda.sch_PrimitiveWire.create([570, 840, 595, 840], 'USB_PLLFILT');
    const st = w && (w.getState ? w.getState() : w);
    created.push({ tag: 'p23-pll-restore', ok: true, id: st && st.primitiveId, net: st && st.net });
  } catch (e) {
    created.push({ tag: 'p23-pll-restore', ok: false, err: String(e && e.message || e).slice(0, 160) });
  }
  try {
    const w = await eda.sch_PrimitiveWire.create([660, 1008, 680, 1008], 'USB_NON_REM1');
    const st = w && (w.getState ? w.getState() : w);
    created.push({ tag: 'r89-nr1-restore', ok: true, id: st && st.primitiveId, net: st && st.net });
  } catch (e) {
    created.push({ tag: 'r89-nr1-restore', ok: false, err: String(e && e.message || e).slice(0, 160) });
  }
  await eda.sch_Document.save();
  const source = await eda.sys_FileManager.getDocumentSource();
  const comps = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  return {
    proj: info.uuid,
    deleted,
    stillBad,
    created,
    saved: true,
    sourceHash: sourceHash(source),
    components: (comps || []).length,
    wires: (wires || []).length,
  };
})()
