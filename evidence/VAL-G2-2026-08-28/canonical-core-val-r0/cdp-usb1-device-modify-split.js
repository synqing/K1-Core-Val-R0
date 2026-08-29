(async () => {
  const R = window._EXTAPI_ROOT_;
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const DEV = '7e7eac39cf44433b9710c4ae4afab424';
  const FP = '0c8e199e56e60728';
  const SEATED = '08b2bb7ecebd47fc8f45f08f001d782e';
  const TITLE = 'USB_C_Hirose_CX_4800304000_seated';
  const SYMBOL = 'c8b5c381560a4f7192aa521a21010e99';
  const dump = (e) => {
    if (e && typeof e === 'object') {
      try { return JSON.parse(JSON.stringify(e)); } catch (_) {}
      return { message: e.message, name: e.name, keys: Object.keys(e), string: String(e) };
    }
    return String(e);
  };
  const out = { steps: [] };
  const note = (label, extra) => { out.steps.push({ label, ...extra }); };

  const tryMod = async (label, assoc, prop) => {
    try {
      const result = await R.lib_Device.modify(DEV, PERSONAL, undefined, null, assoc, undefined, prop);
      note(label, { result });
      return result;
    } catch (e) {
      note(label, { err: dump(e) });
      return null;
    }
  };

  await tryMod('model3d-only', { model3D: { uuid: SEATED, libraryUuid: PERSONAL } }, {
    otherProperty: { '3D Model': SEATED, '3D Model Title': TITLE },
  });

  await tryMod('footprint-obj', { footprint: { uuid: FP, libraryUuid: PERSONAL } }, undefined);
  await tryMod('footprint-uuid', { footprintUuid: FP }, undefined);
  await tryMod('footprint-project', { footprint: { uuid: FP, libraryUuid: PROJECT } }, undefined);

  // Fresh device that uses the USB1 footprint.
  try {
    out.created = await R.lib_Device.create(
      PERSONAL,
      'CX70M-24P1-USB1-FP',
      { libraryUuid: PERSONAL, libraryType: '3', primaryClassificationUuid: '467bd44cbe344ac9875addc0b77e3b60' },
      {
        symbol: { uuid: SYMBOL, libraryUuid: PERSONAL },
        footprint: { uuid: FP, libraryUuid: PERSONAL },
        model3D: { uuid: SEATED, libraryUuid: PERSONAL },
      },
      'USB1 footprint 3D bind only',
      {
        designator: 'USB?',
        manufacturer: 'HRS',
        manufacturerId: 'CX70M-24P1',
        supplier: 'LCSC',
        supplierId: 'C778726',
      },
    );
    note('create', { result: out.created });
  } catch (e) {
    note('create', { err: dump(e) });
    try {
      out.created2 = await R.lib_Device.create(
        PERSONAL,
        'CX70M-24P1-USB1-FP',
        undefined,
        {
          symbol: { uuid: SYMBOL, libraryUuid: PERSONAL },
          footprint: { uuid: FP, libraryUuid: PERSONAL },
          model3D: { uuid: SEATED, libraryUuid: PERSONAL },
        },
        'USB1 footprint 3D bind only',
      );
      note('create-minimal', { result: out.created2 });
    } catch (e2) {
      note('create-minimal', { err: dump(e2) });
    }
  }

  try {
    const after = await R.lib_Device.get(DEV, PERSONAL);
    note('dev-after', {
      assoc: after && after.association,
      other3d: after && after.property && after.property.otherProperty
        ? {
            model: after.property.otherProperty['3D Model'],
            title: after.property.otherProperty['3D Model Title'],
            footprint: after.property.otherProperty.Footprint,
          }
        : null,
    });
  } catch (e) {
    note('dev-after', { err: dump(e) });
  }

  if (out.created || out.created2) {
    try {
      const nu = out.created || out.created2;
      const d = await R.lib_Device.get(nu, PERSONAL);
      note('new-dev', { uuid: nu, assoc: d && d.association, name: d && d.name });
    } catch (e) {
      note('new-dev', { err: dump(e) });
    }
  }

  try {
    out.search = (await R.lib_Device.search('CX70M-24P1-USB1', PERSONAL, undefined, 10, 1) || [])
      .map(x => ({ uuid: x.uuid, name: x.name, libraryUuid: x.libraryUuid }));
  } catch (e) {
    note('search', { err: dump(e) });
  }

  return out;
})()
