(async () => {
  const PROJECT = "64325d0e55e0435abd018defb0089a9b";
  const PCB = "59bef7e87cff4cd580561703b62d8c19";
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const info = await eda.dmt_Project.getCurrentProjectInfo();
  if (info.uuid !== PROJECT) return { stop: true, project: info.uuid };
  await eda.dmt_EditorControl.openDocument(PCB);
  await new Promise((r) => setTimeout(r, 300));
  const doc = await eda.dmt_SelectControl.getCurrentDocumentInfo();
  return { restored: doc && doc.uuid, type: doc && doc.documentType };
})()
