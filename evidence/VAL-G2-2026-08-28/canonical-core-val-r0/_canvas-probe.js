(() => {
  const all = [...document.querySelectorAll('canvas')].map(c => {
    const r = c.getBoundingClientRect();
    return {
      w: c.width, h: c.height, dw: r.width, dh: r.height,
      x: r.left, y: r.top, vis: c.offsetParent !== null,
      cls: c.className, id: c.id,
    };
  });
  return { n: all.length, all };
})()
