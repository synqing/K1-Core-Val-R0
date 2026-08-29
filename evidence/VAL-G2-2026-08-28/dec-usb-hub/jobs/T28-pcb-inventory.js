(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const TARGET = '55ed9ee948734a0e903f37744b51f3b8';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== TARGET) return { stop: true, reason: 'NOT_HOLD', uuid: current && current.uuid };
  if ([LIVE, HUB].includes(current.uuid)) return { stop: true, reason: 'FORBIDDEN' };
  let pcbText = '';
  try {
    const file = await eda.sys_FileManager.getDocumentFile(PCB);
    pcbText = typeof file === 'string' ? file : String((file && (file.source || file.content)) || '');
  } catch (e) {
    return { uuid: current.uuid, pcbErr: String(e && e.message || e).slice(0, 160) };
  }
  const pcbComponents = (pcbText.match(/"type":"COMPONENT"/g) || []).length
    + (pcbText.match(/\["COMPONENT"/g) || []).length;
  const pcbVias = (pcbText.match(/"type":"VIA"/g) || []).length
    + (pcbText.match(/\["VIA"/g) || []).length;
  return {
    uuid: current.uuid,
    name: current.friendlyName,
    pcbLen: pcbText.length,
    pcbHead: pcbText.slice(0, 80),
    pcbComponents,
    pcbVias,
    didNotFocusLive: current.uuid !== LIVE,
  };
})()
