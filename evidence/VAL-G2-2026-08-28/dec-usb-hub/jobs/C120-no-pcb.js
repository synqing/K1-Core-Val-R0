(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const ids = ['a689ce4197fefb88', '6fe37ae7451faa5d'];
  const before = [];
  const after = [];
  for (const id of ids) {
    const g = await eda.sch_PrimitiveComponent.get(id);
    before.push({ id, addIntoPcb: g && g.addIntoPcb, name: g && g.name, des: g && g.designator });
    await eda.sch_PrimitiveComponent.modify(id, { addIntoPcb: false });
    const g2 = await eda.sch_PrimitiveComponent.get(id);
    after.push({ id, addIntoPcb: g2 && g2.addIntoPcb, name: g2 && g2.name });
  }
  await eda.sch_Document.save();
  return { proj: info.uuid, before, after, saved: true };
})()
