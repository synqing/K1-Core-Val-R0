(async () => {
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const EC = eda.dmt_EditorControl;
  const proto = Object.getOwnPropertyNames(Object.getPrototypeOf(EC) || {});
  const keys = Object.keys(EC);
  return { proto: proto.filter((k) => /zoom|fit|select|Zoom|Fit/i.test(k)), keys: keys.filter((k) => /zoom|fit|select/i.test(k)), allProto: proto.slice(0, 40) };
})()
