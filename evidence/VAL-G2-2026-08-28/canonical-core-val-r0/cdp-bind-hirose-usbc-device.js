(async () => {
  const R = window._EXTAPI_ROOT_;
  const personal = '27700277ef7a49e48a0293bece6b2993';
  const system = '0819f05c4eef4c71ace90d822a990e87';
  const official = '4db9e6982d2c421c8c7ea67eaf304069';
  const modelUuid = '71aa35b92da84360b5d9e21f25c486f0';
  const project = 'project';
  const out = { ok: false };

  const trees = {};
  for (const t of ['2', '3', '4', '5']) {
    try { trees[t] = await R.lib_Classification.getAllClassificationTree(personal, t); }
    catch (e) { trees[t] = String(e && e.message || e); }
  }
  out.trees = trees;

  let deviceClass = null;
  if (Array.isArray(trees['3'])) {
    const primary = trees['3'].find(x => x.uuid && x.uuid !== '@all') || trees['3'][0];
    if (primary && primary.uuid && primary.uuid !== '@all') {
      const child = (primary.children && primary.children[0]) || null;
      deviceClass = {
        libraryUuid: personal,
        libraryType: '3',
        primaryClassificationUuid: primary.uuid,
        secondaryClassificationUuid: child ? child.uuid : undefined,
      };
    }
  }
  if (!deviceClass) {
    try {
      out.createdPrimary = await R.lib_Classification.createPrimary(personal, '3', 'Connectors');
    } catch (e) { out.createdPrimaryErr = String(e && e.message || e); }
    const idx = out.createdPrimary;
    if (idx && (idx.primaryClassificationUuid || idx.uuid)) {
      deviceClass = {
        libraryUuid: personal,
        libraryType: '3',
        primaryClassificationUuid: idx.primaryClassificationUuid || idx.uuid,
      };
      try {
        out.createdSecondary = await R.lib_Classification.createSecondary(personal, '3', deviceClass.primaryClassificationUuid, 'USB');
        if (out.createdSecondary && (out.createdSecondary.secondaryClassificationUuid || out.createdSecondary.uuid)) {
          deviceClass.secondaryClassificationUuid = out.createdSecondary.secondaryClassificationUuid || out.createdSecondary.uuid;
        }
      } catch (e) { out.createdSecondaryErr = String(e && e.message || e); }
    }
  }
  out.deviceClass = deviceClass;

  const tryCopy = async (targetLib, classif, name) => {
    try {
      const uuid = await R.lib_Device.copy(official, system, targetLib, classif, name);
      return { ok: !!uuid, uuid, targetLib, name, classif };
    } catch (e) {
      return { ok: false, err: String(e && e.message || e), targetLib, name };
    }
  };

  out.copies = [];
  out.copies.push(await tryCopy(personal, deviceClass, 'CX70M-24P1'));
  if (!out.copies[0].ok) out.copies.push(await tryCopy(personal, ['Connectors', 'USB'], 'CX70M-24P1'));
  if (!out.copies.some(c => c.ok)) out.copies.push(await tryCopy(personal, ['Connectors'], 'CX70M-24P1-C778726'));
  if (!out.copies.some(c => c.ok)) out.copies.push(await tryCopy(project, ['Connectors'], 'CX70M-24P1'));
  if (!out.copies.some(c => c.ok)) out.copies.push(await tryCopy(project, deviceClass, 'CX70M-24P1'));

  let dest = out.copies.find(c => c.ok);

  if (!dest) {
    try {
      const created = await R.lib_Device.create(
        personal,
        'CX70M-24P1',
        deviceClass || ['Connectors', 'USB'],
        {
          symbolType: 2,
          symbol: { uuid: '66b97c87f3654e4fa9c858f82075a5af', libraryUuid: system },
          footprint: { uuid: '44616f94c6914e79972b7923414e99c1', libraryUuid: system },
          model3D: { uuid: modelUuid, libraryUuid: personal },
        },
        'CX70M-24P1 with Hirose CX 4800304000 STEP',
        {
          name: 'CX70M-24P1',
          designator: 'USB?',
          addIntoBom: true,
          addIntoPcb: true,
          manufacturer: 'HRS',
          manufacturerId: 'CX70M-24P1',
          supplier: 'LCSC',
          supplierId: 'C778726',
        },
      );
      out.createdDevice = created;
      if (created) dest = { ok: true, uuid: created, targetLib: personal, name: 'CX70M-24P1', via: 'create' };
    } catch (e) {
      out.createdDeviceErr = String(e && e.message || e);
    }
  }

  if (dest && dest.uuid) {
    try {
      out.modify = await R.lib_Device.modify(
        dest.uuid,
        dest.targetLib,
        undefined,
        undefined,
        { model3D: { uuid: modelUuid, libraryUuid: personal } },
      );
    } catch (e) { out.modifyErr = String(e && e.message || e); }
    try { out.device = await R.lib_Device.get(dest.uuid, dest.targetLib); } catch (e) { out.deviceErr = String(e && e.message || e); }
    out.dest = dest;
  }

  try { out.search = await R.lib_Device.search('CX70M-24P1', personal, undefined, 10, 1); } catch (e) { out.searchErr = String(e && e.message || e); }
  try { out.searchProj = await R.lib_Device.search('CX70M-24P1', project, undefined, 10, 1); } catch (e) { out.searchProjErr = String(e && e.message || e); }

  const assoc = out.device && out.device.association && out.device.association.model3D;
  out.ok = !!(assoc && assoc.uuid === modelUuid);
  return out;
})()
