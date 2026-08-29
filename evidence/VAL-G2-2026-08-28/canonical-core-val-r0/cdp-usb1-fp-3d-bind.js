(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const FP = '0c8e199e56e60728';
  const SEATED = '08b2bb7ecebd47fc8f45f08f001d782e';
  const TITLE = 'USB_C_Hirose_CX_4800304000_seated';
  const XF = '448.8179849815368,328.7394915521145,0,0,0,0,0,-66.733,-80.315';
  const out = { steps: [] };

  const note = (label, extra) => { out.steps.push({ label, ...extra }); };

  let tab;
  try {
    tab = await R.lib_Footprint.openInEditor(FP, PROJECT);
    note('openInEditor-project', { tab });
  } catch (e) {
    note('openInEditor-project', { err: String(e && e.message || e) });
    throw e;
  }
  await new Promise(r => setTimeout(r, 700));
  const doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  note('doc', { doc });
  if (!doc || doc.uuid !== FP) {
    return { ok: false, err: 'footprint editor not active', doc, steps: out.steps };
  }

  const before = await R.sys_FileManager.getDocumentSource();
  note('before', {
    len: before.length,
    has3D: /3D Model/.test(before),
    hasSeated: before.includes(SEATED),
  });

  // Inject footprint-owned 3D attrs into META records (document-level, not instance transform).
  let patched = before;
  patched = patched.replace(
    /\{"type":"META"[^\n]*\}\|\|\{[^\n]*\}/g,
    (block) => {
      if (block.includes('"3D Model"')) return block;
      return block.replace(/("source":"[^"]*")/, `$1,"3D Model":"${SEATED}","3D Model Title":"${TITLE}","3D Model Transform":"${XF}"`);
    }
  );

  // Also add ATTR rows after Designator if missing.
  if (!patched.includes('"key":"3D Model"')) {
    const attr = [
      `{"type":"ATTR","ticket":9001,"id":"e3d1"}||{"groupId":0,"parentId":"","layerId":3,"x":null,"y":null,"key":"3D Model","value":"${SEATED}","keyVisible":false,"valueVisible":false,"fontFamily":"default","fontSize":67.5,"strokeWidth":6,"bold":false,"italic":false,"origin":"LEFT_BOTTOM","angle":0,"reverse":false,"expansion":0,"mirror":false,"locked":false,"zIndex":200}`,
      `{"type":"ATTR","ticket":9002,"id":"e3d2"}||{"groupId":0,"parentId":"","layerId":3,"x":null,"y":null,"key":"3D Model Title","value":"${TITLE}","keyVisible":false,"valueVisible":false,"fontFamily":"default","fontSize":67.5,"strokeWidth":6,"bold":false,"italic":false,"origin":"LEFT_BOTTOM","angle":0,"reverse":false,"expansion":0,"mirror":false,"locked":false,"zIndex":201}`,
      `{"type":"ATTR","ticket":9003,"id":"e3d3"}||{"groupId":0,"parentId":"","layerId":3,"x":null,"y":null,"key":"3D Model Transform","value":"${XF}","keyVisible":false,"valueVisible":false,"fontFamily":"default","fontSize":67.5,"strokeWidth":6,"bold":false,"italic":false,"origin":"LEFT_BOTTOM","angle":0,"reverse":false,"expansion":0,"mirror":false,"locked":false,"zIndex":202}`,
    ].join('\n');
    patched = patched.replace(
      /("key":"Designator","value":"U\?"[^\n]*\})/,
      `$1|\n${attr}`
    );
  }
  note('patched', {
    len: patched.length,
    changed: patched !== before,
    has3D: /3D Model/.test(patched),
    hasSeated: patched.includes(SEATED),
  });

  try {
    out.updateDocumentSource = await R.lib_Footprint.updateDocumentSource(FP, PROJECT, patched);
    note('updateDocumentSource-project', { result: out.updateDocumentSource });
  } catch (e) {
    note('updateDocumentSource-project', { err: String(e && e.message || e) });
    try {
      out.updateDocumentSourcePersonal = await R.lib_Footprint.updateDocumentSource(FP, PERSONAL, patched);
      note('updateDocumentSource-personal', { result: out.updateDocumentSourcePersonal });
    } catch (e2) {
      note('updateDocumentSource-personal', { err: String(e2 && e2.message || e2) });
    }
  }

  if (typeof R.sys_FileManager.setDocumentSource === 'function') {
    try {
      out.setDocumentSource = await R.sys_FileManager.setDocumentSource(patched);
      note('setDocumentSource', { result: out.setDocumentSource });
    } catch (e) {
      note('setDocumentSource', { err: String(e && e.message || e) });
    }
  }

  // Property-panel apply: set the visible 3D Model field so the builder runs OFFSET.
  try {
    const input = [...document.querySelectorAll('input')].find(el =>
      el.offsetParent !== null && (el.title === '<3D Model>' || el.value === '<3D Model>' || el.value === '' && el.className.includes('input_'))
    );
    const named = [...document.querySelectorAll('input')].find(el =>
      el.offsetParent !== null && String(el.title || el.value || '').includes('3D Model')
    );
    const target = named || input;
    if (target) {
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
      if (setter) setter.call(target, TITLE);
      else target.value = TITLE;
      target.dispatchEvent(new Event('input', { bubbles: true }));
      target.dispatchEvent(new Event('change', { bubbles: true }));
      target.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
      target.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', bubbles: true }));
      note('property-panel', { value: target.value, title: target.title });
    } else {
      note('property-panel', { err: 'no 3D Model input' });
    }
  } catch (e) {
    note('property-panel', { err: String(e && e.message || e) });
  }

  // Library search + first-row click as a second apply path.
  try {
    const search = [...document.querySelectorAll('input')].find(el =>
      el.offsetParent !== null && /Search, at lease/i.test(el.placeholder || '')
    );
    if (search) {
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
      if (setter) setter.call(search, 'USB_C_Hirose_CX_4800304000_seated');
      else search.value = 'USB_C_Hirose_CX_4800304000_seated';
      search.dispatchEvent(new Event('input', { bubbles: true }));
      search.dispatchEvent(new Event('change', { bubbles: true }));
      search.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
      await new Promise(r => setTimeout(r, 900));
      const row = [...document.querySelectorAll('tr, .lc-table-row, [class*="row"]')].find(el =>
        el.offsetParent !== null && /USB_C_Hirose_CX_4800304000_seated|08b2bb7e/i.test(el.textContent || '')
      );
      if (row) {
        row.dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true, view: window }));
        note('library-row', { text: String(row.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 160) });
      } else {
        note('library-row', { err: 'no seated row', sample: [...document.querySelectorAll('tr')].slice(0, 5).map(t => String(t.textContent||'').replace(/\s+/g,' ').trim().slice(0,80)) });
      }
    } else {
      note('library-search', { err: 'no search box' });
    }
  } catch (e) {
    note('library-search', { err: String(e && e.message || e) });
  }

  await new Promise(r => setTimeout(r, 500));

  const trySave = async (label, fn) => {
    try { note(label, { result: await fn() }); }
    catch (e) { note(label, { err: String(e && e.message || e) }); }
  };
  if (R.pcb_Document && typeof R.pcb_Document.save === 'function') {
    await trySave('pcb_Document.save', () => R.pcb_Document.save());
  }
  if (R.dmt_EditorControl && typeof R.dmt_EditorControl.saveActiveDocument === 'function') {
    await trySave('saveActiveDocument', () => R.dmt_EditorControl.saveActiveDocument());
  }

  await new Promise(r => setTimeout(r, 400));
  const after = await R.sys_FileManager.getDocumentSource();
  out.after = {
    len: after.length,
    has3D: /3D Model/.test(after),
    hasSeated: after.includes(SEATED),
    hasTransform: after.includes('-80.315'),
    doc: await R.dmt_SelectControl.getCurrentDocumentInfo(),
  };

  // Read back footprint file
  try {
    const f = await R.sys_FileManager.getFootprintFileByFootprintUuid(FP, PROJECT, 'elibz2');
    out.afterFile = f ? { name: f.name, size: f.size } : { empty: true };
  } catch (e) {
    out.afterFileErr = String(e && e.message || e);
  }

  out.ok = !!(out.after.has3D && out.after.hasSeated);
  return out;
})()
