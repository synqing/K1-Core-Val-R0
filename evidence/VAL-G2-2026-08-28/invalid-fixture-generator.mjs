import { writeFileSync } from 'node:fs';

const documentUuid = '9dcda892d43b45c695fdcd1efc347818';

const devices = {
  resistor: [
    'ffb8c4ed7d7244bc918e37313d4ca373',
    '3614094eae9e47dbbbde1f877b2c30ef',
    'b2476e89ebc2432a95ff8ef4515fb745',
    '2893e670fc1049cebce5fa9398c3bd58',
    '67bcedcf1a474734ac65b62dc52125d6',
    '72d71792aca642bfa6283f6c1d1961c3',
  ],
  capacitor: [
    '2eaf9ba597d94b93917d2b625402739a',
    '4724975b6c2a4e8dbf5d2a441323882f',
    '049de29c27014f4897ce8e2ee2a26949',
    'b5c168f4ad9244049bcea93dd255e434',
    '1ee9022f2d574b04b2e7e2b1718bdfd5',
    'e4d5fb354b0e426d82f53ec774ee0ef3',
    'e2ac8ecc52fd4bb69774e64e52b2b08f',
  ],
  rt1062: ['1f60af53654b4c089403430f1a6f9058'],
  esp32s3: ['6b4dea9080f640b8b046333779d77dec'],
  adc6120: ['a91c0d74a9404d5880ac6dceed53c450'],
  microphone: ['7233c3225899412bba6594a8c19da230'],
  nfc: ['d82681df05194db4a45dfdbd5c534ba7'],
  accelerometer: ['62a31043deae423f9f56d6db24e69df4'],
  usbC: ['ac85d077f9884c9887e81c00615e7c99'],
  header: ['f761cfb6af15492697fa5bc126df9a5d'],
  usbEsd: ['e931d537a1bc4fb7b633b601571c876a'],
  ldo: ['1d28b32a594d4e0bad61175e4a878bdc'],
  fuse: ['7703bf76fcaa4ad4ab53c0aed9d27373'],
  buck: ['5f0dc023e0cf4631bcb394455b8db171'],
  crystal: ['dba011b143a248829c6d7f11716dc192'],
  flash: ['186ba0074f284af0924bbcb475a8676a'],
  ledBuffer: ['0afb00d4f7314ae39823cec17728fd6a'],
};

const sections = {
  'RT1062 COMPUTE / BOOT': { x1: 100, y1: 1380, x2: 900, y2: 2260 },
  'ESP32-S3 / RADIO': { x1: 920, y1: 1380, x2: 1680, y2: 2260 },
  'AUDIO / TDM / PDM': { x1: 1700, y1: 1380, x2: 2450, y2: 2260 },
  'POWER ENTRY / RAILS': { x1: 2470, y1: 1380, x2: 3220, y2: 2260 },
  'USB / SERVICE': { x1: 100, y1: 640, x2: 900, y2: 1330 },
  'NFC / ACCELEROMETER': { x1: 920, y1: 640, x2: 1680, y2: 1330 },
  'LED POWER / DATA': { x1: 1700, y1: 640, x2: 2430, y2: 1330 },
  'K1BR / OPTIONS / VALIDATION': { x1: 100, y1: 400, x2: 3100, y2: 560 },
};

const zoneJobs = [{
  tag: 'sheet-title',
  tool: 'add_schematic_text',
  args: {
    x: 110,
    y: 2310,
    content: 'VAL-G2.0  K1-CORE-VAL  OPTION-C SINGLE-SHEET QUALIFICATION',
    fontName: 'Space Mono Bold',
    fontSize: 39.37007874015748,
    textColor: '#FF0000',
    bold: true,
    saveAfter: false,
    expectedDocumentUuid: documentUuid,
  },
}];

