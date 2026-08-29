(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const FP = '0c8e199e56e60728';
  const SEATED = '08b2bb7ecebd47fc8f45f08f001d782e';
  const TITLE = 'USB_C_Hirose_CX_4800304000_seated';
  const out = { steps: [] };
  const note = (label, extra) => { out.steps.push({ label, ...extra }); };

  try { await R.lib_Footprint.openInEditor(FP, PROJECT); } catch (e) { note('open', { err: String(e && e.message || e) }); }
  await new Promise(r => setTimeout(r, 400));
  out.doc = await R.dmt_SelectControl.getCurrentDocumentInfo();

  out.attrApi = R.pcb_PrimitiveAttribute ? Object.getOwnPropertyNames(Object.getPrototypeOf(R.pcb_PrimitiveAttribute)).sort() : null;
  out.fpSearchByProps = typeof R.lib_Footprint.searchByProperties;
  try { out.fpSearchByPropsSrc = String(R.lib_Footprint.searchByProperties).slice(0, 400); } catch (e) {}
  try { out.updateSrc = String(R.lib_Footprint.updateDocumentSource).slice(0, 200); } catch (e) {}

  // Visible 3D Model field after previous attempt
  const inputs = [...document.querySelectorAll('input')].filter(el => el.offsetParent !== null).map(el => ({
    value: String(el.value || '').slice(0, 80),
    title: el.title,
    placeholder: el.placeholder,
    cls: String(el.className || '').slice(0, 40),
  }));
  out.inputs = inputs.filter(i => /3D|Model|Search|Filter|seated|Hirose/i.test(JSON.stringify(i)));

  // Left-panel library tabs and filters
  const tabs = [...document.querySelectorAll('li,span,button,div')].filter(el => el.offsetParent !== null)
    .filter(el => /^(Device|Symbol|Footprint|3D Model|Panel Lib|Personal|System|LCSC|EasyEDA)$/i.test(String(el.textContent || '').trim()))
    .map(el => ({ tag: el.tagName, text: String(el.textContent||'').trim(), cls: String(el.className||'').slice(0,60) }));
  out.tabs = tabs.slice(0, 30);

  // Click Personal if present, then 3D Model tab, then search
  const clickText = (re) => {
    const el = [...document.querySelectorAll('li,span,button,div,a')].find(x =>
      x.offsetParent !== null && re.test(String(x.textContent || '').trim()) && String(x.textContent||'').trim().length < 24
    );
    if (!el) return null;
    el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    return String(el.textContent||'').trim();
  };
  note('click-3d-tab', { hit: clickText(/^3D Model$/) });
  await new Promise(r => setTimeout(r, 200));
  note('click-personal', { hit: clickText(/^Personal$/) });
  await new Promise(r => setTimeout(r, 300));

  const search = [...document.querySelectorAll('input')].find(el =>
    el.offsetParent !== null && /Search/i.test(el.placeholder || '')
  );
  if (search) {
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
    if (setter) setter.call(search, 'seated');
    else search.value = 'seated';
    search.dispatchEvent(new Event('input', { bubbles: true }));
    search.dispatchEvent(new Event('change', { bubbles: true }));
    search.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
    note('search', { value: search.value, placeholder: search.placeholder });
  } else {
    note('search', { err: 'no search' });
  }
  await new Promise(r => setTimeout(r, 1200));

  const rows = [...document.querySelectorAll('tr, [class*="row"]')].filter(el =>
    el.offsetParent !== null && /Hirose|seated|08b2bb|USB_C/i.test(el.textContent || '')
  ).map(el => String(el.textContent||'').replace(/\s+/g,' ').trim().slice(0,160));
  out.rows = rows.slice(0, 10);

  if (rows.length) {
    const el = [...document.querySelectorAll('tr, [class*="row"]')].find(x =>
      x.offsetParent !== null && /Hirose|seated|USB_C/i.test(x.textContent || '')
    );
    el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    await new Promise(r => setTimeout(r, 200));
    el.dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true, view: window }));
    note('placed-row', { text: String(el.textContent||'').replace(/\s+/g,' ').trim().slice(0,160) });
  }

  // Buttons near 3D
  const buttons = [...document.querySelectorAll('button, [role="button"], div')].filter(el => {
    if (el.offsetParent === null) return false;
    const t = String(el.textContent || el.getAttribute('title') || '').replace(/\s+/g,' ').trim();
    return t.length < 20 && /Apply|Place|OK|Add|Bind|Use|Insert|Confirm/i.test(t);
  }).map(el => ({ tag: el.tagName, text: String(el.textContent||el.title||'').replace(/\s+/g,' ').trim().slice(0,30), title: el.getAttribute('title') }));
  out.buttons = buttons.slice(0, 20);

  // Try PrimitiveAttribute.create if present
  if (R.pcb_PrimitiveAttribute && typeof R.pcb_PrimitiveAttribute.create === 'function') {
    try {
      out.attrCreate = await R.pcb_PrimitiveAttribute.create({
        key: '3D Model',
        value: SEATED,
      });
      note('attrCreate', { result: out.attrCreate });
    } catch (e) {
      note('attrCreate', { err: String(e && e.message || e), src: String(R.pcb_PrimitiveAttribute.create).slice(0, 300) });
    }
  }

  const src = await R.sys_FileManager.getDocumentSource();
  out.after = { len: src.length, has3D: /3D Model/.test(src), hasSeated: src.includes(SEATED) };
  return out;
})()
