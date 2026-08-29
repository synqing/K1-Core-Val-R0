(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const LIVE = '64325d0e55e0435abd018defb0089a9b';
  const PAGE = '1435cb46f39e48c8a8aadbb84ca81603';
  const LIB = '0819f05c4eef4c71ace90d822a990e87';
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
  const parts = [
    { role: 'Y3', uuid: 'bc3f643e23b4440084f2b6200b1aa16d', x: 700, y: 800 },
    { role: 'C100', uuid: '89d19a0571134c658a142f8b107908ee', x: 820, y: 700 },
    { role: 'C101', uuid: 'a299e4f29fd2469688f76621c3d59c4d', x: 920, y: 700 },
    { role: 'C102', uuid: '049de29c27014f4897ce8e2ee2a26949', x: 820, y: 800 },
    { role: 'C103', uuid: '049de29c27014f4897ce8e2ee2a26949', x: 920, y: 800 },
    { role: 'C104', uuid: 'a299e4f29fd2469688f76621c3d59c4d', x: 820, y: 900 },
    { role: 'C105', uuid: '89d19a0571134c658a142f8b107908ee', x: 920, y: 900 },
    { role: 'C106', uuid: 'a299e4f29fd2469688f76621c3d59c4d', x: 1020, y: 700 },
    { role: 'C107', uuid: 'a299e4f29fd2469688f76621c3d59c4d', x: 1020, y: 800 },
    { role: 'R77', uuid: 'df256c00fbc140c389de5a49ad9e2ff3', x: 820, y: 1000 },
    { role: 'R78', uuid: 'a8fe6fdf29924f6c9dcbfa5a84a02fec', x: 920, y: 1000 },
    { role: 'R79', uuid: 'a8fe6fdf29924f6c9dcbfa5a84a02fec', x: 1020, y: 1000 },
    { role: 'R80', uuid: '542db4fb88de4c59bd539781e5a30727', x: 1120, y: 700 },
    { role: 'R87', uuid: 'ffb8c4ed7d7244bc918e37313d4ca373', x: 1120, y: 800 },
    { role: 'R88', uuid: 'a8fe6fdf29924f6c9dcbfa5a84a02fec', x: 1120, y: 900 },
    { role: 'R89', uuid: 'a8fe6fdf29924f6c9dcbfa5a84a02fec', x: 1120, y: 1000 },
    { role: 'R90', uuid: 'a8fe6fdf29924f6c9dcbfa5a84a02fec', x: 1220, y: 700 },
    { role: 'R91', uuid: 'ffb8c4ed7d7244bc918e37313d4ca373', x: 1220, y: 800 },
  ];
  const placed = [];
  for (const p of parts) {
    const prim = await eda.sch_PrimitiveComponent.create(
      { libraryUuid: LIB, uuid: p.uuid },
      p.x,
      p.y,
      undefined,
      0,
      false,
      true,
      false,
    );
    const st = prim && (prim.getState ? prim.getState() : prim);
    placed.push({
      role: p.role,
      id: st && (st.primitiveId || st.id || prim && prim.primitiveId),
      designator: st && st.designator,
      x: st && st.x,
      y: st && st.y,
      addIntoPcb: st && st.addIntoPcb,
    });
  }
  await eda.sch_Document.save();
  const source = await eda.sys_FileManager.getDocumentSource();
  const ids = await eda.sch_PrimitiveComponent.getAllPrimitiveId();
  const wires = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  return {
    proj: info.uuid,
    saved: true,
    sourceHash: sourceHash(source),
    components: (ids || []).length,
    wires: (wires || []).length,
    placed,
  };
})()
