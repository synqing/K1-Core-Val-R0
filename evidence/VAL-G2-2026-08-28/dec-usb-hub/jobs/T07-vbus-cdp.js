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
  async function pinsOf(id) {
    const pins = await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(id);
    return (pins || []).map((p) => ({
      n: p.getState_PinNumber(),
      x: p.getState_X(),
      y: p.getState_Y(),
    }));
  }
  const r78 = await pinsOf('a60d36245cbf4e86');
  const r79 = await pinsOf('d7ed808dd32d71fa');
  const r80 = await pinsOf('f6a62bb1e7d23ff6');
  function pin(rows, n) { return rows.find((r) => String(r.n) === String(n)); }
  const created = [];
  async function label(x, y, net) {
    try {
      await eda.sch_PrimitiveAttribute.createNetLabel(x, y, net);
      created.push({ kind: 'label', net, x, y, ok: true });
    } catch (e) {
      created.push({ kind: 'label', net, x, y, ok: false, err: String(e && e.message || e).slice(0, 120) });
    }
  }
  async function gnd(x, y) {
    try {
      const p = await eda.sch_PrimitiveComponent.createNetFlag('Ground', 'GND', x, y);
      const st = p && (p.getState ? p.getState() : p);
      if (st && st.primitiveId) {
        try { await eda.sch_PrimitiveComponent.modify(st.primitiveId, { addIntoPcb: false }); } catch (e) { /* ignore */ }
      }
      created.push({ kind: 'gnd', x, y, ok: true, id: st && st.primitiveId });
    } catch (e) {
      created.push({ kind: 'gnd', x, y, ok: false, err: String(e && e.message || e).slice(0, 120) });
    }
  }
  const r78p1 = pin(r78, 1);
  const r78p2 = pin(r78, 2);
  const r79p1 = pin(r79, 1);
  const r79p2 = pin(r79, 2);
  const r80p1 = pin(r80, 1);
  const r80p2 = pin(r80, 2);
  if (r78p1) await label(r78p1.x, r78p1.y, '5V_USB');
  if (r78p2) await label(r78p2.x, r78p2.y, 'USB_VBUS_DET');
  if (r79p1) await label(r79p1.x, r79p1.y, 'USB_VBUS_DET');
  if (r79p2) await gnd(r79p2.x, r79p2.y);
  if (r80p1) await label(r80p1.x, r80p1.y, '5V_USB');
  if (r80p2) await gnd(r80p2.x, r80p2.y);
  await label(570, 770, 'USB_VBUS_DET');
  await eda.sch_Document.save();
  const source = await eda.sys_FileManager.getDocumentSource();
  const comps = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  const onSys = /5V_SYS/.test(source.slice(source.indexOf('USB_VBUS_DET') || 0, (source.indexOf('USB_VBUS_DET') || 0) + 200));
  return {
    proj: info.uuid,
    r78, r79, r80,
    created,
    saved: true,
    sourceHash: sourceHash(source),
    components: (comps || []).length,
    wires: (wires || []).length,
    tapLooksLike5vSys: onSys,
  };
})()
