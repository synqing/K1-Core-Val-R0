(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const PERSONAL = '27700277ef7a49e48a0293bece6b2993';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const FP = '0c8e199e56e60728';
  const SEATED = '08b2bb7ecebd47fc8f45f08f001d782e';
  const TITLE = 'USB_C_Hirose_CX_4800304000_seated';
  const XF = '448.8179849815368,328.7394915521145,0,0,0,0,0,-66.733,-80.315';
  const out = { steps: [] };
  const note = (label, extra) => { out.steps.push({ label, ...extra }); };

  try { await R.dmt_EditorControl.activateDocument(PCB + '@' + PROJECT); } catch (e) {}
  await new Promise(r => setTimeout(r, 400));
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const usb1 = comps.find(c => c.getState_Designator() === 'USB1');
  const usb2 = comps.find(c => c.getState_Designator() === 'USB2');
  const u6 = comps.find(c => c.getState_Designator() === 'U6-RTC');
  if (usb1.getState_SupplierId() !== 'C778726' || usb1.getState_ManufacturerId() !== 'CX70M-24P1') {
    return { ok: false, err: 'identity' };
  }
  const component = usb1.getState_Component();
  const other = usb1.getState_OtherProperty() || {};
  out.before = {
    usb1: { sid: usb1.getState_SupplierId(), mid: usb1.getState_ManufacturerId(), component, model: other['3D Model'], xf: other['3D Model Transform'] },
    usb2: { model: (usb2.getState_OtherProperty() || {})['3D Model'], xf: (usb2.getState_OtherProperty() || {})['3D Model Transform'] },
    u6: { model: (u6.getState_OtherProperty() || {})['3D Model'], xf: (u6.getState_OtherProperty() || {})['3D Model Transform'] },
  };

  const association = {
    footprint: { uuid: FP, libraryUuid: PERSONAL },
    model3D: { uuid: SEATED, libraryUuid: PERSONAL },
  };
  const property = {
    manufacturerId: 'CX70M-24P1',
    supplier: 'LCSC',
    supplierId: 'C778726',
    otherProperty: {
      '3D Model': SEATED,
      '3D Model Title': TITLE,
      '3D Model Transform': XF,
    },
  };

  const tryMod = async (label, uuid, lib) => {
    try {
      const result = await R.lib_Device.modify(uuid, lib, undefined, null, association, undefined, property);
      note(label, { result, uuid, lib });
      return result;
    } catch (e) {
      note(label, { err: String(e && e.message || e), uuid, lib });
      return false;
    }
  };

  await tryMod('modify-component-project', component.uuid, component.libraryUuid || PROJECT);
  await tryMod('modify-component-personal', component.uuid, PERSONAL);
  await tryMod('modify-fp-as-device-personal', FP, PERSONAL);

  // Re-open footprint 3D manager to see if the associate-device block cleared.
  try { await R.lib_Footprint.openInEditor(FP, PROJECT); } catch (e) { note('reopen-fp', { err: String(e && e.message || e) }); }
  await new Promise(r => setTimeout(r, 600));
  const field = [...document.querySelectorAll('input')].find(el =>
    el.offsetParent !== null && (el.title === '<3D Model>' || String(el.value || '').includes('3D Model') || el.value === TITLE)
  );
  if (field) {
    field.click();
    field.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    note('clicked-field', { value: field.value, title: field.title });
  }
  await new Promise(r => setTimeout(r, 700));
  out.dialogs = [...document.querySelectorAll('[role="dialog"], .ant-modal, [class*="tips"], [class*="modal"]')]
    .filter(el => el.offsetParent !== null)
    .map(el => String(el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 220))
    .slice(0, 8);

  const assocBtn = [...document.querySelectorAll('button,div,span')].find(el =>
    el.offsetParent !== null && String(el.textContent || '').trim() === 'Associated Device'
  );
  if (assocBtn) {
    assocBtn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    note('clicked-associated-device', {});
    await new Promise(r => setTimeout(r, 800));
    out.dialogsAfterAssocClick = [...document.querySelectorAll('[role="dialog"], .ant-modal, [class*="tips"], [class*="modal"]')]
      .filter(el => el.offsetParent !== null)
      .map(el => String(el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 220))
      .slice(0, 8);
  }

  out.doc = await R.dmt_SelectControl.getCurrentDocumentInfo();
  return out;
})()
