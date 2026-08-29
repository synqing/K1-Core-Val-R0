(() => {
  const keys = [];
  for (const k of Object.keys(window)) {
    if (/three|THREE|eda|viewer|WebGL|scene/i.test(k)) keys.push(k);
  }
  const three = window.THREE ? Object.keys(window.THREE).slice(0, 20) : null;
  let canvases = [...document.querySelectorAll('canvas')].map(c => ({
    w: c.width, h: c.height, cls: c.className, id: c.id,
  }));
  const hooks = [];
  const walk = (obj, prefix, depth) => {
    if (!obj || depth > 2) return;
    for (const k of Object.keys(obj)) {
      if (/scene|camera|mesh|usb|model3d|transform/i.test(k)) hooks.push(prefix + k);
    }
  };
  walk(window, 'window.', 1);
  if (window._EXTAPI_ROOT_) walk(window._EXTAPI_ROOT_, 'R.', 1);
  return { keys: keys.slice(0, 40), three, canvases, hooks: hooks.slice(0, 40) };
})()
