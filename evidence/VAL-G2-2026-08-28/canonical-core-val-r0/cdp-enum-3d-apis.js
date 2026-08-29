(async () => {
  const R = window._EXTAPI_ROOT_;
  const names = (obj, limit = 80) => {
    const keys = [];
    let p = obj;
    while (p && keys.length < limit) {
      for (const k of Object.getOwnPropertyNames(p)) keys.push(k);
      p = Object.getPrototypeOf(p);
    }
    return [...new Set(keys)].filter(k => /3d|3D|preview|model|Model|refresh|update|rebuild|transform/i.test(k) || true).slice(0, limit);
  };
  const filter = (arr) => arr.filter(k => /3d|3D|preview|Preview|model|Model|refresh|update|rebuild|camera|fit/i.test(k));
  return {
    root3d: Object.keys(R).filter(k => /3d|3D|preview|Preview/i.test(k)),
    pcbDoc: filter(names(R.pcb_Document, 200)),
    pcbComp: filter(names(R.pcb_PrimitiveComponent, 200)),
    editor: filter(names(R.dmt_EditorControl, 200)),
    header: filter(names(R.sys_HeaderMenu || {}, 80)),
    view: filter(names(R.pcb_ViewControl || R.dmt_ViewControl || {}, 80)),
  };
})()
