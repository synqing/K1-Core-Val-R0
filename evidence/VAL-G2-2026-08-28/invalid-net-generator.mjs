import { readFileSync, writeFileSync } from 'node:fs';

const documentUuid = '9dcda892d43b45c695fdcd1efc347818';
const source = JSON.parse(readFileSync('/tmp/k1-val-g2-source-after-placement.json', 'utf8')).source;
const rows = source.split('\n').filter(Boolean).map(line => JSON.parse(line));
const components = new Map(rows.filter(row => row[0] === 'COMPONENT').map(row => [row[1], {
  primitiveId: row[1],
  part: row[2],
  x: row[3],
  y: row[4],
}]));

const pinRuns = [
  ...JSON.parse(readFileSync('/tmp/k1-val-g2-pin-inventory-results.json', 'utf8')),
  ...JSON.parse(readFileSync('/tmp/k1-val-g2-pin-inventory-retry-results.json', 'utf8')),
];
const pinsByComponent = new Map();
for (const record of pinRuns) {
  if (record.ok && record.result?.componentPrimitiveId && Array.isArray(record.result.pins)) {
    pinsByComponent.set(record.result.componentPrimitiveId, record.result.pins);
  }
}

const passivePart = /^(0402|CL05)/;
const passiveComponents = [...components.values()]
  .filter(component => component.primitiveId !== 'e1' && passivePart.test(component.part))
  .filter(component => {
    const numbers = new Set((pinsByComponent.get(component.primitiveId) ?? []).map(pin => pin.pinNumber));
    return numbers.has('1') && numbers.has('2');
  })
  .sort((a, b) => a.y - b.y || a.x - b.x)
  .slice(0, 120);

if (passiveComponents.length !== 120) {
  throw new Error(`expected 120 wireable passive components, got ${passiveComponents.length}`);
}

const fanoutNets = [
  '+5V_IN',
  '+5V_SYS',
  '+3V3',
  '+1V8',
  '+3V3_A',
  '+3V3_S3',
  '+3V3_NFC',
  '+5V_LED',
  'DGND',
  'AGND',
];

function domainCode(component) {
  if (component.y >= 1380) {
    if (component.x < 920) return 'RT';
    if (component.x < 1700) return 'ESP';
    if (component.x < 2470) return 'AUDIO';
    return 'PWR';
  }
  if (component.y >= 640) {
    if (component.x < 920) return 'USB';
    if (component.x < 1700) return 'NFC';
    return 'LED';
  }
  return 'K1BR';
}

const counters = new Map();
const jobs = passiveComponents.map((component, index) => {
  const code = domainCode(component);
  const serial = (counters.get(code) ?? 0) + 1;
  counters.set(code, serial);
  const uniqueNet = `${code}_QUAL_${String(serial).padStart(3, '0')}`;
  const fanoutNet = fanoutNets[index % fanoutNets.length];
  return {
    tag: `net-${String(index + 1).padStart(3, '0')}-${component.primitiveId}-${uniqueNet}`,
    tool: 'connect_schematic_pins_to_nets',
    args: {
      componentPrimitiveId: component.primitiveId,
      connections: [
        { pinNumber: '1', net: uniqueNet },
        { pinNumber: '2', net: fanoutNet },
      ],
      saveAfter: index === passiveComponents.length - 1,
      expectedDocumentUuid: documentUuid,
    },
  };
});

writeFileSync('/tmp/k1-val-g2-net-jobs.json', JSON.stringify(jobs, null, 2));
writeFileSync('/tmp/k1-val-g2-net-manifest.json', JSON.stringify({
  connectedComponents: jobs.length,
  uniqueNamedNets: jobs.length,
  fanoutNets,
  expectedNamedNetTotal: jobs.length + fanoutNets.length,
  domainUniqueNetCounts: Object.fromEntries(counters),
}, null, 2));
console.log(JSON.stringify(JSON.parse(readFileSync('/tmp/k1-val-g2-net-manifest.json', 'utf8')), null, 2));
