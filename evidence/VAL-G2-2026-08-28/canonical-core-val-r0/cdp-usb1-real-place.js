(async () => {
  const R = window._EXTAPI_ROOT_;
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

  out.doc = await R.dmt_SelectControl.getCurrentDocumentInfo();

  // Close 3D Model Manager if present.
  const manager = [...document.querySelectorAll('*')].find(el =>
    el.offsetParent !== null && String(el.textContent || '').trim() === '3D Model Manager'
  );
  out.hasManager = !!manager;
  const closeX = [...document.querySelectorAll('button,[aria-label],span,div')].find(el => {
    if (el.offsetParent === null) return false;
    const a = el.getAttribute('aria-label') || el.getAttribute('title') || '';
    const t = String(el.textContent || '').trim();
    return /close|关闭/i.test(a) || t === '×' || t === 'X';
  });
  if (closeX) { click(closeX); note('close-x', { title: closeX.getAttribute('title'), aria: closeX.getAttribute('aria-label'), t: String(closeX.textContent||'').trim() }); }
  const cancel = [...document.querySelectorAll('button')].find(el =>
    el.offsetParent !== null && String(el.textContent || '').trim() === 'Cancel'
  );
  if (cancel) { click(cancel); note('cancel', {}); }
  await new Promise(r => setTimeout(r, 300));

  const place = [...document.querySelectorAll('div,button')].find(el =>
    el.offsetParent !== null && String(el.className || '').includes('eda-menu-btn') && String(el.textContent || '').trim() === 'Place'
  );
  out.place = place ? { cls: String(place.className).slice(0, 80), text: String(place.textContent).trim() } : null;
  if (place) { click(place); note('place-menu-btn', {}); }
  await new Promise(r => setTimeout(r, 400));

  const canvases = [...document.querySelectorAll('canvas')].map(c => {
    const r = c.getBoundingClientRect();
    return { w: c.width, h: c.height, cw: r.width, ch: r.height, cls: String(c.className||'').slice(0, 60) };
  });
  out.canvases = canvases;
  const main = [...document.querySelectorAll('canvas')].sort((a, b) =>
    (b.getBoundingClientRect().width * b.getBoundingClientRect().height) - (a.getBoundingClientRect().width * a.getBoundingClientRect().height)
  )[0];
  if (main) {
    const r = main.getBoundingClientRect();
    const x = r.left + r.width / 2;
    const y = r.top + r.height / 2;
    for (const type of ['pointerdown', 'mousedown', 'mouseup', 'pointerup', 'click']) {
      main.dispatchEvent(new MouseEvent(type, { bubbles: true, cancelable: true, view: window, clientX: x, clientY: y, button: 0 }));
    }
    note('main-canvas', { x, y, w: r.width, h: r.height });
  }

  await new Promise(r => setTimeout(r, 500));
  const src = await R.sys_FileManager.getDocumentSource();
  out.after = { len: src.length, has3D: /3D Model/.test(src), hasSeated: src.includes(SEATED) };
  const field = [...document.querySelectorAll('input')].find(el =>
    el.offsetParent !== null && /3D Model/i.test(el.title || el.value || '')
  );
  out.field = field ? { value: field.value, title: field.title } : null;
  out.buttons = [...document.querySelectorAll('button,div')].filter(el => {
    if (el.offsetParent === null) return false;
    const t = String(el.textContent || '').replace(/\s+/g, ' ').trim();
    return t.length > 0 && t.length < 18 && /Place|Apply|Confirm|OK|3D/i.test(t);
  }).map(el => ({ tag: el.tagName, t: String(el.textContent||'').trim(), cls: String(el.className||'').slice(0, 50) })).slice(0, 20);
  return out;
})()
