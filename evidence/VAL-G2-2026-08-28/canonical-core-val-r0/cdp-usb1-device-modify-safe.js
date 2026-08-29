(async () => {
  const R = window._EXTAPI_ROOT_;
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const DEV = '7e7eac39cf44433b9710c4ae4afab424';
  const FP = '0c8e199e56e60728';
  const SEATED = '08b2bb7ecebd47fc8f45f08f001d782e';
  const TITLE = 'USB_C_Hirose_CX_4800304000_seated';
  const dump = (e) => {
    if (!e) return e;
    if (typeof e !== 'object') return String(e);
    const o = { message: e.message, name: e.name, string: String(e) };
    try { Object.assign(o, JSON.parse(JSON.stringify(e))); } catch (_) {}
    try { o.keys = Object.keys(e); } catch (_) {}
    return o;
  };
  const timed = (p, ms, label) => Promise.race([
    Promise.resolve().then(() => p).then(v => ({ ok: true, v })).catch(e => ({ ok: false, err: dump(e) })),
    new Promise(r => setTimeout(() => r({ ok: false, timeout: ms, label }), ms)),
  ]);
  const out = { steps: [] };

  out.ping = await timed(R.dmt_SelectControl.getCurrentDocumentInfo(), 3000, 'ping');

  out.model3d = await timed(R.lib_Device.modify(
    DEV, PERSONAL, undefined, null,
    { model3D: { uuid: SEATED, libraryUuid: PERSONAL } },
    undefined,
    { otherProperty: { '3D Model': SEATED, '3D Model Title': TITLE } },
  ), 8000, 'model3d');

  if (out.model3d.timeout) return out;

  out.footprint = await timed(R.lib_Device.modify(
    DEV, PERSONAL, undefined, null,
    { footprint: { uuid: FP, libraryUuid: PERSONAL } },
    undefined,
    undefined,
  ), 8000, 'footprint');

  out.get = await timed(R.lib_Device.get(DEV, PERSONAL), 5000, 'get');
  if (out.get.ok && out.get.v) {
    const d = out.get.v;
    out.dev = {
      name: d.name,
      assoc: d.association,
      other: d.property && d.property.otherProperty ? {
        model: d.property.otherProperty['3D Model'],
        title: d.property.otherProperty['3D Model Title'],
        footprint: d.property.otherProperty.Footprint,
      } : null,
    };
  }
  return out;
})()
