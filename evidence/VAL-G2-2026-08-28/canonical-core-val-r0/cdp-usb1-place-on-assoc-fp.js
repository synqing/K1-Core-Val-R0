(async () => {
  const R = window._EXTAPI_ROOT_;
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const DEV_FP = '279f06324aa142578b6ff40a12f66d9b';
  const USB1_FP = '0c8e199e56e60728';
  const SEATED = '08b2bb7ecebd47fc8f45f08f001d782e';
  const timed = (p, ms) => Promise.race([
    Promise.resolve().then(() => p).then(v => ({ ok: true, v })).catch(e => ({ ok: false, err: String(e && e.message || e) })),
    new Promise(r => setTimeout(() => r({ ok: false, timeout: ms }), ms)),
  ]);
  const out = { steps: [] };
  const note = (label, extra) => { out.steps.push({ label, ...extra }); };

  out.ping = await timed(R.dmt_SelectControl.getCurrentDocumentInfo(), 3000);

  // Cancel leftover dialogs.
  for (const btn of [...document.querySelectorAll('button')].reverse()) {
    const t = String(btn.textContent || '').trim();
    if (btn.offsetParent !== null && (t === 'Cancel' || t === 'Close')) {
      btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    }
  }
  await new Promise(r => setTimeout(r, 250));

  out.open = await timed(R.lib_Footprint.openInEditor(DEV_FP, PERSONAL), 8000);
  note('open', out.open);
  await new Promise(r => setTimeout(r, 800));
  out.doc = await timed(R.dmt_SelectControl.getCurrentDocumentInfo(), 3000);

  const before = await timed(R.sys_FileManager.getDocumentSource(), 4000);
  out.before = before.ok ? { len: before.v.length, has3D: /3D Model/.test(before.v), hasSeated: before.v.includes(SEATED) } : before;

  const field = [...document.querySelectorAll('input')].find(el =>
    el.offsetParent !== null && /3D Model/i.test(el.title || el.value || '')
  );
  if (field) {
    field.focus();
    field.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    note('field', { value: field.value, title: field.title });
  } else {
    note('field', { err: 'missing' });
  }
  await new Promise(r => setTimeout(r, 900));

  const tips = [...document.querySelectorAll('[role="dialog"], .ant-modal')].filter(el => el.offsetParent !== null)
    .map(el => String(el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 180));
  out.dialogs = tips;

  const assocBtn = [...document.querySelectorAll('button')].find(el =>
    el.offsetParent !== null && /Associated Device/i.test(el.textContent || '')
  );
  if (assocBtn) {
    note('still-needs-device', {});
    const cancel = [...document.querySelectorAll('button')].find(el =>
      el.offsetParent !== null && String(el.textContent || '').trim() === 'Cancel'
    );
    if (cancel) cancel.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  }

  const seated = [...document.querySelectorAll('tr')].find(el =>
    el.offsetParent !== null && /USB_C_Hirose_CX_4800304000_seated/i.test(el.textContent || '')
  );
  if (seated) {
    seated.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    seated.dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true, view: window }));
    note('clicked-seated', { text: String(seated.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 140) });
    await new Promise(r => setTimeout(r, 300));
    const confirm = [...document.querySelectorAll('button')].find(el =>
      el.offsetParent !== null && String(el.textContent || '').trim() === 'Confirm'
    );
    if (confirm) {
      confirm.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
      note('confirmed-3d', {});
    }
  } else {
    note('no-seated-row', {
      rows: [...document.querySelectorAll('tr')].filter(el => el.offsetParent !== null)
        .map(el => String(el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 100)).slice(0, 8),
    });
  }

  await new Promise(r => setTimeout(r, 600));
  out.saveApis = {
    pcb_Document: !!(R.pcb_Document && R.pcb_Document.save),
    sys_saveDocument: !!(R.sys_FileManager && R.sys_FileManager.saveDocument),
    sys_save: !!(R.sys_FileManager && R.sys_FileManager.save),
  };
  if (R.sys_FileManager && typeof R.sys_FileManager.saveDocument === 'function') {
    out.save = await timed(R.sys_FileManager.saveDocument(), 8000);
  } else if (R.pcb_Document && typeof R.pcb_Document.save === 'function') {
    out.save = await timed(R.pcb_Document.save(), 8000);
  } else {
    out.save = { skipped: true };
  }
  await new Promise(r => setTimeout(r, 400));
  const after = await timed(R.sys_FileManager.getDocumentSource(), 4000);
  out.after = after.ok ? {
    len: after.v.length,
    has3D: /3D Model/.test(after.v),
    hasSeated: after.v.includes(SEATED),
    sample: after.v.includes('3D Model') ? after.v.split('\n').filter(l => /3D Model/.test(l)).slice(0, 6) : [],
  } : after;

  const field2 = [...document.querySelectorAll('input')].find(el =>
    el.offsetParent !== null && /3D Model/i.test(el.title || el.value || '')
  );
  out.fieldAfter = field2 ? { value: field2.value, title: field2.title } : null;
  out.docAfter = await timed(R.dmt_SelectControl.getCurrentDocumentInfo(), 3000);
  return out;
})()
