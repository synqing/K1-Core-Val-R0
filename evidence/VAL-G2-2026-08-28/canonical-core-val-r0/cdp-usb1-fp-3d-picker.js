(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const FP = '0c8e199e56e60728';
  const out = { steps: [] };
  const note = (label, extra) => { out.steps.push({ label, ...extra }); };
  try { await R.lib_Footprint.openInEditor(FP, PROJECT); } catch (e) {}
  await new Promise(r => setTimeout(r, 400));
  out.doc = await R.dmt_SelectControl.getCurrentDocumentInfo();

  const field = [...document.querySelectorAll('input')].find(el =>
    el.offsetParent !== null && (el.title === '<3D Model>' || el.value === '<3D Model>')
  );
  note('field', field ? { value: field.value, title: field.title } : { err: 'missing' });
  if (field) {
    field.focus();
    field.click();
    field.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    field.dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true, view: window }));
  }
  await new Promise(r => setTimeout(r, 600));

  const dialogs = [...document.querySelectorAll('[role="dialog"], .ant-modal, .el-dialog, [class*="modal"], [class*="dialog"]')]
    .filter(el => el.offsetParent !== null)
    .map(el => String(el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 240));
  out.dialogs = dialogs;

  const placeBtns = [...document.querySelectorAll('div,button,span')].filter(el =>
    el.offsetParent !== null && String(el.textContent || '').trim() === 'Place'
  );
  note('place-count', { n: placeBtns.length });
  if (placeBtns.length) {
    placeBtns[0].dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    note('clicked-place', { cls: String(placeBtns[0].className || '').slice(0, 80) });
  }

  // Click the left-library Personal LI specifically (not the property-panel Personal).
  const personalLi = [...document.querySelectorAll('li')].find(el =>
    el.offsetParent !== null && String(el.textContent || '').trim() === 'Personal'
  );
  if (personalLi) {
    personalLi.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    note('clicked-personal-li', { cls: String(personalLi.className || '').slice(0, 80) });
  }
  await new Promise(r => setTimeout(r, 400));

  const searchBoxes = [...document.querySelectorAll('input')].filter(el =>
    el.offsetParent !== null && /Search/i.test(el.placeholder || '')
  ).map(el => ({ ph: el.placeholder, val: el.value, cls: String(el.className||'').slice(0,40) }));
  out.searchBoxes = searchBoxes;

  const titles = [...document.querySelectorAll('[title]')].filter(el => el.offsetParent !== null)
    .map(el => el.getAttribute('title')).filter(t => t && /3D|Model|Place|Apply|Personal/i.test(t)).slice(0, 30);
  out.titles = titles;
  return out;
})()
