(async () => {
  const R = window._EXTAPI_ROOT_;
  const LIB = '0819f05c4eef4c71ace90d822a990e87';
  const ids = [
    '7e3f17b4e5b64384aaa03075cd65e3e3',
    'e6946995a72f4deaa7b036359e4ff6e7',
    'ea8551bd5e9c4319bb8e029bbc32cda4',
  ];
  const out = { models: [] };
  for (const id of ids) {
    try {
      const m = await R.lib_3DModel.get(id, LIB);
      out.models.push({
        id,
        ok: true,
        name: m && (m.name || m.title),
        keys: m && Object.keys(m).slice(0, 20),
      });
    } catch (e) {
      out.models.push({ id, ok: false, err: String(e && e.message || e) });
    }
  }
  return out;
})()
