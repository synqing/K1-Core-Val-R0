(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  return {
    copyProject: String(eda.dmt_Project.copyProject),
    createProject: String(eda.dmt_Project.createProject),
    deleteProject: String(eda.dmt_Project.deleteProject),
    modifyName: String(eda.dmt_Project.modifyProjectFriendlyName),
    modifyDesc: String(eda.dmt_Project.modifyProjectDescription),
    getAll: String(eda.dmt_Project.getAllProjectsUuid).slice(0, 200),
  };
})()
