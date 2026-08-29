(() => {
  const buttons = [...document.querySelectorAll('button, [role="button"], span, div')].filter(el => el.offsetParent !== null);
  const cancel = buttons.find(el => /^(Cancel|取消|Close|关闭)$/i.test((el.textContent || '').trim()));
  const hits = buttons.filter(el => /Export 3D|Cancel|取消|Close/i.test((el.textContent || '').trim())).slice(0, 12).map(el => (el.textContent || '').trim());
  if (cancel) {
    cancel.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    return { ok: true, clicked: (cancel.textContent || '').trim(), hits };
  }
  return { ok: false, hits };
})()
