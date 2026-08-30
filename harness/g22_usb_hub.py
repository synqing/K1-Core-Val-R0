#!/usr/bin/env python3
"""G2.2 USB2422 + J1 semantic reconstruction (D-049 / D-050).

V3 sheets have no PIN records. J1 pin ends come from the live GT-USB-7005A
symbol offsets (MCP list, host Y negated). USB2422 pin ends come from
DS00001726B numbers plus the hub-lane symbol offsets applied to the HOLD
instance. A failed transform (too few proof pins) is UNRESOLVED, not PASS.

This check is fail-closed. Zero records, zero designators, zero named nets,
or an unproven USB2422 transform cannot print PASS.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from easyeda_source_format import parse_v3_records
from extract_electrical_graph import _load_source
from g22_pwr1_ilm import (
    PinHit,
    RESISTOR_0402_PINS,
    _attrs_by_owner,
    _components,
    _pin_hits,
    _vertex_nets,
    _wire_geometry,
    pin_xy,
)

J1_DESIGNATOR = "J1-PWR1"
RETIRED_J1 = "J1-USB4105-RETIRED"
FORBIDDEN_TYPE_C = ("J7-ESP",)
U20_DESIGNATOR = "U20-USB"
U21_DESIGNATOR = "U21-USB"
U22_DESIGNATOR = "U22-USB"
U6_DESIGNATOR = "U6-RTC"
U9_DESIGNATOR = "U9-ESP"
RUSB_DP = "RUSB_DP-PWR1"
RUSB_DN = "RUSB_DN-PWR1"
R94 = "R94-USB"
R95 = "R95-USB"
R85 = "R85-USB"
R90 = "R90-USB"
C123 = "C123-USB"
R77 = "R77-USB"
C100 = "C100-USB"
C101 = "C101-USB"
Y3 = "Y3-USB"
TUNE_DP = "RUSB_S3_DP_TUNE"
TUNE_DM = "RUSB_S3_DM_TUNE"
J6 = "J6-ESP"
J12 = "J12-USB"

# Symbol-frame offsets for GT-USB-7005A at HOLD origin (150, -4120) rot 0.
# Live MCP list_schematic_component_pins 2026-08-30, host (x,+y) → source (x,-y).
# A-column pin ends at x=110 (sx=-40), A1 at origin Y (sy=0), pitch -32.
# Prior table used sx=-35 / A1 sy=+100 and missed every live pin end.
J1_PINS: dict[str, dict[str, Any]] = {
    "A1": {"name": "GND", "sx": -40, "sy": 0, "expect": "GND", "group": "GND", "nc": False},
    "A2": {"name": "TX1+", "sx": -40, "sy": -32, "expect": None, "group": "NC", "nc": True},
    "A3": {"name": "TX1-", "sx": -40, "sy": -64, "expect": None, "group": "NC", "nc": True},
    "A4": {"name": "VBUS", "sx": -40, "sy": -96, "expect": "5V_USB", "group": "VBUS", "nc": False},
    "A5": {"name": "CC1", "sx": -40, "sy": -128, "expect": "USB_CC1", "group": "CC1", "nc": False},
    "A6": {"name": "D+", "sx": -40, "sy": -160, "expect": "USB_DP_J1", "group": "DP", "nc": False},
    "A7": {"name": "D-", "sx": -40, "sy": -192, "expect": "USB_DN_J1", "group": "DM", "nc": False},
    "A8": {"name": "SBU1", "sx": -40, "sy": -224, "expect": None, "group": "NC", "nc": True},
    "A9": {"name": "VBUS", "sx": -40, "sy": -256, "expect": "5V_USB", "group": "VBUS", "nc": False},
    "A10": {"name": "RX2-", "sx": -40, "sy": -288, "expect": None, "group": "NC", "nc": True},
    "A11": {"name": "RX2+", "sx": -40, "sy": -320, "expect": None, "group": "NC", "nc": True},
    "A12": {"name": "GND", "sx": -40, "sy": -352, "expect": "GND", "group": "GND", "nc": False},
    "B1": {"name": "GND", "sx": 240, "sy": 0, "expect": "GND", "group": "GND", "nc": False},
    "B2": {"name": "TX2+", "sx": 240, "sy": -32, "expect": None, "group": "NC", "nc": True},
    "B3": {"name": "TX2-", "sx": 240, "sy": -64, "expect": None, "group": "NC", "nc": True},
    "B4": {"name": "VBUS", "sx": 240, "sy": -96, "expect": "5V_USB", "group": "VBUS", "nc": False},
    "B5": {"name": "CC2", "sx": 240, "sy": -128, "expect": "USB_CC2", "group": "CC2", "nc": False},
    "B6": {"name": "D+", "sx": 240, "sy": -160, "expect": "USB_DP_J1", "group": "DP", "nc": False},
    "B7": {"name": "D-", "sx": 240, "sy": -192, "expect": "USB_DN_J1", "group": "DM", "nc": False},
    "B8": {"name": "SBU2", "sx": 240, "sy": -224, "expect": None, "group": "NC", "nc": True},
    "B9": {"name": "VBUS", "sx": 240, "sy": -256, "expect": "5V_USB", "group": "VBUS", "nc": False},
    "B10": {"name": "RX1-", "sx": 240, "sy": -288, "expect": None, "group": "NC", "nc": True},
    "B11": {"name": "RX1+", "sx": 240, "sy": -320, "expect": None, "group": "NC", "nc": True},
    "B12": {"name": "GND", "sx": 240, "sy": -352, "expect": "GND", "group": "GND", "nc": False},
    "S1": {"name": "SHELL.TAB1", "sx": 20, "sy": -420, "expect": "GND", "group": "SHIELD", "nc": False},
    "S2": {"name": "SHELL.TAB2", "sx": 70, "sy": -420, "expect": "GND", "group": "SHIELD", "nc": False},
    "S3": {"name": "SHELL.TAB3", "sx": 120, "sy": -420, "expect": "GND", "group": "SHIELD", "nc": False},
    "S4": {"name": "SHELL.TAB4", "sx": 170, "sy": -420, "expect": "GND", "group": "SHIELD", "nc": False},
}

# USB2422 QFN-24 + EP. Offsets in source frame for origin (400, -800) rot 0.
# Pin numbers: DS00001726B. DN1 = 4/3, DN2 = 5/2.
USB2422_PINS: dict[str, dict[str, Any]] = {
    "1": {"name": "VDD33", "sx": -170, "sy": -50, "expect": "3V3"},
    "2": {"name": "USBDM_DN2", "sx": -170, "sy": -40, "expect": "USB_DM_DN2"},
    "3": {"name": "USBDM_DN1", "sx": -170, "sy": -30, "expect": "USB_DM_DN1"},
    "4": {"name": "USBDP_DN1", "sx": -170, "sy": -20, "expect": "USB_DP_DN1"},
    "5": {"name": "USBDP_DN2", "sx": -170, "sy": -10, "expect": "USB_DP_DN2"},
    "6": {"name": "NC", "sx": -170, "sy": 0, "expect": None},
    "7": {"name": "PRTPWR1", "sx": -170, "sy": 10, "expect": "USB_PRTPWR1"},
    "8": {"name": "OCS1_N", "sx": -170, "sy": 20, "expect": "USB_OCS1_N"},
    "9": {"name": "VDD33", "sx": -170, "sy": 30, "expect": "3V3"},
    "10": {"name": "CRFILT", "sx": -170, "sy": 40, "expect": None},
    "11": {"name": "PRTPWR2", "sx": -170, "sy": 50, "expect": "USB_PRTPWR2"},
    "12": {"name": "OCS2_N", "sx": -170, "sy": 60, "expect": "USB_OCS2_N"},
    "13": {"name": "NON_REM1", "sx": 170, "sy": 60, "expect": "3V3"},
    "14": {"name": "CFG_SEL", "sx": 170, "sy": 50, "expect": "GND"},
    "15": {"name": "RESET_N", "sx": 170, "sy": 40, "expect": "USB_RESET_N"},
    "16": {"name": "VBUS_DET", "sx": 170, "sy": 30, "expect": "USB_VBUS_DET"},
    "17": {"name": "NON_REM0", "sx": 170, "sy": 20, "expect": "GND"},
    "18": {"name": "VDD33", "sx": 170, "sy": 10, "expect": "3V3"},
    "19": {"name": "USBDM_UP", "sx": 170, "sy": 0, "expect": "USB_DM_UP"},
    "20": {"name": "USBDP_UP", "sx": 170, "sy": -10, "expect": "USB_DP_UP"},
    "21": {"name": "XTALOUT", "sx": 170, "sy": -20, "expect": "USB_XTALOUT"},
    "22": {"name": "XTALIN", "sx": 170, "sy": -30, "expect": "USB_XTALIN"},
    "23": {"name": "PLLFILT", "sx": 170, "sy": -40, "expect": None},
    "24": {"name": "RBIAS", "sx": 170, "sy": -50, "expect": None},
    "25": {"name": "EP", "sx": 170, "sy": -60, "expect": "GND"},
}

U20_PROOF_PINS = ("2", "3", "4", "5", "7", "9", "14", "16", "17", "18", "19", "20", "25")
U20_PROOF_MIN = 8

U21_PINS: dict[str, dict[str, Any]] = {
    "1": {"name": "GND", "sx": -60, "sy": -10},
    "2": {"name": "IN", "sx": -60, "sy": 0},
    "3": {"name": "EN1", "sx": -60, "sy": 10},
    "4": {"name": "EN2", "sx": -60, "sy": 20},
    "5": {"name": "OC2", "sx": 60, "sy": 20},
    "6": {"name": "OUT2", "sx": 60, "sy": 10},
    "7": {"name": "OUT1", "sx": 60, "sy": 0},
    "8": {"name": "OC1", "sx": 60, "sy": -10},
}

U22_PINS: dict[str, dict[str, Any]] = {
    "1": {"name": "OUT", "sx": -35, "sy": -10},
    "2": {"name": "NC", "sx": -35, "sy": 0},
    "3": {"name": "PG", "sx": -35, "sy": 10},
    "4": {"name": "EN", "sx": 35, "sy": 10},
    "5": {"name": "GND", "sx": 35, "sy": 0},
    "6": {"name": "IN", "sx": 35, "sy": -10},
    "7": {"name": "EP", "sx": 0, "sy": -30},
}

DP_CHAIN = {"USB_DP_J1", "USB_DP_PROT", "USB_DP_UP"}
DM_CHAIN = {"USB_DN_J1", "USB_DN_PROT", "USB_DM_UP"}
SERIES_AUDIT = (R85, R90, R94, C123)

# Documented exceptions: none on the live HOLD. DNP-open (both sides empty) is not same-net.
SAME_NET_EXCEPTIONS: dict[str, str] = {}


@dataclass
class UsbHubReport:
    ok: bool
    unresolved: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    j1_pins: dict[str, PinHit] = field(default_factory=dict)
    u20_pins: dict[str, PinHit] = field(default_factory=dict)
    u21_pins: dict[str, PinHit] = field(default_factory=dict)
    series: dict[str, dict[str, Any]] = field(default_factory=dict)
    paths: dict[str, Any] = field(default_factory=dict)
    straps: dict[str, Any] = field(default_factory=dict)
    transform: dict[str, Any] = field(default_factory=dict)
    reconstruction: str = (
        "GT-USB-7005A MCP offsets + USB2422 DS00001726B offsets; "
        "vertex coincidence tolerance 0"
    )

    def as_dict(self) -> dict[str, Any]:
        def pins(table: dict[str, PinHit]) -> dict:
            return {
                pin: {"name": h.name, "xy": list(h.xy), "nets": h.nets, "open": h.open}
                for pin, h in table.items()
            }

        return {
            "ok": self.ok,
            "unresolved": self.unresolved,
            "errors": self.errors,
            "warnings": self.warnings,
            "counts": self.counts,
            "reconstruction": self.reconstruction,
            "transform": self.transform,
            "j1_pins": pins(self.j1_pins),
            "u20_pins": pins(self.u20_pins),
            "u21_pins": pins(self.u21_pins),
            "series": self.series,
            "paths": self.paths,
            "straps": self.straps,
        }


def _one_net(hit: PinHit) -> str | None:
    if len(hit.nets) == 1:
        return hit.nets[0]
    return None


def _two_pin_nets(comp: dict, verts) -> tuple[list[str], list[str]]:
    hits = _pin_hits(comp, RESISTOR_0402_PINS, verts)
    return hits["1"].nets, hits["2"].nets


def _near(comp: dict | None, verts, net: str, radius: int = 400) -> bool:
    if comp is None:
        return False
    ux, uy = int(round(comp["x"])), int(round(comp["y"]))
    for (x, y), nets in verts.items():
        if net in nets and abs(x - ux) <= radius and abs(y - uy) <= radius:
            return True
    return False


def analyse(source: str, *, source_path: str | None = None) -> UsbHubReport:
    errors: list[str] = []
    warnings: list[str] = []
    report = UsbHubReport(ok=False, unresolved=False, errors=errors, warnings=warnings)

    records = parse_v3_records(source)
    files = 1 if source_path else 0
    empty_counts = {
        "files_inspected": files,
        "easyeda_records_parsed": 0,
        "components_inspected": 0,
        "connector_pins_resolved": 0,
        "usb2422_pins_resolved": 0,
        "nets_inspected": 0,
        "assertions_executed": 0,
    }
    if not records:
        report.unresolved = True
        report.counts = empty_counts
        errors.append("parsed 0 EasyEDA records; failing closed")
        return report

    attrs = _attrs_by_owner(records)
    components = _components(records, attrs)
    net_of_wire, segs = _wire_geometry(records, attrs)
    verts = _vertex_nets(net_of_wire, segs)
    named_nets = sorted({n for n in net_of_wire.values() if n})
    assertions = 0

    report.counts = {
        "files_inspected": max(files, 1),
        "easyeda_records_parsed": len(records),
        "components_inspected": len(components),
        "connector_pins_resolved": 0,
        "usb2422_pins_resolved": 0,
        "nets_inspected": len(named_nets),
        "assertions_executed": 0,
    }
    if not components:
        report.unresolved = True
        errors.append("parsed 0 designated components; failing closed")
        return report
    if not named_nets:
        report.unresolved = True
        errors.append("parsed 0 named nets; failing closed")
        return report

    # --- receptacle census ---
    assertions += 1
    for name in FORBIDDEN_TYPE_C:
        if name in components:
            errors.append(f"forbidden second Type-C present: {name}")
    j1 = components.get(J1_DESIGNATOR)
    assertions += 1
    if j1 is None:
        errors.append(f"{J1_DESIGNATOR} missing")
        report.unresolved = True
        report.counts["assertions_executed"] = assertions
        return report
    part = str(j1.get("partId") or "") + " " + str((j1.get("attrs") or {}).get("Manufacturer Part") or "")
    assertions += 1
    if "GT-USB-7005A" not in part and "7005A" not in part:
        errors.append(f"{J1_DESIGNATOR} is not GT-USB-7005A (part={part!r})")

    j1_hits = _pin_hits(j1, J1_PINS, verts)
    report.j1_pins = j1_hits
    report.counts["connector_pins_resolved"] = len(j1_hits)
    assertions += 1
    if len(j1_hits) != 28:
        report.unresolved = True
        errors.append(f"J1 pin-role reconstruction produced {len(j1_hits)} pins, not 28")
        report.counts["assertions_executed"] = assertions
        return report

    wired_functional = 0
    for number, spec in J1_PINS.items():
        hit = j1_hits[number]
        got = _one_net(hit)
        if spec["group"] == "NC":
            assertions += 1
            if got and got not in {"GND"} and not str(got).upper().startswith("NC"):
                errors.append(f"J1.{number} {spec['name']} is NC but landed on {got}")
            continue
        expect = spec["expect"]
        assertions += 1
        if spec["group"] == "DP":
            if got in DP_CHAIN:
                wired_functional += 1
            else:
                errors.append(f"J1.{number} D+ present={got or 'OPEN'} expected one of {sorted(DP_CHAIN)}")
        elif spec["group"] == "DM":
            if got in DM_CHAIN:
                wired_functional += 1
            else:
                errors.append(f"J1.{number} D− present={got or 'OPEN'} expected one of {sorted(DM_CHAIN)}")
        elif expect and got == expect:
            wired_functional += 1
        else:
            errors.append(f"J1.{number} {spec['name']} present={got or 'OPEN'} expected={expect}")

    report.paths["j1_functional_wired"] = wired_functional
    assertions += 1
    if wired_functional < 16:
        errors.append(f"GT-USB-7005A lacks meaningful connectivity ({wired_functional} functional pins)")

    # --- USB2422 ---
    u20 = components.get(U20_DESIGNATOR)
    assertions += 1
    if u20 is None:
        errors.append(f"{U20_DESIGNATOR} missing")
        report.unresolved = True
        report.counts["assertions_executed"] = assertions
        return report

    u20_hits = _pin_hits(u20, USB2422_PINS, verts)
    report.u20_pins = u20_hits
    report.counts["usb2422_pins_resolved"] = len(u20_hits)
    proof_ok = 0
    for pin in U20_PROOF_PINS:
        expect = USB2422_PINS[pin]["expect"]
        got = _one_net(u20_hits[pin])
        if expect and got == expect:
            proof_ok += 1
    report.transform = {
        "u20_proof_pins_matched": proof_ok,
        "u20_proof_min": U20_PROOF_MIN,
        "u20_xy": [u20["x"], u20["y"]],
        "u20_rotation": u20.get("rotation"),
    }
    assertions += 1
    if proof_ok < U20_PROOF_MIN:
        report.unresolved = True
        errors.append(
            f"USB2422 transform unproven ({proof_ok}/{len(U20_PROOF_PINS)} "
            f"proof pins; need {U20_PROOF_MIN})"
        )
        report.counts["assertions_executed"] = assertions
        return report

    def u20_net(pin: str) -> str | None:
        return _one_net(u20_hits[pin])

    for pin in ("1", "9", "18"):
        assertions += 1
        if u20_net(pin) != "3V3":
            errors.append(f"U20.{pin} VDD33 present={u20_net(pin) or 'OPEN'} expected=3V3")
    assertions += 1
    if u20_net("25") != "GND":
        errors.append(f"U20.25 EP present={u20_net('25') or 'OPEN'} expected=GND")
    assertions += 1
    if u20_hits["10"].open:
        errors.append("U20.10 CRFILT open — C100-USB 1 µF missing")
    assertions += 1
    if u20_hits["23"].open:
        errors.append("U20.23 PLLFILT open — C101-USB 100 nF missing")
    assertions += 1
    if u20_hits["24"].open:
        errors.append("U20.24 RBIAS open — R77-USB 12 kΩ missing")
    assertions += 1
    if u20_hits["22"].open:
        errors.append("U20.22 XTALIN open — Y3-USB / USB_XTALIN missing")
    assertions += 1
    xtalout = u20_net("21")
    if xtalout == "GND":
        errors.append("U20.21 XTALOUT on GND — crystal pin-row merge (S-USB-08)")
    elif xtalout != "USB_XTALOUT":
        errors.append(f"U20.21 XTALOUT present={xtalout or 'OPEN'} expected=USB_XTALOUT")
    assertions += 1
    rbias = u20_net("24")
    xtalin = u20_net("22")
    if rbias and xtalin and rbias == xtalin:
        errors.append(
            f"U20.24 RBIAS shares net {rbias} with XTALIN — corridor merge (S-USB-07)"
        )
    assertions += 1
    if Y3 not in components:
        errors.append("Y3-USB 24 MHz crystal missing")
    elif all(not nets for nets in _two_pin_nets(components[Y3], verts)):
        errors.append("Y3-USB placed but both pins open")

    cfg = u20_net("14")
    n1 = u20_net("13")
    n0 = u20_net("17")
    report.straps = {
        "CFG_SEL": cfg,
        "NON_REM1": n1,
        "NON_REM0": n0,
        "strap_mode": cfg == "GND",
        "non_rem_10": n1 == "3V3" and n0 == "GND",
    }
    assertions += 1
    if cfg != "GND":
        errors.append(f"CFG_SEL present={cfg or 'OPEN'} expected=GND (strap mode)")
    assertions += 1
    if n1 != "3V3" or n0 != "GND":
        errors.append(f"NON_REM[1:0] present={n1 or 'OPEN'}/{n0 or 'OPEN'} expected=3V3/GND (10)")
    assertions += 1
    if n0 == "3V3":
        errors.append("NON_REM0 tied to VDD33 — forbidden")
    assertions += 1
    if u20_net("11") == "GND":
        errors.append("U20.11 PRTPWR2 is on GND — KILL-B AND path missing USB_PRTPWR2")
    elif u20_net("11") != "USB_PRTPWR2":
        errors.append(f"U20.11 PRTPWR2 present={u20_net('11') or 'OPEN'} expected=USB_PRTPWR2")

    # --- upstream / DN1 / DN2 ---
    assertions += 1
    if u20_net("20") != "USB_DP_UP":
        errors.append(f"hub US D+ present={u20_net('20') or 'OPEN'} expected=USB_DP_UP")
    assertions += 1
    if u20_net("19") != "USB_DM_UP":
        errors.append(f"hub US D− present={u20_net('19') or 'OPEN'} expected=USB_DM_UP")
    assertions += 1
    if u20_net("4") != "USB_DP_DN1" or u20_net("3") != "USB_DM_DN1":
        errors.append(
            f"hub DN1 present={u20_net('4') or 'OPEN'}/{u20_net('3') or 'OPEN'} "
            "expected=USB_DP_DN1/USB_DM_DN1"
        )
    assertions += 1
    if u20_net("5") != "USB_DP_DN2" or u20_net("2") != "USB_DM_DN2":
        errors.append(
            f"hub DN2 present={u20_net('5') or 'OPEN'}/{u20_net('2') or 'OPEN'} "
            "expected=USB_DP_DN2/USB_DM_DN2"
        )

    # T2 pin-column keepout: west signals must never land on the 3V3 rail.
    west_not_3v3 = ("2", "3", "4", "5", "6", "7", "8", "10", "11", "12")
    for pin in west_not_3v3:
        assertions += 1
        got = u20_net(pin)
        if got == "3V3":
            name = USB2422_PINS[pin]["name"]
            errors.append(
                f"U20.{pin} {name} shorted onto 3V3 — west pin-column keepout (S-USB-06)"
            )

    u6 = components.get(U6_DESIGNATOR)
    u9 = components.get(U9_DESIGNATOR)
    assertions += 1
    if u6 is None:
        errors.append("U6-RTC missing — DN1 RT endpoint cannot be proven")
    elif not _near(u6, verts, "USB_DP_DN1") or not _near(u6, verts, "USB_DM_DN1"):
        errors.append("USB_DP_DN1/USB_DM_DN1 have no vertex near U6-RTC")
    assertions += 1
    s3_ok = False
    if TUNE_DP in components:
        t1, t2 = _two_pin_nets(components[TUNE_DP], verts)
        if "USB_DP_S3" in t1 + t2 and ("USB_DP_DN2" in t1 + t2 or "USB_DP_DN2_SEL" in t1 + t2):
            s3_ok = True
    if u9 is not None and _near(u9, verts, "USB_DP_S3"):
        s3_ok = True
    if not s3_ok:
        errors.append("DN2 does not reach ESP32-S3 native USB (tune / USB_DP_S3)")

    rusb_ok = False
    if RUSB_DP in components:
        a, b = _two_pin_nets(components[RUSB_DP], verts)
        if "USB_DP_UP" in a + b and ("USB_DP_PROT" in a + b or "USB_DP_J1" in a + b):
            rusb_ok = True
    report.paths["upstream"] = {
        "hub_dp": u20_net("20"),
        "hub_dm": u20_net("19"),
        "rusb_series": rusb_ok,
        "j1_dp": _one_net(j1_hits["A6"]),
        "j1_dm": _one_net(j1_hits["A7"]),
    }
    assertions += 1
    if not rusb_ok:
        errors.append("upstream series RUSB_DP-PWR1 does not bridge connector-side net to USB_DP_UP")

    report.paths["dn1"] = {"dp": u20_net("4"), "dm": u20_net("3")}
    report.paths["dn2"] = {"dp": u20_net("5"), "dm": u20_net("2"), "s3_reached": s3_ok}

    # --- XOR ---
    xor = {"r94": None, "r95": None, "both_active": False, "r94_same_net": False}
    r94_nets: tuple[list[str], list[str]] | None = None
    r95_nets: tuple[list[str], list[str]] | None = None
    if R94 in components:
        r94_nets = _two_pin_nets(components[R94], verts)
        xor["r94"] = r94_nets
        xor["r94_same_net"] = bool(r94_nets[0]) and r94_nets[0] == r94_nets[1] and len(r94_nets[0]) == 1
    if R95 in components:
        r95_nets = _two_pin_nets(components[R95], verts)
        xor["r95"] = r95_nets
    r95_live = bool(r95_nets and r95_nets[0] and r95_nets[1])
    r94_live = bool(r94_nets and r94_nets[0] and r94_nets[1])
    xor["both_active"] = r94_live and r95_live
    report.paths["xor"] = xor
    assertions += 1
    if xor["r94_same_net"]:
        errors.append("R94-USB is same-net — XOR/series 0 Ω can be routed around")
    assertions += 1
    if xor["both_active"]:
        errors.append("R94-USB and R95-USB are both electrically connected — XOR violated")
    assertions += 1
    if J6 not in components:
        errors.append("J6-ESP recovery UART missing")

    # --- F6 / validity ---
    u21 = components.get(U21_DESIGNATOR)
    u22 = components.get(U22_DESIGNATOR)
    assertions += 1
    if u21 is None or u22 is None:
        errors.append("U21-USB / U22-USB missing — F6 validity cannot be proven")
    else:
        u21_hits = _pin_hits(u21, U21_PINS, verts)
        u22_hits = _pin_hits(u22, U22_PINS, verts)
        report.u21_pins = u21_hits
        inn = _one_net(u21_hits["2"])
        out = _one_net(u22_hits["1"])
        report.paths["f6"] = {"u21_in": inn, "u22_out": out}
        assertions += 1
        if inn == "5V_PROTECTED":
            errors.append("U21.2 IN is 5V_PROTECTED — F6_VALIDITY_SOURCE must be 5V0_USB_VALID")
        elif inn != "5V0_USB_VALID":
            errors.append(f"U21.2 IN present={inn or 'OPEN'} expected=5V0_USB_VALID")
        assertions += 1
        if out not in {None, "5V0_USB_VALID"} and out != inn:
            warnings.append(f"U22.1 OUT is {out}")
        if out != "5V0_USB_VALID":
            errors.append(f"U22.1 OUT present={out or 'OPEN'} expected=5V0_USB_VALID")

    # --- series / bypass ---
    for des in SERIES_AUDIT:
        row = {"present": des in components, "classification": "ABSENT", "nets": None}
        if des in components:
            a, b = _two_pin_nets(components[des], verts)
            row["nets"] = [a, b]
            if not a and not b:
                row["classification"] = "OPEN"
            elif a == b and len(a) == 1:
                row["classification"] = "DEFECT"
                if des in SAME_NET_EXCEPTIONS:
                    row["classification"] = "INTENTIONAL_SAME_NET"
                    warnings.append(f"{des} same-net allowed: {SAME_NET_EXCEPTIONS[des]}")
                else:
                    errors.append(f"{des} same-net bypass on {a[0]}")
            elif a and b and set(a) != set(b):
                row["classification"] = "TRUE_SERIES"
            else:
                row["classification"] = "UNRESOLVED"
                errors.append(f"{des} series landing unresolved a={a} b={b}")
        else:
            errors.append(f"{des} missing from series/bypass audit")
        report.series[des] = row
        assertions += 1

    report.counts["assertions_executed"] = assertions
    vacuous = [k for k, v in report.counts.items() if v == 0]
    if vacuous:
        report.unresolved = True
        errors.append(f"vacuous counts: {report.counts}")
    report.ok = (not errors) and (not report.unresolved)
    return report


def fixture_v3(
    *,
    wire_j1: bool = True,
    r94_same_net: bool = False,
    prtpwr2_gnd: bool = False,
    include_support: bool = True,
    dn_on_3v3: bool = False,
    xtalout_gnd: bool = False,
    rbias_on_xtalin: bool = False,
    retired_j1_xy: tuple[int, int] | None = None,
    ocs_picture_frame: bool = False,
) -> str:
    """Minimal V3 sheet for the USB hub assertions."""

    def rec(typ: str, id_: str, payload: dict, ticket: int) -> str:
        header = json.dumps({"type": typ, "ticket": ticket, "id": id_}, separators=(",", ":"))
        return f"{header}||{json.dumps(payload, separators=(',', ':'))}|"

    rows: list[str] = []
    ticket = 1

    def add(typ, id_, payload):
        nonlocal ticket
        rows.append(rec(typ, id_, payload, ticket))
        ticket += 1

    def component(eid, part, x, y, designator, rotation=0):
        add("COMPONENT", eid, {"partId": part, "x": x, "y": y, "rotation": rotation, "isMirror": False})
        add("ATTR", f"d{eid}", {"parentId": eid, "key": "Designator", "value": designator})

    def wire(wid: str, net: str, segments: list[tuple[int, int, int, int]]):
        add("WIRE", wid, {"zIndex": 1, "locked": False})
        add("ATTR", f"n{wid}", {"parentId": wid, "key": "NET", "value": net})
        for i, (sx, sy, ex, ey) in enumerate(segments):
            add("LINE", f"l{wid}{i}", {"startX": sx, "startY": sy, "endX": ex, "endY": ey, "lineGroup": wid})

    def stub_at(wid, net, xy, dx=20):
        x, y = xy
        wire(wid, net, [(x, y, x + dx, y)])

    component("eJ1", "GT-USB-7005A-IND.1", 150, -4120, J1_DESIGNATOR)
    component("eU1", "TPS259474LRPWR.1", 690, -4110, "U1-PWR1")
    component("eU17", "TPS62913RPUR.1", 200, -3000, "U17-PWR2")
    component("eU20", "USB2422T-I/MJ.1", 400, -800, U20_DESIGNATOR)
    component("eU21", "TPS2052BDR.1", 1200, -800, U21_DESIGNATOR)
    component("eU22", "TPS7A2550DRVR.1", 1500, -600, U22_DESIGNATOR)
    component("eU6", "MIMXRT1062DVJ6B.1", 2250, -3930, U6_DESIGNATOR, 90)
    component("eU9", "ESP32-S3-WROOM-1.1", 4260, -4365, U9_DESIGNATOR)
    component("eRusb", "RC0402FR-070RL.1", 555, -4165, RUSB_DP)
    component("eR94", "RC0402FR-070RL.1", 2100, -800, R94)
    component("eR95", "RC0402FR-070RL.1", 2100, -1000, R95)
    component("eR85", "0402WGF4700TCE.1", 1720, -1200, R85)
    component("eR90", "0402WGF1002TCE.1", 760, -980, R90)
    component("eC123", "CC0603KRX7R9BB104.1", 1420, -1100, C123)
    component("eTune", "0402WGF220JTCE.1", 4000, -4280, TUNE_DP)
    component("eY3", "X322524MSB4SI.1", 845, -735, Y3)
    component("eR77", "0402WGF1202TCE.1", 200, -980, R77)
    component("eC100", "CL10A105KB8NNNC.1", 200, -1100, C100)
    component("eC101", "CC0603KRX7R9BB104.1", 280, -1100, C101)
    component("eJ6", "HEADER_1X6.1", 4770, -4490, J6)

    j1 = {"x": 150, "y": -4120, "rotation": 0, "isMirror": False}
    u20 = {"x": 400, "y": -800, "rotation": 0, "isMirror": False}
    u21 = {"x": 1200, "y": -800, "rotation": 0, "isMirror": False}
    u22 = {"x": 1500, "y": -600, "rotation": 0, "isMirror": False}

    if wire_j1:
        for pin, spec in J1_PINS.items():
            if spec["group"] == "NC":
                continue
            net = spec["expect"]
            if spec["group"] == "DP":
                net = "USB_DP_J1"
            elif spec["group"] == "DM":
                net = "USB_DN_J1"
            stub_at(f"wJ1{pin}", net, pin_xy(j1, spec["sx"], spec["sy"]))

    # USB2422 required pins
    pin_nets = {
        "1": "3V3",
        "2": "USB_DM_DN2",
        "3": "USB_DM_DN1",
        "4": "USB_DP_DN1",
        "5": "USB_DP_DN2",
        "7": "USB_PRTPWR1",
        "8": "USB_OCS1_N",
        "9": "3V3",
        "11": "GND" if prtpwr2_gnd else "USB_PRTPWR2",
        "12": "USB_OCS2_N",
        "13": "3V3",
        "14": "GND",
        "15": "USB_RESET_N",
        "16": "USB_VBUS_DET",
        "17": "GND",
        "18": "3V3",
        "19": "USB_DM_UP",
        "20": "USB_DP_UP",
        "21": "GND" if xtalout_gnd else "USB_XTALOUT",
        "22": "USB_XTALIN",
        "25": "GND",
    }
    if dn_on_3v3:
        for pin in ("2", "3", "4", "5"):
            pin_nets[pin] = "3V3"
    if include_support:
        pin_nets["10"] = "USB_CRFILT"
        pin_nets["23"] = "USB_PLLFILT"
        pin_nets["24"] = "USB_XTALIN" if rbias_on_xtalin else "USB_RBIAS"
    for pin, net in pin_nets.items():
        spec = USB2422_PINS[pin]
        stub_at(f"wU20{pin}", net, pin_xy(u20, spec["sx"], spec["sy"]))

    stub_at("wU21in", "5V0_USB_VALID", pin_xy(u21, U21_PINS["2"]["sx"], U21_PINS["2"]["sy"]))
    stub_at("wU22out", "5V0_USB_VALID", pin_xy(u22, U22_PINS["1"]["sx"], U22_PINS["1"]["sy"]))

    # RUSB series PROT → UP
    wire("wRusb1", "USB_DP_PROT", [(535, -4165, 555, -4165)])
    wire("wRusb2", "USB_DP_UP", [(555, -4165, 575, -4165)])

    # R94
    if r94_same_net:
        wire("wR94a", "USB_DP_DN2", [(2080, -800, 2120, -800)])
    else:
        wire("wR94a", "USB_DP_DN2", [(2080, -800, 2090, -800)])
        wire("wR94b", "USB_DP_DN2_SEL", [(2110, -800, 2120, -800)])

    # R85 / R90 / C123 as true series
    wire("wR85a", "USB_5V_VALID", [(1700, -1200, 1710, -1200)])
    wire("wR85b", "USB_5V_VALID_S3", [(1730, -1200, 1740, -1200)])
    wire("wR90a", "USB_NON_REM1", [(740, -980, 750, -980)])
    wire("wR90b", "3V3", [(770, -980, 780, -980)])
    wire("wC123a", "3V3", [(1400, -1100, 1410, -1100)])
    wire("wC123b", "GND", [(1430, -1100, 1440, -1100)])

    # Tune + S3 + RT proximity
    wire("wTune1", "USB_DP_DN2_SEL", [(3980, -4280, 4000, -4280)])
    wire("wTune2", "USB_DP_S3", [(4000, -4280, 4020, -4280)])
    wire("wS3", "USB_DP_S3", [(4175, -4280, 4200, -4280)])
    wire("wRT", "USB_DP_DN1", [(2490, -4040, 2510, -4040)])
    wire("wRTm", "USB_DM_DN1", [(2350, -4040, 2370, -4040)])

    if include_support:
        stub_at("wY3a", "USB_XTALIN", (825, -735))
        stub_at("wY3b", "USB_XTALOUT", (865, -735), dx=-20)
        stub_at("wR77a", "USB_RBIAS", (180, -980))
        stub_at("wR77b", "GND", (220, -980), dx=-20)
        stub_at("wC100a", "USB_CRFILT", (180, -1100))
        stub_at("wC100b", "GND", (220, -1100), dx=-20)
        stub_at("wC101a", "USB_PLLFILT", (260, -1100))
        stub_at("wC101b", "GND", (300, -1100), dx=-20)

    if retired_j1_xy is not None:
        component(
            "eJ1r",
            "USB4105-A-GF-A.1",
            retired_j1_xy[0],
            retired_j1_xy[1],
            RETIRED_J1,
        )
    if ocs_picture_frame:
        wire("wOcsFrame", "USB_OCS1_N", [(90, -1500, 1285, -1500)])

    return "\n".join(rows) + "\n"


def load_and_analyse(path) -> UsbHubReport:
    source, _ = _load_source(path)
    return analyse(source, source_path=str(path))
