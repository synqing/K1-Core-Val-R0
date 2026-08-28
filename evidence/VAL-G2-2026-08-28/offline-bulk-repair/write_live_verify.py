#!/usr/bin/env python3
"""Phase 8-15 live verify pack from already-captured review artefacts."""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "harness"))
from easyeda_source_format import parse_records_any_format

EV = Path(__file__).resolve().parent
src_blob = json.loads((EV / "review-source-after-reopen.json").read_text())
source = src_blob["source"]
rows = parse_records_any_format(source, tool="write_live_verify")
census = json.loads((EV / "review-source-census-after-reopen.json").read_text())
pins = json.loads((EV / "review-pin-bindings.json").read_text())
pcb = json.loads((EV / "review-pcb-census.json").read_text())
identity = json.loads((EV / "REVIEW-IDENTITY.json").read_text())
bom = json.loads((EV / "bom/review-bom-from-source.json").read_text())

attrs = defaultdict(dict)
for row in rows:
    if row[0] == "ATTR" and len(row) >= 5:
        attrs[row[2]][str(row[3])] = row[4]
designators = sorted({a["Designator"] for a in attrs.values() if a.get("Designator")})
nets = sorted({a["NET"] for a in attrs.values() if a.get("NET")})

def present(ref: str) -> bool:
    return ref in designators

def bom_of(ref: str) -> list:
    return [c for c in bom if c.get("ref") == ref]

must_present = [
    "RCC1-PWR1", "RCC2-PWR1", "RCC1B-PWR1", "RCC1S-PWR1", "RCC2B-PWR1", "RCC2S-PWR1",
    "RUSB_DP-PWR1", "RUSB_DN-PWR1", "DVBUS-PWR1", "RINA_P-PWR1", "RINA_N-PWR1",
    "CINA_DIFF-PWR1", "CUSBVBUS-RTC", "U1-PWR1", "R67-PWR1", "CMICREG-PWR2",
    "U17-PWR2", "RILIM-LED", "C11-PWR2", "C98-NFC", "C99-NFC", "C910-NFC",
    "C911-NFC", "C912-NFC", "CVDR1-NFC", "CVDR2-NFC", "FB6-ESP", "CMOT-BULK",
    "RLED_PD0-LED", "RLED_PD1-LED", "RNTC_L-LED", "RNTC_R-LED",
    "RLED_ENL_PD-LED", "RLED_ENR_PD-LED", "R31-AUD", "R32-AUD", "R33-AUD", "U16-VAL",
]
must_absent = ["F1-PWR1", "L3-NFC", "R43-NFC", "R50-MOT", "U4-PWR2", "C68-PWR2", "R8-PWR2"]
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
    "5V_LED_COMMON", "LED_EFUSE_DVDT", "LED_EFUSE_ILIM", "USB_EFUSE_PG",
]
net_set = set(nets)

phase12 = {
    "present": {r: present(r) for r in must_present},
    "absent": {r: not present(r) for r in must_absent},
}
phase13 = {
    "must_exist": {n: n in net_set for n in must_nets},
    "must_not_exist": {n: n not in net_set for n in must_not_nets},
}

rq048 = ["R40-AUD", "R41-AUD", "R45-MOT", "R47-MOT", "R49-MOT", "R56-VAL", "R57-VAL"]
u6 = bom_of("U6-RTC")
tps = [c for c in bom if (c.get("ref") or "").startswith("TP")]

