(async () => {
  const sandbox = Object.values(window._EXTAPI_SCRIPT_SPACES_ || {}).find((e) => e && e.eda);
  const eda = sandbox.eda;
  const names = [];
  let cur = eda.sys_FileManager;
  for (let d = 0; d < 4 && cur; d += 1) {
    names.push(...Object.getOwnPropertyNames(cur).filter((n) => typeof eda.sys_FileManager[n] === 'function'));
    cur = Object.getPrototypeOf(cur);
  }
  const uniq = [...new Set(names)].sort();
  const sigs = {};
  for (const n of uniq) sigs[n] = String(eda.sys_FileManager[n]).slice(0, 160);
  const editor = [];
  cur = eda.dmt_EditorControl;
  for (let d = 0; d < 4 && cur; d += 1) {
    editor.push(...Object.getOwnPropertyNames(cur).filter((n) => typeof eda.dmt_EditorControl[n] === 'function'));
    cur = Object.getPrototypeOf(cur);
  }
  const edUniq = [...new Set(editor)].filter((n) => /create|page|schematic|open|import|source/i.test(n)).sort();
  const edSigs = {};
  for (const n of edUniq) edSigs[n] = String(eda.dmt_EditorControl[n]).slice(0, 140);
  return { fm: sigs, editor: edSigs };
})()
