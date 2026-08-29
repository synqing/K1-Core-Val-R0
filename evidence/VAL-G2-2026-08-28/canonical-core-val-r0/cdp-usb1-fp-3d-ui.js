(async () => {
  const R = window._EXTAPI_ROOT_;
  const out = {};
  try { out.doc = await R.dmt_SelectControl.getCurrentDocumentInfo(); }
  catch (e) { out.docErr = String(e && e.message || e); }

  const src = await R.sys_FileManager.getDocumentSource();
  out.sourceLen = src.length;
  out.has3DModel = /3D Model/.test(src);
  out.primitiveSample = [];
  const re = /\{"type":"PRIMITIVE".{0,500}/g;
  let m;
  while ((m = re.exec(src)) && out.primitiveSample.length < 8) {
    out.primitiveSample.push(m[0]);
  }
  const modelish = [];
  for (const line of src.split('\n')) {
    if (/3D|model|Model|OFFSET|offset/i.test(line)) modelish.push(line.slice(0, 240));
  }
  out.modelishLines = modelish.slice(0, 30);

  const nodes = [...document.querySelectorAll('*')].filter(el => el.offsetParent !== null);
  const hits = [];
  for (const el of nodes) {
    const t = (el.getAttribute('title') || el.getAttribute('aria-label') || el.textContent || '');
    if (!t) continue;
    const s = String(t).replace(/\s+/g, ' ').trim();
    if (s.length > 80) continue;
    if (/3D Model|Offset|Rotation|Apply|Height|Auto/i.test(s)) {
      hits.push({
        tag: el.tagName,
        cls: String(el.className || '').slice(0, 80),
        title: el.getAttribute('title'),
        aria: el.getAttribute('aria-label'),
        text: s.slice(0, 80),
        input: el.tagName === 'INPUT' ? { type: el.type, value: el.value, name: el.name } : undefined,
      });
    }
  }
  out.hits = hits.slice(0, 60);

  const inputs = [...document.querySelectorAll('input,textarea,[contenteditable="true"]')]
    .filter(el => el.offsetParent !== null)
    .map(el => ({
      tag: el.tagName,
      type: el.type,
      name: el.name,
      placeholder: el.placeholder,
      value: String(el.value || el.textContent || '').slice(0, 80),
      aria: el.getAttribute('aria-label'),
      title: el.getAttribute('title'),
    }));
  out.inputs = inputs.slice(0, 40);

  return out;
})()
