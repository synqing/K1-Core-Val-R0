(async () => {
  const eda = globalThis._EXTAPI_ROOT_;
  const HUB = '41c8e6523576456582ea35958b3684ed';
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== HUB) return { stop: true, uuid: info.uuid };
  const out = { proj: info.uuid, tries: [] };
  const attrApi = eda.sch_PrimitiveAttribute;
  out.attrKeys = attrApi ? Object.keys(attrApi) : [];
  try {
    if (attrApi && attrApi.delete) {
      await attrApi.delete('ebr000790');
      out.tries.push({ via: 'attr.delete', ok: true });
    }
  } catch (e) {
    out.tries.push({ via: 'attr.delete', ok: false, err: String(e && e.message || e).slice(0, 160) });
  }
  try {
    if (attrApi && attrApi.modify) {
      await attrApi.modify('ebr000790', { value: 'no' });
      out.tries.push({ via: 'attr.modify', ok: true });
    }
  } catch (e) {
    out.tries.push({ via: 'attr.modify', ok: false, err: String(e && e.message || e).slice(0, 160) });
  }
  await eda.sch_Document.save();
  const source = await eda.sys_FileManager.getDocumentSource();
  out.stillNc = source.includes('"id":"ebr000790"') && source.includes('NO_CONNECT');
  out.ncSnippet = (() => {
    const i = source.indexOf('ebr000790');
    return i < 0 ? null : source.slice(Math.max(0, i - 80), i + 180);
  })();
  return out;
})()
