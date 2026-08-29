(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const proj = info && (info.uuid || info.projectUuid);
  if (proj === LIVE) return { stop: true, reason: 'LIVE_FOCUSED', proj };
  const doc = eda.dmt_EditorControl.getCurrentDocumentUuid
    ? await eda.dmt_EditorControl.getCurrentDocumentUuid()
    : null;
  const deviceMethods = Object.getOwnPropertyNames(Object.getPrototypeOf(eda.lib_Device)).filter((n) => n !== 'constructor');
  const fpMethods = Object.getOwnPropertyNames(Object.getPrototypeOf(eda.lib_Footprint)).filter((n) => n !== 'constructor');
  const SYS = '0819f05c4eef4c71ace90d822a990e87';
  const cacheDev = await eda.lib_Device.get('5dc457597e3143e4a20f9524f559bd07', SYS);
  const cacheFp = await eda.lib_Footprint.get('1cad738ee1594315b752ff008a616130', SYS);
  const cacheSym = await eda.lib_Symbol.get('f53e9740f767419fb71147aacf36c525', SYS);
  const indDev = await eda.lib_Device.get('64a4890ac65a4002b950d8b07c8459df', '27700277ef7a49e48a0293bece6b2993');
  function slim(item) {
    if (!item) return null;
    const assoc = item.association || {};
    return {
      uuid: item.uuid,
      name: item.name,
      keys: Object.keys(item),
      assocKeys: Object.keys(assoc),
      symbolUuid: assoc.symbolUuid || assoc.symbol || (item.property && item.property.Symbol),
      footprintUuid: assoc.footprintUuid || assoc.footprint || (item.property && item.property.Footprint),
      property: item.property || null,
      subPartNames: item.subPartNames || null,
    };
  }
  function fpPads(fp) {
    if (!fp) return null;
    const pads = fp.pads || fp.pad || fp.primitives || null;
    return {
      keys: Object.keys(fp),
      name: fp.name,
      padCount: Array.isArray(pads) ? pads.length : null,
      padNums: Array.isArray(pads)
        ? pads.map((p) => p.padNumber || p.number || p.name).slice(0, 40)
        : null,
    };
  }
  return {
    proj,
    friendly: info && (info.friendlyName || info.name),
    doc,
    hubOk: proj === HUB,
    deviceMethods,
    fpMethods,
    cacheDev: slim(cacheDev),
    cacheSym: slim(cacheSym),
    cacheFp: fpPads(cacheFp),
    indDev: slim(indDev),
  };
})()