for (const [name, rect] of Object.entries(sections)) {
  zoneJobs.push({
    tag: `zone-${name}`,
    tool: 'add_schematic_rectangle',
    args: {
      topLeftX: rect.x1,
      topLeftY: rect.y1,
      width: rect.x2 - rect.x1,
      height: rect.y2 - rect.y1,
      lineWidth: 1,
      lineType: 0,
      fillStyle: 0,
      saveAfter: false,
      expectedDocumentUuid: documentUuid,
    },
  });
  zoneJobs.push({
    tag: `title-${name}`,
    tool: 'add_schematic_text',
    args: {
      x: rect.x1 + 12,
      y: rect.y2 - 25,
      content: name,
      fontName: 'Space Mono Bold',
      fontSize: 15.748031496062993,
      textColor: '#FF0000',
      bold: true,
      saveAfter: false,
      expectedDocumentUuid: documentUuid,
    },
  });
}
zoneJobs.at(-1).args.saveAfter = true;

function cycle(type, count) {
  return Array.from({ length: count }, (_, i) => ({ type, deviceUuid: devices[type][i % devices[type].length] }));
}

const domainItems = {
  'RT1062 COMPUTE / BOOT': [
    ...cycle('rt1062', 1), ...cycle('flash', 2), ...cycle('crystal', 2),
    ...cycle('resistor', 20), ...cycle('capacitor', 15),
  ],
  'ESP32-S3 / RADIO': [
    ...cycle('esp32s3', 1), ...cycle('flash', 2), ...cycle('crystal', 2),
    ...cycle('resistor', 12), ...cycle('capacitor', 13),
  ],
  'AUDIO / TDM / PDM': [
    ...cycle('adc6120', 4), ...cycle('microphone', 8),
    ...cycle('resistor', 6), ...cycle('capacitor', 7),
  ],
  'NFC / ACCELEROMETER': [
    ...cycle('nfc', 2), ...cycle('accelerometer', 4),
    ...cycle('resistor', 7), ...cycle('capacitor', 7),
  ],
  'POWER ENTRY / RAILS': [
    ...cycle('buck', 4), ...cycle('ldo', 4), ...cycle('fuse', 4),
    ...cycle('resistor', 5), ...cycle('capacitor', 8),
  ],
  'USB / SERVICE': [
    ...cycle('usbC', 4), ...cycle('usbEsd', 8), ...cycle('header', 4),
    ...cycle('resistor', 2), ...cycle('capacitor', 2),
  ],
  'LED POWER / DATA': [
    ...cycle('ledBuffer', 8), ...cycle('header', 2),
    ...cycle('resistor', 5), ...cycle('capacitor', 5),
  ],
  // One 10k resistor already exists at (240,480); place only the remaining 19.
  'K1BR / OPTIONS / VALIDATION': [
    ...cycle('header', 2), ...cycle('resistor', 10), ...cycle('capacitor', 7),
  ],
};

function rtPositions() {
  const points = [{ x: 500, y: 1820 }];
  for (let i = 0; i < 11; i++) points.push({ x: 150, y: 1480 + i * 70 });
  for (let i = 0; i < 11; i++) points.push({ x: 850, y: 1480 + i * 70 });
  for (let i = 0; i < 7; i++) points.push({ x: 230 + i * 90, y: 2220 });
  for (let i = 0; i < 7; i++) points.push({ x: 230 + i * 90, y: 1420 });
  points.push({ x: 260, y: 1600 }, { x: 740, y: 1600 }, { x: 260, y: 2050 });
  return points.slice(0, 40);
}

function espPositions() {
  const points = [{ x: 1300, y: 1820 }];
  for (let i = 0; i < 11; i++) points.push({ x: 960, y: 1480 + i * 70 });
  for (let i = 0; i < 11; i++) points.push({ x: 1640, y: 1480 + i * 70 });
  for (let i = 0; i < 6; i++) points.push({ x: 1050 + i * 90, y: 2200 });
  points.push({ x: 1250, y: 1430 });
  return points.slice(0, 30);
}

function gridPositions(x0, y0, cols, dx, dy, count) {
  return Array.from({ length: count }, (_, i) => ({
    x: x0 + (i % cols) * dx,
    y: y0 + Math.floor(i / cols) * dy,
  }));
}

