(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const TARGET = '54d2a25bce4b44c3af878e8b91af3554';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== TARGET) return { stop: true, reason: 'NOT_IMPORT', uuid: current && current.uuid };
  if ([LIVE, HUB].includes(current.uuid)) return { stop: true, reason: 'FORBIDDEN' };

  let pcbSrc = '';
  try {
    const file = await eda.sys_FileManager.getDocumentFile(PCB);
    pcbSrc = typeof file === 'string' ? file : String((file && (file.source || file.content)) || '');
  } catch (e) {
    pcbSrc = { err: String(e && e.message || e).slice(0, 160) };
  }
  const pcbText = typeof pcbSrc === 'string' ? pcbSrc : '';
  const pcbComponents = (pcbText.match(/"type":"COMPONENT"/g) || []).length
    + (pcbText.match(/\["COMPONENT"/g) || []).length;
  const pcbVias = (pcbText.match(/"type":"VIA"/g) || []).length
    + (pcbText.match(/\["VIA"/g) || []).length;

  let live = null;
  try {
    const info = await eda.dmt_Project.getProjectInfo(LIVE);
    live = { uuid: info && info.uuid, name: info && info.friendlyName };
  } catch (e) {
    live = { err: String(e && e.message || e).slice(0, 160) };
  }
  let liveFile = null;
  try {
    const file = await eda.sys_FileManager.getProjectFileByProjectUuid(LIVE);
    const blob = file && (file.size || file.byteLength || (typeof file === 'string' ? file.length : null));
    liveFile = {
      type: file == null ? 'null' : typeof file,
      keys: file && typeof file === 'object' ? Object.keys(file).slice(0, 16) : null,
      size: blob,
      name: file && file.name,
    };
  } catch (e) {
    liveFile = { err: String(e && e.message || e).slice(0, 160) };
  }

  let liveSch = null;
  try {
    const pages = ((((await eda.dmt_Project.getProjectInfo(LIVE)).data || [])[0] || {}).schematic || {}).page || [];
    liveSch = pages.map((p) => p.uuid);
  } catch (e) {
    liveSch = { err: String(e && e.message || e).slice(0, 120) };
  }

  return {
    currentUuid: current.uuid,
    currentName: current.friendlyName,
    didNotFocusLive: current.uuid !== LIVE,
    pcbType: typeof pcbSrc,
    pcbLen: pcbText.length,
    pcbHead: pcbText.slice(0, 80),
    pcbComponents,
    pcbVias,
    live,
    liveFile,
    liveSch,
  };
})()
