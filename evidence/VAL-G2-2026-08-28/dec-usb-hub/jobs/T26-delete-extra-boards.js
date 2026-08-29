(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const G22 = 'f0f6cd233d69411ea478de1037da28fc';
  const KEEP_BOARD = '4a4562eab5ff7ae6';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const current = await eda.dmt_Project.getCurrentProjectInfo();
  if (!current || current.uuid !== G22) return { stop: true, uuid: current && current.uuid };
  if ([LIVE, HUB].includes(current.uuid)) return { stop: true, reason: 'FORBIDDEN' };
  const boards = await eda.dmt_Board.getAllBoardsInfo();
  const deleted = [];
  for (const b of boards || []) {
    if (b.uuid !== KEEP_BOARD && b.parentProjectUuid === G22) {
      try {
        deleted.push({ uuid: b.uuid, name: b.name, result: await eda.dmt_Board.deleteBoard(b.uuid) });
      } catch (e) {
        deleted.push({ uuid: b.uuid, err: String(e && e.message || e).slice(0, 140) });
      }
    }
  }
  const after = await eda.dmt_Board.getAllBoardsInfo();
  return {
    deleted,
    boards: (after || []).map((b) => ({ uuid: b.uuid, name: b.name, pcb: b.pcb && b.pcb.uuid })),
  };
})()