const positions = {
  'RT1062 COMPUTE / BOOT': rtPositions(),
  'ESP32-S3 / RADIO': espPositions(),
  'AUDIO / TDM / PDM': gridPositions(1770, 1450, 5, 135, 170, 25),
  'NFC / ACCELEROMETER': gridPositions(970, 700, 5, 140, 180, 20),
  'POWER ENTRY / RAILS': gridPositions(2530, 1450, 5, 145, 170, 25),
  'USB / SERVICE': gridPositions(170, 700, 5, 145, 180, 20),
  'LED POWER / DATA': gridPositions(1760, 700, 5, 135, 180, 20),
  'K1BR / OPTIONS / VALIDATION': Array.from({ length: 19 }, (_, i) => ({ x: 390 + i * 140, y: 480 })),
};

const placementJobs = [];
const candidates = [{ des: 'PILOT_R', section: 'K1BR / OPTIONS / VALIDATION', x: 240, y: 480, type: 'resistor', existingPrimitiveId: 'e61' }];
let serial = 1;
for (const [domain, items] of Object.entries(domainItems)) {
  if (items.length !== positions[domain].length) throw new Error(`${domain}: items=${items.length} positions=${positions[domain].length}`);
  items.forEach((item, i) => {
    const p = positions[domain][i];
    const tag = `place-${String(serial).padStart(3, '0')}-${domain}-${item.type}`;
    placementJobs.push({
      tag,
      tool: 'add_schematic_component',
      args: {
        deviceUuid: item.deviceUuid,
        x: p.x,
        y: p.y,
        rotation: 0,
        addIntoBom: true,
        addIntoPcb: true,
        saveAfter: false,
        expectedDocumentUuid: documentUuid,
      },
    });
    candidates.push({ des: tag, section: domain, x: p.x, y: p.y, type: item.type });
    serial++;
  });
}
placementJobs.at(-1).args.saveAfter = true;

if (placementJobs.length !== 199) throw new Error(`expected 199 placement jobs, got ${placementJobs.length}`);
if (candidates.length !== 200) throw new Error(`expected 200 candidates including pilot, got ${candidates.length}`);

const shape = {
  boardName: 'K1-CORE-VAL-SINGLE-SHEET-QUAL',
  schematicPageUuid: documentUuid,
  description: 'Disposable VAL-G2.0 representative single-sheet placement zones.',
  sections,
  moduleEnvelopes: {},
  rules: {
    margin: 0,
    minPassivePitch: 70,
    requireInsideSection: true,
    forbidInsideModuleEnvelope: true,
  },
};

const manifest = {
  projectUuid: '09e9c541fd3d404082d4b92e55ae5336',
  abandonedProjectUuid: '64325d0e55e0435abd018defb0089a9b',
  schematicUuid: 'ad2bbec597804b06bebf5eaa5eb302cb',
  schematicPageUuid: documentUuid,
  existingElectricalComponents: 1,
  newPlacementJobs: placementJobs.length,
  plannedElectricalComponents: candidates.length,
  domains: Object.fromEntries(Object.entries(domainItems).map(([name, items]) => [name, items.length + (name === 'K1BR / OPTIONS / VALIDATION' ? 1 : 0)])),
};

writeFileSync('/tmp/k1-val-g2-zone-jobs.json', JSON.stringify(zoneJobs, null, 2));
writeFileSync('/tmp/k1-val-g2-placement-jobs.json', JSON.stringify(placementJobs, null, 2));
writeFileSync('/tmp/k1-val-g2-placement-candidates.json', JSON.stringify(candidates, null, 2));
writeFileSync('/tmp/k1-val-g2-placement-shape.json', JSON.stringify(shape, null, 2));
writeFileSync('/tmp/k1-val-g2-fixture-manifest.json', JSON.stringify(manifest, null, 2));
console.log(JSON.stringify({ zoneJobs: zoneJobs.length, placementJobs: placementJobs.length, candidates: candidates.length, domains: manifest.domains }, null, 2));
