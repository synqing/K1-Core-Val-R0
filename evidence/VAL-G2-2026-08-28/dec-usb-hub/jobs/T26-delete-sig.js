(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  if (!sandbox) return { error: 'no sandbox' };
  const eda = sandbox.eda;
  return {
    sig: String(eda.dmt_Project.deleteProject),
    length: eda.dmt_Project.deleteProject.length,
  };
})()
