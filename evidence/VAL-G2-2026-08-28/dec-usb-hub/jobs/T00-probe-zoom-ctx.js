(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const TAB = PAGE + '@' + HUB;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  const iframes = Array.from(document.querySelectorAll('iframe')).map((el) => ({
    name: el.name || '',
    id: el.id || '',
    src: String(el.src || '').slice(0, 120),
    w: el.clientWidth,
    h: el.clientHeight,
    className: String(el.className || '').slice(0, 80),
  }));
  const hasZoom = !!(eda && eda.dmt_EditorControl && eda.dmt_EditorControl.zoomToSelectedPrimitives);
  const hasSelect = !!(eda && eda.sch_SelectControl && eda.sch_SelectControl.doSelectPrimitives);
  return {
    proj: info && info.uuid,
    tab: TAB,
    iframeCount: iframes.length,
    iframes,
    hasZoom,
    hasSelect,
    zoomKeys: eda && eda.dmt_EditorControl
      ? Object.getOwnPropertyNames(Object.getPrototypeOf(eda.dmt_EditorControl)).filter((n) => /zoom|select|fit/i.test(n))
      : [],
  };
})()
