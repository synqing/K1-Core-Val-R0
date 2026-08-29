(async () => {
  const out = {};
  const texts = [...document.querySelectorAll('input,button,div,span,li,td')].filter(el => el.offsetParent !== null);
  out.inputs = [...document.querySelectorAll('input')].filter(el => el.offsetParent !== null).map(el => ({
    value: String(el.value || '').slice(0, 80),
    ph: el.placeholder,
    title: el.title,
    cls: String(el.className || '').slice(0, 50),
  })).slice(0, 30);
  out.buttons = [...document.querySelectorAll('button, [role="button"], div')].filter(el => {
    if (el.offsetParent === null) return false;
    const t = String(el.textContent || '').replace(/\s+/g, ' ').trim();
    return t.length > 0 && t.length < 24 && /OK|Cancel|Select|Search|Personal|System|Create|New|Confirm|Associate/i.test(t);
  }).map(el => ({ tag: el.tagName, text: String(el.textContent||'').replace(/\s+/g,' ').trim(), cls: String(el.className||'').slice(0,50) })).slice(0, 25);

  const dialog = [...document.querySelectorAll('[role="dialog"], [class*="modal"], [class*="container"]')].find(el =>
    el.offsetParent !== null && /Select Device/i.test(el.textContent || '')
  );
  out.dialogText = dialog ? String(dialog.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 500) : null;
  out.rows = [...document.querySelectorAll('tr')].filter(el => el.offsetParent !== null)
    .map(el => String(el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 120))
    .slice(0, 15);
  return out;
})()
