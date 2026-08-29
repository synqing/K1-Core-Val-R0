(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const TARGET = '54d2a25bce4b44c3af878e8b91af3554';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== TARGET) return { stop: true, reason: 'NOT_IMPORT', uuid: current && current.uuid };
  if ([LIVE, HUB].includes(current.uuid)) return { stop: true, reason: 'FORBIDDEN' };

  const c2 = await eda.sch_PrimitiveComponent.get('e108');
  const rcc2s = await eda.sch_PrimitiveComponent.get('e125');
  const capRef = c2.component;
  const rRef = rcc2s && rcc2s.component
    ? rcc2s.component
    : { libraryUuid: capRef.libraryUuid, uuid: '2f462e4da9be832666742cf63c5d4f22' };

  let c1;
  try {
    c1 = await eda.sch_PrimitiveComponent.create(capRef, 115, 4420, '', 0, false, true, false);
  } catch (e) {
    return { stop: true, reason: 'C1_CREATE_FAIL', err: String(e && e.message || e).slice(0, 200), capRef };
  }
  let rcc;
  try {
    rcc = await eda.sch_PrimitiveComponent.create(rRef, 265, 3995, '', 0, false, false, false);
  } catch (e) {
    return {
      stop: true,
      reason: 'RCC_CREATE_FAIL',
      err: String(e && e.message || e).slice(0, 200),
      c1Id: c1 && (c1.primitiveId || c1.id),
      rRef,
    };
  }

  const c1Id = (c1 && (c1.primitiveId || c1.id)) || String(c1);
  const rId = (rcc && (rcc.primitiveId || rcc.id)) || String(rcc);
  return {
    capRef,
    rRef: { libraryUuid: rRef.libraryUuid, uuid: rRef.uuid, name: rRef.name },
    c1Id,
    rId,
    c1Type: typeof c1,
    rType: typeof rcc,
    c1Keys: c1 && typeof c1 === 'object' ? Object.keys(c1).slice(0, 16) : null,
  };
})()
