(async () => {
  const R = window._EXTAPI_ROOT_;
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const DEV_FP = '279f06324aa142578b6ff40a12f66d9b';
  const SEATED = '08b2bb7ecebd47fc8f45f08f001d782e';
  const out = { steps: [] };
  const note = (label, extra) => { out.steps.push({ label, ...extra }); };
  const click = (el) => {
    if (!el) return false;
    el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: window }));
    el.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, view: window }));
    el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    return true;
  };

  let doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  if (!doc || doc.uuid !== DEV_FP) {
    await R.lib_Footprint.openInEditor(DEV_FP, PERSONAL);
    await new Promise(r => setTimeout(r, 700));
    doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  }
  out.doc = doc;

  // Close manager dialogs so the left library is usable.
  for (const btn of [...document.querySelectorAll('button')].reverse()) {
    const t = String(btn.textContent || '').trim();
    if (btn.offsetParent !== null && (t === 'Cancel' || t === 'Close')) click(btn);
  }
  await new Promise(r => setTimeout(r, 200));

  const clickExact = (re, maxLen = 24) => {
    const el = [...document.querySelectorAll('li,span,button,div,a')].find(x =>
      x.offsetParent !== null && re.test(String(x.textContent || '').trim()) && String(x.textContent || '').trim().length < maxLen
    );
    if (el) click(el);
    return el ? String(el.textContent || '').trim() : null;
  };
  note('tab-3d', { hit: clickExact(/^3D Model$/) });
  await new Promise(r => setTimeout(r, 200));
  note('tab-personal', { hit: clickExact(/^Personal$/) });
  await new Promise(r => setTimeout(r, 400));

  const search = [...document.querySelectorAll('input')].find(el =>
    el.offsetParent !== null && /Search/i.test(el.placeholder || '')
  );
  if (search) {
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
    if (setter) setter.call(search, 'seated');
    else search.value = 'seated';
    search.dispatchEvent(new Event('input', { bubbles: true }));
    search.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
    note('search', { value: search.value });
  }
  await new Promise(r => setTimeout(r, 1100));

  const row = [...document.querySelectorAll('tr')].find(el =>
    el.offsetParent !== null && /USB_C_Hirose_CX_4800304000_seated/i.test(el.textContent || '')
  );
  out.rows = [...document.querySelectorAll('tr')].filter(el => el.offsetParent !== null)
    .map(el => String(el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 140)).slice(0, 12);
  if (row) {
    click(row);
    note('row', { text: String(row.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 140) });
  } else {
    note('row', { err: 'none' });
  }
  await new Promise(r => setTimeout(r, 200));

  const placeBtns = [...document.querySelectorAll('div,button')].filter(el => {
    if (el.offsetParent === null) return false;
    const t = String(el.textContent || '').replace(/\s+/g, ' ').trim();
    return t === 'Place';
  }).map(el => ({
    tag: el.tagName,
    cls: String(el.className || '').slice(0, 80),
    disabled: el.getAttribute('disabled') || el.className.includes('disabled'),
  }));
  out.placeBtns = placeBtns;
  const place = [...document.querySelectorAll('div,button')].find(el =>
    el.offsetParent !== null && String(el.textContent || '').trim() === 'Place'
  );
  if (place) {
    click(place);
    note('place', { cls: String(place.className || '').slice(0, 80) });
  } else {
    note('place', { err: 'no Place' });
  }
  await new Promise(r => setTimeout(r, 400));

  // Click canvas centre in case Place armed a tool.
  const canvas = document.querySelector('canvas');
  out.canvas = canvas ? { w: canvas.width, h: canvas.height, cls: String(canvas.className || '').slice(0, 60) } : null;
  if (canvas) {
    const r = canvas.getBoundingClientRect();
    const x = r.left + r.width / 2;
    const y = r.top + r.height / 2;
    const ev = (type) => canvas.dispatchEvent(new MouseEvent(type, {
      bubbles: true, cancelable: true, view: window, clientX: x, clientY: y, button: 0,
    }));
    ev('mousedown'); ev('mouseup'); ev('click');
    note('canvas-click', { x, y });
  }

  await new Promise(r => setTimeout(r, 500));
  if (R.pcb_Document && typeof R.pcb_Document.save === 'function') {
    try { out.save = await R.pcb_Document.save(); } catch (e) { out.save = String(e && e.message || e); }
  }
  const src = await R.sys_FileManager.getDocumentSource();
  out.after = {
    len: src.length,
    has3D: /3D Model/.test(src),
    hasSeated: src.includes(SEATED),
    types: (() => {
      const c = {};
      const re = /\{"type":"([A-Z0-9_]+)"/g;
      let m;
      while ((m = re.exec(src))) c[m[1]] = (c[m[1]] || 0) + 1;
      return c;
    })(),
  };
  const field = [...document.querySelectorAll('input')].find(el =>
    el.offsetParent !== null && /3D Model/i.test(el.title || el.value || '')
  );
  out.field = field ? { value: field.value, title: field.title } : null;
  out.dialogs = [...document.querySelectorAll('[role="dialog"], .ant-modal')].filter(el => el.offsetParent !== null)
    .map(el => String(el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 140));
  return out;
})()