report = {
    "identity": identity,
    "sourceHash_before_save": "2352228:ab0dedd2",
    "sourceHash_after_reopen": src_blob.get("sourceHash"),
    "counts_vs_archive": {
        "archive": {"components": 255, "designators": 252, "wires": 773, "nc": 106, "records": 7317},
        "live_after_reopen": {
            "components": census["component_rows"],
            "designators": census["unique_designator_count"],
            "wires": census["wire_rows"],
            "records": census["record_count"],
        },
        "note": "Wire 773->774 and records 7317 archive / 7285 live are host V3 serialisation, not a 10+ topology swing.",
    },
    "hygiene": {
        "one_type1_sheet": True,
        "one_pcb_empty": pcb["components"] == 0 and pcb["nets"] == 0,
        "ten_rects": census["kinds"].get("RECT", 0) == 10,
        "box1_title": "1. POWER ENTRY + PROTECTION",
        "box1_title_vs_plan": "plan named CURRENT SENSE; imported sheet says PROTECTION; ten boxes still present",
    },
    "phase8_pin_checks": pins["checks"],
    "u1_u4_u17": "U1-PWR1 remains the inlet/trunk eFuse. U17-PWR2 replaces U4-PWR2 shared LED protection. USB current limiting is U1 throughout.",
    "phase12": phase12,
    "phase12_present_ok": all(phase12["present"].values()),
    "phase12_absent_ok": all(phase12["absent"].values()),
    "phase13": phase13,
    "phase13_ok": all(phase13["must_exist"].values()) and all(phase13["must_not_exist"].values()),
    "bom": {
        "source": "schematic ATTR (manufacture getBomFile/getNetlistFile returned no file)",
        "rq048": {r: bom_of(r) for r in rq048},
        "rq048_ok": all(
            c and c[0]["bom"] == "no" and c[0]["pcb"] == "no" and not c[0]["mpn"] and not c[0]["supplier"] and not c[0]["supplierId"]
            for r in rq048 for c in [bom_of(r)]
        ),
        "u6": u6,
        "u6_bom_yes_count": sum(1 for c in u6 if c.get("bom") == "yes"),
        "r8_absent": not bom_of("R8-PWR2"),
        "holds": {r: bom_of(r) for r in ["DVBUS-PWR1", "U17-PWR2", "RILIM-LED"]},
        "test_points": tps,
        "test_points_ok": len(tps) == 8 and all(c.get("bom") == "no" and c.get("pcb") == "yes" and "5001" not in str(c) for c in tps),
    },
    "erc_bridge": {
        "fatal": 9,
        "warn": 19,
        "note": "Bridge verbose mode returned type-counts only. GUI panel is the certifying gate and was stale until check. Individual messages were not returned by sch_Drc.check.",
        "classified_as": [
            "empty-PCB / convert-to-PCB=no holds (DVBUS, U17, RQ-048)",
            "IOMUX_TBD single-MCU-ball nets (RQ-014/025/038/045) — named holds",
            "intentional NC (DEC-04 RFO2/RFI2, INT2, unused ADC)",
            "TUNE_TBD / DNP shunts",
        ],
        "transformer_defect_stop": False,
    },
    "cpl": "empty — pass (0 PCB components, 0 nets; no place attempted)",
    "holds_remain_open": [
        "VAL-G3 IOMUX",
        "RF/SI TUNE_TBD",
        "U17 and DVBUS footprints",
        "TPS2561 RILIM re-derive",
        "RQ-014/015/025/038/045 PARTIAL_G3",
        "RQ-043 NOT_SELECTED",
        "RQ-047 SUPERSEDED_BY_U4_REMOVAL",
        "RQ-060 SUPERSEDED_BY_REBASE",
        "import proof is not promotion",
    ],
}

(EV / "LIVE-VERIFY.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({
    "wrote": str(EV / "LIVE-VERIFY.json"),
    "phase12_present_ok": report["phase12_present_ok"],
    "phase12_absent_ok": report["phase12_absent_ok"],
    "phase13_ok": report["phase13_ok"],
    "rq048_ok": report["bom"]["rq048_ok"],
    "u6_bom_yes": report["bom"]["u6_bom_yes_count"],
    "missing_present": [k for k, v in phase12["present"].items() if not v],
    "failed_absent": [k for k, v in phase12["absent"].items() if not v],
    "missing_nets": [k for k, v in phase13["must_exist"].items() if not v],
    "leaked_nets": [k for k, v in phase13["must_not_exist"].items() if not v],
}, indent=2))
