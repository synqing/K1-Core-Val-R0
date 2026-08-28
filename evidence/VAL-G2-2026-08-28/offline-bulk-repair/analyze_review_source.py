#!/usr/bin/env python3
"""Census and postcondition checks for the imported review schematic source."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "harness"))
from easyeda_source_format import describe, parse_records_any_format, parse_v3_records

SRC_PATH = Path(sys.argv[1])
OUT_PATH = Path(sys.argv[2])

payload = json.loads(SRC_PATH.read_text())
source = payload["source"]
fmt = describe(source)
rows = parse_records_any_format(source, tool="analyze_review_source")

kind = Counter(row[0] for row in rows if row)
components = [row for row in rows if row and row[0] == "COMPONENT"]
wires = [row for row in rows if row and row[0] == "WIRE"]
texts = [row for row in rows if row and row[0] == "TEXT"]
rects = [row for row in rows if row and row[0] == "RECT"]
ncs = [row for row in rows if row and row[0] in {"NO_CONNECT", "NC", "FLAG"}]

# Designators live on ATTR parented to COMPONENT. V2-shaped ATTR is
# ["ATTR", id, parent, key, value, ...]
designators = []
attrs_by_owner = defaultdict(dict)
for row in rows:
    if not row:
        continue
    if row[0] == "ATTR" and len(row) >= 5:
        owner, key, val = row[2], str(row[3]), row[4] if len(row) > 4 else ""
        attrs_by_owner[owner][key] = val
        if key in {"Designator", "designator"}:
            designators.append(val)

v3_records = parse_v3_records(source)
v3_types = Counter(r.type for r in v3_records)
pin_nets = defaultdict(set)
for rec in v3_records:
    if rec.type not in {"PIN", "COMPONENT_PIN"}:
        continue
    parent = rec.get("parentId") or rec.get("ownerId")
    pin = rec.get("pinNumber") or rec.get("number")
    net = rec.get("net") or rec.get("NET")
    ref = attrs_by_owner.get(parent, {}).get("Designator")
    if ref and pin and net:
        pin_nets[str(net)].add(f"{ref}.{pin}")

unique = sorted(set(d for d in designators if d))
raw_designators = unique
wire_nets = sorted({
    str(attrs["NET"])
    for attrs in attrs_by_owner.values()
    if attrs.get("NET")
})
raw_nets = sorted(set(wire_nets) | set(pin_nets))
if not raw_designators:
    raw_designators = sorted(set(re.findall(r'"key":"Designator","value":"([^"]+)"', source)))
if not raw_nets:
    raw_nets = sorted(set(re.findall(r'"key":"NET","value":"([^"]+)"', source)))

box_titles = [
    "1. POWER ENTRY + CURRENT SENSE",
    "2. POWER CONVERSION + DISTRIBUTION",
    "3. RT1062 COMPUTE + CORE POWER",
    "4. RT1062 BOOT + CLOCK + DEBUG",
    "5. ESP32-S3 RADIO + SERVICE + K1BR",
    "6. AUDIO CAPTURE + CLOCK + MIC FLEX",
    "7. NFC FRONT END + ANTENNA",
    "8. MOTION / ACCELEROMETER",
    "9. LED DATA + TEMPERATURE",
    "10. DEBUG / RECOVERY + VALIDATION OPTIONS",
]
titles_found = {t: t in source for t in box_titles}

def present(ref: str) -> bool:
    return ref in raw_designators or f'"{ref}"' in source

def attr_for(ref: str) -> dict:
    for owner, attrs in attrs_by_owner.items():
        if attrs.get("Designator") == ref or attrs.get("designator") == ref:
            return attrs
    return {}

def bom_fields(ref: str) -> dict:
    attrs = attr_for(ref)
    keys = {k.lower(): (k, attrs[k]) for k in attrs}
    def grab(*names):
        for n in names:
            if n.lower() in keys:
                return keys[n.lower()][1]
        # scan source near designator for common ATTR names
        return None
    return {
        "Add into BOM": grab("Add into BOM", "Add Into BOM", "bom"),
        "Convert to PCB": grab("Convert to PCB", "Convert To PCB", "pcb"),
        "Manufacturer Part": grab("Manufacturer Part", "Manufacturer Part Number", "mpn"),
        "Supplier Part": grab("Supplier Part", "Supplier Part Number"),
        "supplierId": grab("Supplier ID", "supplierId", "Supplier Id"),
        "Value": grab("Value", "value"),
        "raw_keys": sorted(attrs.keys()),
    }

must_present = [
    "U1-PWR1", "R67-PWR1", "U17-PWR2", "C11-PWR2", "U16-VAL",
    "R31-AUD", "R32-AUD", "R33-AUD",
    "RCC1-PWR1", "RCC2-PWR1", "DVBUS-PWR1", "RILIM-LED",
]
# clock resistors may use different domain suffixes
clock_globs = [d for d in raw_designators if re.match(r"R3[123]-", d)]
must_absent = ["F1-PWR1", "L3-NFC", "R43-NFC", "R50-MOT", "U4-PWR2", "C68-PWR2", "R8-PWR2"]
rq048 = ["R40-AUD", "R41-AUD", "R45-MOT", "R47-MOT", "R49-MOT", "R56-VAL", "R57-VAL"]
dead_nets = ["5V_LED_COMMON", "LED_EFUSE_DVDT", "LED_EFUSE_ILIM", "USB_EFUSE_PG"]
must_nets = [
    "3V3_S3_FILTERED", "5V_LED_L_SW", "5V_LED_R_SW", "INA_KELVIN_N", "INA_KELVIN_P",
    "K1BR_CS_S3", "K1BR_IRQ_RT", "K1BR_MISO_RT", "K1BR_MOSI_S3", "K1BR_SCK_S3",
    "LED_FAULT_L_N", "LED_FAULT_R_N", "LED_PWR_L_EN", "LED_PWR_R_EN", "MIC_PWR_EN_N",
    "NFC_RFI1_DIV", "RT_I2C_SCL", "RT_I2C_SDA", "RT_USB_AUD_STRAP_IOMUX_TBD",
    "S3_I2C_SCL", "S3_I2C_SDA", "TPS2561_ILIM", "USB_CC1_ADC_TAP", "USB_CC2_ADC_TAP",
    "USB_DN_J1", "USB_DN_PROT", "USB_DN_RT", "USB_DP_J1", "USB_DP_PROT", "USB_DP_RT",
    "PWR_ENTRY_PG_RT_IOMUX_TBD",
]
must_not_nets = [
    "5V_USB_FILTERED", "K1BR_CS", "K1BR_IRQ", "K1BR_MISO", "K1BR_MOSI", "K1BR_SCK",
    "MIC_PWR_EN", "MOTION_SCL", "MOTION_SDA", "NFC_MATCH_L", "OPT_USB_AUD_RT",
] + dead_nets

# Pin-net from raw source patterns like "U1-PWR1","3" nearby NET
# EasyEDA source often has COMPONENT then ATTR Net on pins as:
# ["PIN", id, ..., "3"] and ATTR NET
pin_net_pairs = re.findall(
    r'\["ATTR","[^"]+","[^"]*","(?:Net|NET)","([^"]+)"',
    source,
)

report = {
    "format": fmt,
    "v3_types": dict(v3_types),
    "documentUuid": payload.get("documentUuid"),
    "documentType": payload.get("documentType"),
    "sourceHash": payload.get("sourceHash"),
    "characters": payload.get("characters"),
    "record_count": len(rows),
    "kinds": dict(kind),
    "component_rows": len(components),
    "wire_rows": len(wires),
    "text_rows": len(texts),
    "rect_rows": len(rects),
    "designator_attr_count": len(raw_designators),
    "unique_designators": raw_designators,
    "unique_designator_count": len(raw_designators),
    "box_titles": titles_found,
    "all_ten_titles": all(titles_found.values()),
    "presence": {ref: present(ref) for ref in must_present + must_absent},
    "clock_resistors": clock_globs,
    "r31_r32_r33": {
        "R31": [d for d in raw_designators if d.startswith("R31-")],
        "R32": [d for d in raw_designators if d.startswith("R32-")],
        "R33": [d for d in raw_designators if d.startswith("R33-")],
    },
    "u6_designators": [d for d in raw_designators if d.startswith("U6")],
    "rq048_bom": {ref: bom_fields(ref) for ref in rq048},
    "hold_bom": {ref: bom_fields(ref) for ref in ["DVBUS-PWR1", "U17-PWR2", "RILIM-LED", "R8-PWR2"]},
    "raw_net_count": len(raw_nets),
    "raw_nets_sample": raw_nets[:40],
    "must_nets_present": {n: n in source for n in must_nets},
    "must_not_nets_absent": {n: n not in source for n in must_not_nets},
    "u4_mentions": len(re.findall(r"U4-PWR2", source)),
    "u17_mentions": len(re.findall(r"U17-PWR2", source)),
    "u1_mentions": len(re.findall(r"U1-PWR1", source)),
    "domain_suffix_violations": [
        d for d in raw_designators if d and not re.search(r"-[A-Z0-9]+$", d) and not d.startswith("TP")
    ],
    "stale_primitives": {pid: pid in source for pid in ["e153914", "e146347"]},
    "pin_net_count": {k: len(v) for k, v in sorted(pin_nets.items())[:30]},
    "attr_key_histogram": dict(Counter(
        row[3] for row in rows if row and row[0] == "ATTR" and len(row) > 3
    )),
}

OUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({
    "wrote": str(OUT_PATH),
    "sourceHash": report["sourceHash"],
    "records": report["record_count"],
    "components": report["component_rows"],
    "wires": report["wire_rows"],
    "designators": report["unique_designator_count"],
    "all_ten_titles": report["all_ten_titles"],
    "U1": report["presence"].get("U1-PWR1"),
    "U4": report["presence"].get("U4-PWR2"),
    "U17": report["presence"].get("U17-PWR2"),
    "C68": report["presence"].get("C68-PWR2"),
    "R8": report["presence"].get("R8-PWR2"),
    "clock": report["r31_r32_r33"],
    "dead_nets_absent": report["must_not_nets_absent"],
}, indent=2))
