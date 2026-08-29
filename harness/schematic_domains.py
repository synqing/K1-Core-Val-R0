#!/usr/bin/env python3
"""Domain assignment, net classification, and signal-weighted adjacency.

GND and raw power-fanout must not drive schematic placement. Weighting rules
are the contract for floorplan code; do not invent a second scheme.
"""
from __future__ import annotations

import re
from collections import defaultdict

SUFFIX_DOMAIN = {
    "PWR1": "power_entry",
    "PWR2": "power_reg",
    "USB": "usb_hub",
    "RTC": "rt1062",
    "RTC1": "rt1062",
    "RTDBG": "debug",
    "ESP": "s3",
    "AUD": "audio",
    "NFC": "nfc",
    "MOT": "motion",
    "LED": "led",
    "VAL": "validation",
    "BULK": "power_reg",
}

DOMAINS = (
    "power_entry",
    "usb_hub",
    "power_reg",
    "audio",
    "rt1062",
    "led",
    "debug",
    "s3",
    "nfc",
    "motion",
    "validation",
)

# Declared human reading flow. Residual graph weight may not override this.
READING_ORDER = list(DOMAINS)

GND_NETS = re.compile(r"^(GND|AGND|DGND|PGND|GNDA|GNDD)(_.*)?$", re.I)
POWER_NETS = re.compile(
    r"^(5V_|5V0_|3V3|3V3_|1V8|1V2|VDD|VBUS|5V_SYS|5V_PROTECTED|5V_USB|5V_LED|"
    r"NFC_5V|3V3_MIC|USB_VBUS|RT_USB_VBUS|S3_USB_VBUS|VBAT)",
    re.I,
)
HIGH_FANOUT_CONTROL = re.compile(
    r"(IOMUX_TBD|POR|RESET|BOOT|EN_|_EN$|_PG$|FAULT|ALERT)",
    re.I,
)

BUS_GROUPS = {
    "k1br": re.compile(r"K1BR|SPI_MCU|BRIDGE", re.I),
    "tdm": re.compile(r"(BCLK|FSYNC|SDOUT|SDIN|MCLK|SAI|I2S|TDM)", re.I),
    "i2c": re.compile(r"I2C_|_SDA|_SCL", re.I),
    "usb_data": re.compile(r"USB_D[PM]|USB2_|USB_DP_|USB_DM_|DP_|DN_", re.I),
    "pdm": re.compile(r"PDM_", re.I),
}

FUNCTIONAL_PAIRS = {
    frozenset(("rt1062", "audio")): 4.0,
    frozenset(("rt1062", "led")): 3.5,
    frozenset(("rt1062", "debug")): 3.0,
    frozenset(("rt1062", "s3")): 3.0,
    frozenset(("s3", "nfc")): 3.0,
    frozenset(("s3", "debug")): 2.5,
    frozenset(("power_entry", "power_reg")): 4.0,
    frozenset(("power_entry", "usb_hub")): 4.0,
    frozenset(("usb_hub", "rt1062")): 3.0,
    frozenset(("usb_hub", "s3")): 3.0,
    frozenset(("power_reg", "rt1062")): 1.2,
    frozenset(("power_reg", "led")): 2.0,
    frozenset(("s3", "motion")): 1.5,
    frozenset(("rt1062", "motion")): 1.5,
}

SI_NETS = re.compile(r"(USB_D|RFO|RFI|ANT|XTAL|OSC|PDM_|BCLK|MCLK)", re.I)
OWNERSHIP_NETS = re.compile(
    r"(RESET|BOOT|I2C_SEL|I2C_EN|LED_ARM|LED_EN|RECOVERY|UART)",
    re.I,
)


def domain_for_designator(designator: str) -> str:
    if "-" not in designator:
        return "validation"
    suffix = designator.rsplit("-", 1)[-1]
    return SUFFIX_DOMAIN.get(suffix, "validation")


def classify_net(name: str) -> str:
    if not name:
        return "unknown"
    if GND_NETS.match(name):
        return "gnd"
    if POWER_NETS.match(name):
        return "power"
    if SI_NETS.search(name):
        return "si"
    if OWNERSHIP_NETS.search(name):
        return "ownership"
    for group, pattern in BUS_GROUPS.items():
        if pattern.search(name):
            return f"bus:{group}"
    if HIGH_FANOUT_CONTROL.search(name):
        return "control"
    return "signal"


def net_placement_weight(name: str) -> float:
    kind = classify_net(name)
    if kind == "gnd":
        return 0.0
    if kind == "power":
        return 0.05
    if kind == "control":
        return 0.1
    if kind.startswith("bus:"):
        return 1.0
    if kind == "si":
        return 2.5
    if kind == "ownership":
        return 2.0
    return 1.5


def bus_key(name: str) -> str:
    kind = classify_net(name)
    if kind.startswith("bus:"):
        return kind
    return f"net:{name}"


def adjacency_from_membership(designator_nets: dict[str, set[str]]) -> dict:
    """Weighted undirected domain graph. GND excluded. Buses collapsed."""
    domain_of = {d: domain_for_designator(d) for d in designator_nets}
    interface_domains: dict[str, set[str]] = defaultdict(set)
    for designator, nets in designator_nets.items():
        domain = domain_of[designator]
        seen_bus = set()
        for net in nets:
            if classify_net(net) == "gnd":
                continue
            key = bus_key(net)
            if key in seen_bus:
                continue
            seen_bus.add(key)
            interface_domains[key].add(domain)

    weights = defaultdict(float)
    for key, domains in interface_domains.items():
        if len(domains) < 2:
            continue
        name = key[4:] if key.startswith("net:") else key
        weight = net_placement_weight(name if key.startswith("net:") else name)
        domains = sorted(domains)
        for i, left in enumerate(domains):
            for right in domains[i + 1 :]:
                weights[frozenset((left, right))] += weight

    for pair, bonus in FUNCTIONAL_PAIRS.items():
        weights[pair] += bonus

    residual = {
        f"{min(pair)}|{max(pair)}": round(value, 3)
        for pair, value in sorted(weights.items(), key=lambda item: (-item[1], tuple(item[0])))
        if value > 0
    }
    return {
        "weights": residual,
        "reading_order": READING_ORDER,
        "rule": "reading_order_overrides_residual_weight",
    }


def declared_region_boxes(origin=(200, 200), cell=(4200, 2800), gap=400):
    """Soft-region boxes in schematic units (0.01 inch). Not prison cells."""
    # west spine, centre RT, east S3 — reading flow, not a 2x5 grid of equals
    layout = {
        "power_entry": (origin[0], origin[1], 3800, 2400),
        "usb_hub": (origin[0], origin[1] + 2600, 3800, 2600),
        "power_reg": (origin[0], origin[1] + 5400, 3800, 2400),
        "audio": (origin[0] + 4200, origin[1] + 2800, 3600, 2400),
        "rt1062": (origin[0] + 4200, origin[1], 4200, 2600),
        "led": (origin[0] + 8600, origin[1], 3600, 2400),
        "debug": (origin[0] + 4200, origin[1] + 5600, 3600, 2000),
        "s3": (origin[0] + 8000, origin[1] + 2800, 4200, 2600),
        "nfc": (origin[0] + 12400, origin[1] + 2800, 3200, 2000),
        "motion": (origin[0] + 12400, origin[1] + 5000, 2800, 1800),
        "validation": (origin[0] + 8600, origin[1] + 5600, 3600, 2000),
    }
    return {k: {"x": v[0], "y": v[1], "w": v[2], "h": v[3]} for k, v in layout.items()}
