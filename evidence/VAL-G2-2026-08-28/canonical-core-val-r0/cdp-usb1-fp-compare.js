(async () => {
  const R = window._EXTAPI_ROOT_;
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const USB1_FP = '0c8e199e56e60728';
  const DEV_FP = '279f06324aa142578b6ff40a12f66d9b';
  const timed = (p, ms) => Promise.race([
    Promise.resolve().then(() => p).then(v => ({ ok: true, v })).catch(e => ({ ok: false, err: String(e && e.message || e) })),
    new Promise(r => setTimeout(() => r({ ok: false, timeout: ms }), ms)),
  ]);
  const slim = async (uuid, lib) => {
    const g = await timed(R.lib_Footprint.get(uuid, lib), 5000);
    if (!g.ok) return { uuid, lib, ...g };
    const d = g.v || {};
    return {
      uuid, lib,
      name: d.name,
      libraryUuid: d.libraryUuid,
      description: d.description,
      keys: Object.keys(d),
    };
  };
  const file = async (uuid, lib) => {
    const g = await timed(R.sys_FileManager.getFootprintFileByFootprintUuid(uuid, lib, 'elibz2'), 5000);
    if (!g.ok || !g.v) return { uuid, lib, ...g };
    return { uuid, lib, name: g.v.name, size: g.v.size };
  };
  const out = {
    usb1_proj: await slim(USB1_FP, PROJECT),
    usb1_pers: await slim(USB1_FP, PERSONAL),
    dev_pers: await slim(DEV_FP, PERSONAL),
    dev_proj: await slim(DEV_FP, PROJECT),
    file_usb1_proj: await file(USB1_FP, PROJECT),
    file_usb1_pers: await file(USB1_FP, PERSONAL),
    file_dev_pers: await file(DEV_FP, PERSONAL),
  };

  out.fpModifyProj = await timed(R.lib_Device.modify(
    '7e7eac39cf44433b9710c4ae4afab424', PERSONAL, undefined, null,
    { footprint: { uuid: USB1_FP, libraryUuid: PROJECT } }, undefined, undefined,
  ), 8000);

  out.create = await timed(R.lib_Device.create(
    PERSONAL,
    'CX70M-24P1-USB1-FP',
    undefined,
    {
      symbol: { uuid: 'c8b5c381560a4f7192aa521a21010e99', libraryUuid: PERSONAL },
      footprint: { uuid: USB1_FP, libraryUuid: PERSONAL },
      model3D: { uuid: '08b2bb7ecebd47fc8f45f08f001d782e', libraryUuid: PERSONAL },
    },
    'USB1 footprint 3D bind only',
  ), 8000);

  return out;
})()
