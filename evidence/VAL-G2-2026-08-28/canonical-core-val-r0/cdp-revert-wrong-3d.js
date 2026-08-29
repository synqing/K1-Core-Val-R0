(async () => {
  const R = window._EXTAPI_ROOT_;
  const tab = '59bef7e87cff4cd580561703b62d8c19@64325d0e55e0435abd018defb0089a9b';
  try { await R.dmt_EditorControl.activateDocument(tab); } catch (e) {}
  const comps = await R.pcb_PrimitiveComponent.getAll();
  const restore = {
    'C43-ESP': { model: 'b7d13df3e9464d7a99d0651d1a5b4d57', title: 'C0402_L1.0-W0.5-H0.5', transform: '39.37,19.685,0,0,0,0,0,0,0' },
    'C44-ESP': { model: 'b7d13df3e9464d7a99d0651d1a5b4d57', title: 'C0402_L1.0-W0.5-H0.5', transform: '39.37,19.685,0,0,0,0,0,0,0' },
    'D1-PWR1': { model: '1370be37a17e44418ae52e2b4cc1f5e5', title: 'SOT-23-6_L2.9-W1.6-H1.5-LS2.8-P0.95', transform: '110.236,113.364,0,90,0,0,0.0005,0.0005,0' },
    'U10-ESP': { model: '1370be37a17e44418ae52e2b4cc1f5e5', title: 'SOT-23-6_L2.9-W1.6-H1.5-LS2.8-P0.95', transform: '110.236,113.364,0,90,0,0,0.0005,0.0005,0' },
    'USB2': { model: '0513051d44a0486b835661f1b78cdeb9', title: 'USB-C-SMD_HYCW78-USBC24-140B', transform: '486.22,391.18524,0,0,0,0,-0.002,-66.733,-78.74' },
  };
  const out = { reverted: [], usb1: null };
  for (const c of comps) {
    const des = c.getState_Designator && c.getState_Designator();
    if (restore[des]) {
      const prev = (c.getState_OtherProperty && c.getState_OtherProperty()) || {};
      c.setState_OtherProperty({
        ...prev,
        '3D Model': restore[des].model,
        '3D Model Title': restore[des].title,
        '3D Model Transform': restore[des].transform,
      });
      out.reverted.push({
        des,
        other3d: (c.getState_OtherProperty() || {})['3D Model Title'],
        model3d: c.getState_Model3D && c.getState_Model3D(),
      });
    }
    if (des === 'USB1') {
      out.usb1 = {
        model3d: c.getState_Model3D && c.getState_Model3D(),
        other: {
          model: (c.getState_OtherProperty() || {})['3D Model'],
          title: (c.getState_OtherProperty() || {})['3D Model Title'],
          sid: c.getState_SupplierId && c.getState_SupplierId(),
          mid: c.getState_ManufacturerId && c.getState_ManufacturerId(),
        },
      };
    }
  }
  out.ok = out.reverted.length === 5 && out.usb1 && out.usb1.other.title === 'USB_C_Hirose_CX_4800304000_v3';
  return out;
})()
