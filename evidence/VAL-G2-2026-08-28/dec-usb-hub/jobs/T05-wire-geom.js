(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  function summarize(id) {
    return (async () => {
      try {
        const w = await eda.sch_PrimitiveWire.get(id);
        const st = w && (w.getState ? w.getState() : w);
        const net = st && (st.net || (w.getState_Net && w.getState_Net()));
        const line = st && st.line;
        const nums = [];
        (function walk(v) {
          if (typeof v === 'number') nums.push(v);
          else if (Array.isArray(v)) v.forEach(walk);
        })(line);
        const xs = [], ys = [];
        for (let i = 0; i + 1 < nums.length; i += 2) {
          xs.push(nums[i]);
          ys.push(nums[i + 1]);
        }
        const pairs = [];
        for (let i = 0; i + 3 < nums.length; i += 2) {
          pairs.push([nums[i], nums[i + 1], nums[i + 2], nums[i + 3]]);
        }
        const leftCol = pairs.filter((p) => {
          const minX = Math.min(p[0], p[2]), maxX = Math.max(p[0], p[2]);
          const minY = Math.min(p[1], p[3]), maxY = Math.max(p[1], p[3]);
          return minX <= 230 && maxX >= 230 && minY < 860 && maxY > 730;
        });
        const rightUsb = pairs.filter((p) => {
          const minX = Math.min(p[0], p[2]), maxX = Math.max(p[0], p[2]);
          const minY = Math.min(p[1], p[3]), maxY = Math.max(p[1], p[3]);
          return minX <= 570 && maxX >= 570 && minY <= 815 && maxY >= 795;
        });
        return {
          id,
          exists: true,
          net,
          nNums: nums.length,
          nPairs: pairs.length,
          bbox: xs.length ? [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)] : null,
          leftCol: leftCol.length,
          rightUsb: rightUsb.length,
          leftColSample: leftCol.slice(0, 8),
          rightUsbSample: rightUsb.slice(0, 8),
        };
      } catch (e) {
        return { id, exists: false, err: String(e && e.message || e).slice(0, 160) };
      }
    })();
  }
  const ids = ['fd3dd96d58a6e4c4', 'f030c09f4f3caf10'];
  const out = [];
  for (const id of ids) out.push(await summarize(id));
  return { proj: info.uuid, wires: out };
})()
