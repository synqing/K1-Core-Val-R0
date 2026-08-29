(async () => {
  const R = window._EXTAPI_ROOT_;
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const DEV = '7e7eac39cf44433b9710c4ae4afab424';
  const FP = '0c8e199e56e60728';
  const SEATED = '08b2bb7ecebd47fc8f45f08f001d782e';
  const TITLE = 'USB_C_Hirose_CX_4800304000_seated';
  const SYMBOL = 'c8b5c381560a4f7192aa521a21010e99';
  const out = { steps: [] };
  const note = (label, extra) => { out.steps.push({ label, ...extra }); };

  let beforeDev = null;
  try {
    beforeDev = await R.lib_Device.get(DEV, PERSONAL);
    note('get-before', {
      name: beforeDev && beforeDev.name,
      fp: beforeDev && beforeDev.association && beforeDev.association.footprint,
      model3D: beforeDev && beforeDev.association && beforeDev.association.model3D,
      other3d: beforeDev && beforeDev.property && beforeDev.property.otherProperty
        ? {
            model: beforeDev.property.otherProperty['3D Model'],
            title: beforeDev.property.otherProperty['3D Model Title'],
          }
        : null,
    });
  } catch (e) {
    note('get-before', { err: String(e && e.message || e) });
    return { ok: false, steps: out.steps };
  }

  try {
    out.modify = await R.lib_Device.modify(
      DEV,
      PERSONAL,
      undefined,
      null,
      {
        symbol: { uuid: SYMBOL, libraryUuid: PERSONAL },
        footprint: { uuid: FP, libraryUuid: PERSONAL },
        model3D: { uuid: SEATED, libraryUuid: PERSONAL },
      },
      undefined,
      {
        otherProperty: {
          '3D Model': SEATED,
          '3D Model Title': TITLE,
        },
      },
    );
    note('modify', { result: out.modify });
  } catch (e) {
    note('modify', { err: String(e && e.message || e) });
    return { ok: false, steps: out.steps };
  }

  let afterDev = null;
  try {
    afterDev = await R.lib_Device.get(DEV, PERSONAL);
    note('get-after', {
      name: afterDev && afterDev.name,
      assoc: afterDev && afterDev.association,
      other3d: afterDev && afterDev.property && afterDev.property.otherProperty
        ? {
            model: afterDev.property.otherProperty['3D Model'],
            title: afterDev.property.otherProperty['3D Model Title'],
            xf: afterDev.property.otherProperty['3D Model Transform'],
            footprint: afterDev.property.otherProperty.Footprint,
          }
        : null,
    });
  } catch (e) {
    note('get-after', { err: String(e && e.message || e) });
  }

  // Close leftover dialogs without confirming a wrong part.
  for (const btn of [...document.querySelectorAll('button')].reverse()) {
    const t = String(btn.textContent || '').trim();
    if (btn.offsetParent !== null && (t === 'Cancel' || t === 'Close')) {
      btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    }
  }
  await new Promise(r => setTimeout(r, 300));

  let tab;
  try {
    tab = await R.lib_Footprint.openInEditor(FP, PROJECT);
    note('openInEditor', { tab });
  } catch (e) {
    note('openInEditor', { err: String(e && e.message || e) });
  }
  await new Promise(r => setTimeout(r, 800));

  const field = [...document.querySelectorAll('input')].find(el =>
    el.offsetParent !== null && /3D Model/i.test(el.title || el.value || '')
  );
  if (field) {
    field.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    field.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: window }));
    note('clicked-3d-field', { value: field.value, title: field.title });
  } else {
    note('clicked-3d-field', { err: 'no field' });
  }
  await new Promise(r => setTimeout(r, 900));

  const assocBtn = [...document.querySelectorAll('button')].find(el =>
    el.offsetParent !== null && /Associated Device/i.test(el.textContent || '')
  );
  if (assocBtn) {
    assocBtn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    note('clicked-associated-device', {});
    await new Promise(r => setTimeout(r, 900));
    const search = [...document.querySelectorAll('input')].find(el =>
      el.offsetParent !== null && /Search/i.test(el.placeholder || '')
    );
    if (search) {
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
      if (setter) setter.call(search, 'CX70M-24P1');
      else search.value = 'CX70M-24P1';
      search.dispatchEvent(new Event('input', { bubbles: true }));
      search.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
      await new Promise(r => setTimeout(r, 1100));
    }
    const row = [...document.querySelectorAll('tr')].find(el =>
      el.offsetParent !== null
      && /CX70M-24P1/i.test(el.textContent || '')
      && /C778726|HRS|Personal/i.test(el.textContent || '')
    ) || [...document.querySelectorAll('tr')].find(el =>
      el.offsetParent !== null
      && /CX70M-24P1/i.test(el.textContent || '')
      && !/No\./.test(el.textContent || '')
      && String(el.textContent || '').length > 20
    );
    out.deviceRows = [...document.querySelectorAll('tr')].filter(el => el.offsetParent !== null)
      .map(el => String(el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 160)).slice(0, 15);
    if (row) {
      row.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
      note('selected-device-row', { text: String(row.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 160) });
      await new Promise(r => setTimeout(r, 200));
      const confirm = [...document.querySelectorAll('button')].find(el =>
        el.offsetParent !== null && String(el.textContent || '').trim() === 'Confirm'
      );
      if (confirm) {
        confirm.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
        note('confirmed-device', {});
      }
    } else {
      note('no-safe-device-row', {});
      const cancel = [...document.querySelectorAll('button')].find(el =>
        el.offsetParent !== null && String(el.textContent || '').trim() === 'Cancel'
      );
      if (cancel) cancel.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    }
    await new Promise(r => setTimeout(r, 700));
  } else {
    note('no-assoc-tips', {
      dialogs: [...document.querySelectorAll('[role="dialog"], .ant-modal')].filter(el => el.offsetParent !== null)
        .map(el => String(el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 120)),
    });
  }

  const seated = [...document.querySelectorAll('tr')].find(el =>
    el.offsetParent !== null && /USB_C_Hirose_CX_4800304000_seated/i.test(el.textContent || '')
  );
  if (seated) {
    seated.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    seated.dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true, view: window }));
    note('clicked-seated', { text: String(seated.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 160) });
    await new Promise(r => setTimeout(r, 300));
    const confirm3d = [...document.querySelectorAll('button')].find(el =>
      el.offsetParent !== null && String(el.textContent || '').trim() === 'Confirm'
    );
    if (confirm3d) {
      confirm3d.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
      note('confirmed-3d', {});
    }
  } else {
    note('no-seated-row', {});
  }

  await new Promise(r => setTimeout(r, 600));
  try { note('save-fp', { result: await R.dmt_EditorControl.saveActiveDocument() }); }
  catch (e) { note('save-fp', { err: String(e && e.message || e) }); }

  await new Promise(r => setTimeout(r, 400));
  const src = await R.sys_FileManager.getDocumentSource();
  const field2 = [...document.querySelectorAll('input')].find(el =>
    el.offsetParent !== null && /3D Model/i.test(el.title || el.value || '')
  );
  out.after = {
    len: src.length,
    has3D: /3D Model/.test(src),
    hasSeated: src.includes(SEATED),
    field: field2 ? { value: field2.value, title: field2.title } : null,
    doc: await R.dmt_SelectControl.getCurrentDocumentInfo(),
  };
  out.ok = !!(out.after.has3D && out.after.hasSeated);
  return out;
})()
