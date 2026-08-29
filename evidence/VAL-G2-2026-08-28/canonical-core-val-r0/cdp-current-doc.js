(async () => {
  const R = window._EXTAPI_ROOT_;
  const out = {};
  try { out.doc = await R.dmt_SelectControl.getCurrentDocumentInfo(); }
  catch (e) { out.docErr = String(e && e.message || e); }
  const titles = [...document.querySelectorAll('[title],button,[aria-label]')]
    .filter(x => x.offsetParent !== null)
    .map(x => x.getAttribute('title') || x.getAttribute('aria-label'))
    .filter(t => t && /3D|2D|Preview|Fit|PCB/i.test(t))
    .slice(0, 40);
  out.titles = titles;
  out.has3dCanvas = !!document.querySelector('canvas');
  out.canvasCount = document.querySelectorAll('canvas').length;
  return out;
})()
