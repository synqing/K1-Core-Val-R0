(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const HUSK = 'f0f6cd233d69411ea478de1037da28fc';
  const info = await eda.dmt_Project.getProjectInfo(HUSK);
  const keys = info ? Object.keys(info) : [];
  return {
    uuid: info && info.uuid,
    friendlyName: info && info.friendlyName,
    name: info && info.name,
    folderUuid: info && (info.folderUuid || info.ownerFolderUuid),
    teamUuid: info && info.teamUuid,
    keys,
    extra: {
      folder: info && info.folder,
      owner: info && info.owner,
      path: info && info.path,
    },
  };
})()
