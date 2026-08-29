(async () => {
  const R = window._EXTAPI_ROOT_;
  const PROJECT = '64325d0e55e0435abd018defb0089a9b';
  const USB1_FP = '0c8e199e56e60728';
  const USB2_FP = '59bef7e87cff4cd580561703b62d8c19_001a257400b89df6';
  const toB64 = async (file) => {
    if (!file) return null;
    const buf = await file.arrayBuffer();
    const bytes = new Uint8Array(buf);
    let bin = '';
    const chunk = 0x8000;
    for (let i = 0; i < bytes.length; i += chunk) {
      bin += String.fromCharCode(...bytes.subarray(i, i + chunk));
    }
    return { name: file.name, size: file.size, type: file.type, b64: btoa(bin) };
  };
  const usb1 = await R.sys_FileManager.getFootprintFileByFootprintUuid(USB1_FP, PROJECT, 'elibz2');
  const usb2 = await R.sys_FileManager.getFootprintFileByFootprintUuid(USB2_FP, PROJECT, 'elibz2');
  return {
    usb1: await toB64(usb1),
    usb2: await toB64(usb2),
  };
})()
