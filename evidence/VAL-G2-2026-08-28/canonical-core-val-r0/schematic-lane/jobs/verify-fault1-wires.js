(async () => {
  const eda = globalThis._EXTAPI_ROOT_ || window._EXTAPI_ROOT_;
  const ghost = await eda.sch_PrimitiveWire.get("e82471");
  const fault = await eda.sch_PrimitiveWire.get("2639a4b072b190b5");
  const ids = await eda.sch_PrimitiveWire.getAllPrimitiveId();
  return {
    ghost: ghost && { id: ghost.primitiveId, net: ghost.net, lineLen: (ghost.line || []).length, line: ghost.line },
    fault: fault && { id: fault.primitiveId, net: fault.net, line: fault.line },
    hasGhost: ids.includes("e82471"),
    hasFault: ids.includes("2639a4b072b190b5"),
    nWires: ids.length,
  };
})()
