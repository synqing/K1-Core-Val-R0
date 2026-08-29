(async () => {
  const R = window._EXTAPI_ROOT_;
  const system = '0819f05c4eef4c71ace90d822a990e87';
  const uuid = '1f60af53654b4c089403430f1a6f9058';
  const d = await R.lib_Device.get(uuid, system);
  return {
    name: d && d.name,
    subPartNames: d && d.subPartNames,
    symbolUuid: d && d.association && (d.association.symbolUuid || (d.association.symbol && d.association.symbol.uuid)),
    footprint: d && d.association && d.association.footprint,
    model3D: d && d.association && d.association.model3D,
    other3d: d && d.property && d.property.otherProperty && {
      model: d.property.otherProperty['3D Model'],
      title: d.property.otherProperty['3D Model Title'],
    },
    supplierId: d && d.property && d.property.supplierId,
    manufacturerId: d && d.property && d.property.manufacturerId,
  };
})()
