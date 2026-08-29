(async () => {
  const R = window._EXTAPI_ROOT_;
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const SYSTEM = '0819f05c4eef4c71ace90d822a990e87';
  const out = {};
  try { out.searchSeatedP = await R.lib_3DModel.search('seated', PERSONAL, undefined, 20, 1); }
  catch (e) { out.searchSeatedPErr = String(e && e.message || e); }
  try { out.searchHiroseP = await R.lib_3DModel.search('USB_C_Hirose', PERSONAL, undefined, 20, 1); }
  catch (e) { out.searchHirosePErr = String(e && e.message || e); }
  try { out.searchSeatedS = await R.lib_3DModel.search('seated', SYSTEM, undefined, 20, 1); }
  catch (e) { out.searchSeatedSErr = String(e && e.message || e); }
  try { out.getSeated = await R.lib_3DModel.get('08b2bb7ecebd47fc8f45f08f001d782e', PERSONAL); }
  catch (e) { out.getSeatedErr = String(e && e.message || e); }
  out.attrCreateArity = R.pcb_PrimitiveAttribute && R.pcb_PrimitiveAttribute.create && R.pcb_PrimitiveAttribute.create.length;
  try { out.attrCreateSrc = String(R.pcb_PrimitiveAttribute.create); }
  catch (e) {}
  try { out.attrModifySrc = String(R.pcb_PrimitiveAttribute.modify); }
  catch (e) {}
  try { out.attrGetAll = await R.pcb_PrimitiveAttribute.getAll(); }
  catch (e) { out.attrGetAllErr = String(e && e.message || e); }
  return out;
})()
