(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const TAB = PAGE + '@' + HUB;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const a = await eda.sch_SelectControl.doSelectPrimitives(['e72', 'e108'], TAB);
  const ids = await eda.sch_SelectControl.getSelectedPrimitives_PrimitiveId(TAB);
  const ids2 = await eda.sch_SelectControl.getAllSelectedPrimitives_PrimitiveId(TAB);
  return { proj: info.uuid, doSelect: a, ids, ids2 };
})()
