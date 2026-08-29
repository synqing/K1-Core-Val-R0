(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const drc = eda.sch_Drc;
  const names = [];
  let o = drc;
  for (let i = 0; i < 5 && o; i += 1) {
    names.push(...Object.getOwnPropertyNames(o));
    o = Object.getPrototypeOf(o);
  }
  const frames = [...document.querySelectorAll('iframe')].map((f) => ({
    id: f.id, name: f.name, src: (f.src || '').slice(0, 80),
  }));
  const bodySample = (document.body && document.body.innerText || '').slice(0, 500);
  return { proj: info.uuid, names: [...new Set(names)].slice(0, 80), frames, bodySample };
})()
