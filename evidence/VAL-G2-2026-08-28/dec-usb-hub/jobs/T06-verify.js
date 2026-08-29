(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const PCB = '59bef7e87cff4cd580561703b62d8c19';
  function sourceHash(source) {
    let hash = 2166136261;
    for (let i = 0; i < source.length; i += 1) {
      hash ^= source.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return source.length + ':' + (hash >>> 0).toString(16).padStart(8, '0');
  }
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (!info || info.uuid === LIVE || info.uuid !== HUB) {
    return { stop: true, reason: 'BAD_PROJ', uuid: info && info.uuid };
  }
  await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  const pins = await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId('92edd0bd8901c171');
  const pinXY = {};
  for (const pin of pins || []) {
    pinXY[pin.getState_PinNumber()] = {
      name: pin.getState_PinName && pin.getState_PinName(),
      x: pin.getState_X(),
      y: pin.getState_Y(),
    };
  }
  const wireIds = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  const hits = {};
  const usbPins = { '2': 1, '3': 1, '4': 1, '5': 1, '19': 1, '20': 1, '7': 1 };
  const interesting = {};
  function walkNums(line) {
    const nums = [];
    (function walk(v) {
      if (typeof v === 'number') nums.push(v);
      else if (Array.isArray(v)) v.forEach(walk);
    })(line);
    return nums;
  }
  for (const id of wireIds || []) {
    try {
      const w = await eda.sch_PrimitiveWire.get(id);
      if (!w) continue;
      const st = w.getState ? w.getState() : w;
      const net = (st && st.net) || (w.getState_Net && w.getState_Net()) || '';
      const line = (st && st.line) || (w.getState_Line && w.getState_Line());
      const nums = walkNums(line);
      for (const [n, meta] of Object.entries(pinXY)) {
        for (let i = 0; i + 1 < nums.length; i += 2) {
          if (Math.abs(nums[i] - meta.x) < 1 && Math.abs(nums[i + 1] - meta.y) < 1) {
            if (!hits[n]) hits[n] = [];
            hits[n].push({ id, net });
          }
        }
      }
      if (/USB_|RBIAS|CRFILT|PLL|XTAL|RESET|CFG|NON_REM|3V3|GND/.test(String(net))) {
        if (!interesting[net]) interesting[net] = 0;
        interesting[net] += 1;
      }
    } catch (e) { /* skip */ }
  }
  let pcbCount = null;
  try {
    await eda.dmt_EditorControl.activateDocument(PCB + '@' + HUB);
    const pcbIds = await eda.pcb_PrimitiveComponent.getAllPrimitiveId();
    pcbCount = (pcbIds || []).length;
    await eda.dmt_EditorControl.activateDocument(PAGE + '@' + HUB);
  } catch (e) {
    pcbCount = 'err ' + String(e && e.message || e).slice(0, 80);
  }
  const source = await eda.sys_FileManager.getDocumentSource();
  const comps = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const usbTouched = Object.keys(usbPins).filter((n) => (hits[n] || []).some((h) => h.net && h.net !== ''));
  return {
    proj: info.uuid,
    sourceHash: sourceHash(source),
    components: (comps || []).length,
    wires: (wireIds || []).length,
    pcbCount,
    pinHits: hits,
    usbTouched,
    interesting,
  };
})()
