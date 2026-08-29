(async () => {
  const out = { steps: [] };
  const note = (label, extra) => { out.steps.push({ label, ...extra }); };

  // Search the Select Device dialog for the Hirose C-number only.
  const deviceSearch = [...document.querySelectorAll('input')].find(el =>
    el.offsetParent !== null && el.placeholder && /Search/i.test(el.placeholder) && el.value === 'USB-TYPE-C-SMD_CX70M-24P1'
  ) || [...document.querySelectorAll('input')].filter(el =>
    el.offsetParent !== null && /Search/i.test(el.placeholder || '')
  ).slice(-1)[0];
  if (!deviceSearch) return { ok: false, err: 'no device search', steps: out.steps };
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
  if (setter) setter.call(deviceSearch, 'C778726');
  else deviceSearch.value = 'C778726';
  deviceSearch.dispatchEvent(new Event('input', { bubbles: true }));
  deviceSearch.dispatchEvent(new Event('change', { bubbles: true }));
  deviceSearch.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
  note('searched', { value: deviceSearch.value });
  await new Promise(r => setTimeout(r, 1200));

  const rows = [...document.querySelectorAll('tr')].filter(el => el.offsetParent !== null)
    .map(el => String(el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 160));
  out.rows = rows.slice(0, 20);
  const cx = [...document.querySelectorAll('tr')].find(el =>
    el.offsetParent !== null && /C778726|CX70M-24P1/i.test(el.textContent || '') && !/No\./.test(el.textContent || '')
  );
  if (cx) {
    cx.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    note('selected-cx', { text: String(cx.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 160) });
    await new Promise(r => setTimeout(r, 200));
    const confirm = [...document.querySelectorAll('button')].find(el =>
      el.offsetParent !== null && String(el.textContent || '').trim() === 'Confirm'
    );
    if (confirm) {
      confirm.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
      note('confirmed-device', {});
    }
  } else {
    note('no-cx-row', {});
    // Do not confirm a wrong part. Cancel the device picker.
    const cancel = [...document.querySelectorAll('button')].find(el =>
      el.offsetParent !== null && String(el.textContent || '').trim() === 'Cancel'
    );
    if (cancel) {
      cancel.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
      note('cancelled-device-picker', {});
    }
  }
  await new Promise(r => setTimeout(r, 800));

  // Select the seated STEP in the 3D Model Manager if it is usable now.
  const seated = [...document.querySelectorAll('tr')].find(el =>
    el.offsetParent !== null && /USB_C_Hirose_CX_4800304000_seated/i.test(el.textContent || '')
  );
  if (seated) {
    seated.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    seated.dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true, view: window }));
    note('clicked-seated-row', { text: String(seated.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 160) });
  } else {
    note('no-seated-row', {});
  }
  await new Promise(r => setTimeout(r, 400));

  const confirm3d = [...document.querySelectorAll('button')].find(el =>
    el.offsetParent !== null && String(el.textContent || '').trim() === 'Confirm'
  );
  if (confirm3d) {
    confirm3d.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    note('confirmed-3d', {});
  }

  await new Promise(r => setTimeout(r, 500));
  const R = window._EXTAPI_ROOT_;
  const src = await R.sys_FileManager.getDocumentSource();
  out.after = {
    len: src.length,
    has3D: /3D Model/.test(src),
    hasSeated: src.includes('08b2bb7ecebd47fc8f45f08f001d782e'),
    doc: await R.dmt_SelectControl.getCurrentDocumentInfo(),
  };
  const field = [...document.querySelectorAll('input')].find(el =>
    el.offsetParent !== null && /3D Model/i.test(el.title || el.value || '')
  );
  out.field = field ? { value: field.value, title: field.title } : null;
  out.dialogs = [...document.querySelectorAll('[role="dialog"], .ant-modal')].filter(el => el.offsetParent !== null)
    .map(el => String(el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 160));
  return out;
})()
