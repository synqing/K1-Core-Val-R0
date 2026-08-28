#!/usr/bin/env python3
"""Build the VAL-G2.0A Option-C fixture plan from architecture and contracts.

This is the circuit inventory the last session never wrote. Counts are a consequence
of the topology, not the target. EasyEDA library UUIDs here are stable MPN/value
bind keys; VAL-G2.0B must resolve them through search_library_devices before place.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
OUT = Path(__file__).resolve().parent / "FIXTURE-PLAN.json"

# Sheet columns follow signal/power flow, not a parts catalogue.
ORIGIN = {
    "POWER_ENTRY": (80, 80),
    "POWER_SENSE": (80, 520),
    "POWER_BUCK": (80, 900),
    "POWER_LED": (80, 1400),
    "POWER_BRANCH": (80, 1780),
    "RT_CORE": (1100, 80),
    "RT_DECOUPLE": (1100, 620),
    "RT_CLOCK_MEM": (1100, 1280),
    "RT_DEBUG": (1100, 1680),
    "ESP_CORE": (2200, 80),
    "ESP_USB": (2200, 720),
    "K1BR": (2200, 1180),
    "AUDIO_ADC": (3300, 80),
    "AUDIO_CLOCK": (3300, 720),
    "AUDIO_MIC": (3300, 1180),
    "NFC": (4400, 80),
    "MOTION": (4400, 1100),
    "LED_DATA": (5500, 80),
    "OPTIONS": (5500, 720),
    "DEBUG_FABRIC": (5500, 1100),
}

DOMAIN_OF_BLOCK = {
    "POWER_ENTRY": "POWER",
    "POWER_SENSE": "POWER",
    "POWER_BUCK": "POWER",
    "POWER_LED": "LED",
    "POWER_BRANCH": "POWER",
    "RT_CORE": "RT1062_SUPPORT",
    "RT_DECOUPLE": "RT1062_SUPPORT",
    "RT_CLOCK_MEM": "RT1062_SUPPORT",
    "RT_DEBUG": "DEBUG",
    "ESP_CORE": "ESP32_S3_SUPPORT",
    "ESP_USB": "USB",
    "K1BR": "K1BR",
    "AUDIO_ADC": "AUDIO",
    "AUDIO_CLOCK": "AUDIO",
    "AUDIO_MIC": "AUDIO",
    "NFC": "NFC",
    "MOTION": "MOTION",
    "LED_DATA": "LED",
    "OPTIONS": "OPTIONS",
    "DEBUG_FABRIC": "DEBUG",
}

PLACEMENT_INTENT = {
    "POWER_ENTRY": "USB entry and eFuse sit at the source; protected 5 V leaves to the right toward sense and conversion",
    "POWER_SENSE": "Shunt sits in the 5 V trunk; INA226 Kelvin-senses beside it",
    "POWER_BUCK": "TPS62913 input capacitors at the 5 V arrival, inductor and 3V3 bulk toward the loads",
    "POWER_LED": "LED eFuse after 5V_SYS; left and right LED rails leave toward the west-edge connectors",
    "POWER_BRANCH": "Microphone LDO and NFC 5 V filter hang off 5V_SYS toward their domains",
    "RT_CORE": "Reset supervisor and boot straps at the POR_B side; RT1062 body central in the compute cluster",
    "RT_DECOUPLE": "Local decoupling stays beside the RT1062 rail pins it serves, not in a remote bank",
    "RT_CLOCK_MEM": "24 MHz crystal beside the oscillator pins; QSPI flash on the FlexSPI escape",
    "RT_DEBUG": "SWD header and BootROM UART sit on the RT1062 side, never through ESP32_S3",
    "ESP_CORE": "WROOM module with EN/BOOT support at the radio cluster; antenna clearance implied to the east",
    "ESP_USB": "Service USB connector and ESD at the ESP32_S3 USB PHY pins",
    "K1BR": "SPI series resistors sit on the seam between RT1062 master and ESP32_S3 slave",
    "AUDIO_ADC": "TLV320ADC6120 central; supply decoupling local; TDM toward RT1062 SAI",
    "AUDIO_CLOCK": "Series and isolation options on AUDIO_MCLK/BCLK/FSYNC so a laboratory clock can take over",
    "AUDIO_MIC": "Flex microphone connector and 0R XOR so the two PDM routes cannot load the bus together",
    "NFC": "ST25R3916B, 27.12 MHz crystal and matching stay on the carrier; antenna terminals at the RF edge",
    "MOTION": "Accelerometer near structural centre; 0R XOR matrix drawn beside the I2C and IRQ lines",
    "LED_DATA": "Level shifters between RT1062 3.3 V data and the 5 V strip connectors J2/J3",
    "OPTIONS": "Option links as fitted or DNP resistors on named validation straps",
    "DEBUG_FABRIC": "POR_B wired-OR parts and the ESP32_S3-independent Serial Downloader path beside debug",
}


def device_uuid(key: str) -> str:
    return hashlib.md5(("easyeda-device|" + key).encode("utf-8")).hexdigest()


def library_uuid(key: str) -> str:
    return hashlib.md5(("easyeda-library|" + key).encode("utf-8")).hexdigest()


def source(document: str, revision: str, locator: str, url_or_path: str, requirement_type: str | None = None) -> dict:
    payload = {
        "document": document,
        "revision": revision,
        "locator": locator,
        "url_or_path": url_or_path,
    }
    if requirement_type is not None:
        payload["requirement_type"] = requirement_type
    return payload


SRC = {
    "power": source(
        "architecture/POWER-ARCHITECTURE.md", "2026-08-28", "power-tree",
        "architecture/POWER-ARCHITECTURE.md", "K1_CONTRACT_REQUIRED",
    ),
    "clock": source(
        "architecture/CLOCK-ARCHITECTURE.md", "2026-08-28", "audio-and-inter-mcu-clocks",
        "architecture/CLOCK-ARCHITECTURE.md", "K1_CONTRACT_REQUIRED",
    ),
    "audio": source(
        "contracts/audio-interface.md", "RATIFIED", "capture-and-clocks",
        "contracts/audio-interface.md", "K1_CONTRACT_REQUIRED",
    ),
    "mic": source(
        "contracts/microphone-interface.md", "RATIFIED", "im69d130-flex-and-xor",
        "contracts/microphone-interface.md", "K1_CONTRACT_REQUIRED",
    ),
    "led": source(
        "contracts/led-interface.md", "RATIFIED", "dual-channel-level-shift",
        "contracts/led-interface.md", "K1_CONTRACT_REQUIRED",
    ),
    "nfc": source(
        "contracts/nfc-interface.md", "RATIFIED", "st25r3916b-carrier-frontend",
        "contracts/nfc-interface.md", "K1_CONTRACT_REQUIRED",
    ),
    "motion": source(
        "contracts/motion-interface.md", "DEFAULT", "i2c-irq-ownership-matrix",
        "contracts/motion-interface.md", "K1_CONTRACT_REQUIRED",
    ),
    "usb": source(
        "contracts/usb-interface.md", "RATIFIED", "service-usb-esp32-s3",
        "contracts/usb-interface.md", "K1_CONTRACT_REQUIRED",
    ),
    "k1br": source(
        "contracts/k1br-bridge.md", "RATIFIED", "spi-command-state-telemetry",
        "contracts/k1br-bridge.md", "K1_CONTRACT_REQUIRED",
    ),
    "debug": source(
        "contracts/debug-fabric.md", "REQUIREMENTS_ONLY", "boot-reset-uart-swd",
        "contracts/debug-fabric.md", "K1_CONTRACT_REQUIRED",
    ),
    "rt_pkg": source(
        "authority/01-DECISION-REGISTER.md", "D-028", "MIMXRT1062DVJ6B",
        "authority/01-DECISION-REGISTER.md", "K1_CONTRACT_REQUIRED",
    ),
    "rt_ds": source(
        "NXP IMXRT1060CEC / MIMXRT1060-EVKB", "IMXRT1060CEC", "internal-DCDC-decoupling-boot-uart",
        "https://www.nxp.com/docs/en/data-sheet/IMXRT1060CEC.pdf", "DATASHEET_REQUIRED",
    ),
    "s3_hdg": source(
        "Espressif ESP32-S3 Hardware Design Guidelines", "current", "module-power-usb-boot-antenna",
        "https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/",
        "DATASHEET_REQUIRED",
    ),
    "tlv": source(
        "TI TLV320ADC6120 datasheet", "SBAS892", "tdm-pdm-supplies-clocks",
        "https://www.ti.com/product/TLV320ADC6120", "DATASHEET_REQUIRED",
    ),
    "st_an": source(
        "ST AN5240 / ST25R3916B", "AN5240", "crystal-matching-rfo-rfi",
        "https://www.st.com/resource/en/application_note/an5240-antenna-matching-for-st25r3916b-stmicroelectronics.pdf",
        "REFERENCE_DESIGN_REQUIRED",
    ),
    "ina": source(
        "TI INA226 datasheet", "SBOS547", "kelvin-shunt-i2c",
        "https://www.ti.com/product/INA226", "DATASHEET_REQUIRED",
    ),
    "tps62913": source(
        "TI TPS62913 datasheet", "SLUSEA4", "3a-low-noise-buck",
        "https://www.ti.com/product/TPS62913", "DATASHEET_REQUIRED",
    ),
    "tps25947": source(
        "TI TPS25947 datasheet", "SLVSFE9", "efuse-protection",
        "https://www.ti.com/product/TPS25947", "VALIDATION_OPTION",
    ),
    "lis2": source(
        "ST LIS2DH12 datasheet", "DS10998", "i2c-accelerometer-candidate",
        "https://www.st.com/resource/en/datasheet/lis2dh12.pdf", "VALIDATION_OPTION",
    ),
    "stress": source(
        "schematic/single-sheet-qualification/TEST-PLAN.md", "VAL-G2.0A",
        "twenty-percent-stress-margin",
        "schematic/single-sheet-qualification/TEST-PLAN.md", "DERIVED",
    ),
}


class Builder:
    def __init__(self) -> None:
        self.components: list[dict] = []
        self.nets: dict[str, dict] = {}
        self.block_refs: dict[str, list[str]] = defaultdict(list)
        self.cursors = {name: 0 for name in ORIGIN}
        self.used_xy: set[tuple[int, int]] = set()

    def _xy(self, block: str) -> tuple[int, int]:
        n = self.cursors[block]
        self.cursors[block] = n + 1
        x0, y0 = ORIGIN[block]
        col = n % 4
        row = n // 4
        x = x0 + col * 92 + (13 if row % 2 else 0) + (n % 3) * 5
        y = y0 + row * 78 + (9 if col % 2 else 0) + (n % 2) * 6
        while (x, y) in self.used_xy:
            x += 7
            y += 5
        self.used_xy.add((x, y))
        return x, y

    def add(
        self,
        ref: str,
        role: str,
        block: str,
        cls: str,
        mpn: str,
        value: str,
        source_ref: dict,
        rationale: str,
        *,
        fixture_only: bool = False,
        stress_basis: str | None = None,
        lib_family: str | None = None,
        rotation: int = 0,
        shared_device_justification: str | None = None,
    ) -> str:
        domain = DOMAIN_OF_BLOCK[block]
        x, y = self._xy(block)
        family = lib_family or cls
        component = {
            "ref": ref,
            "role": role,
            "domain": domain,
            "class": cls,
            "basis": source_ref["document"] + " / " + source_ref["locator"],
            "fixture_only": fixture_only,
            "manufacturer_part_number": mpn,
            "value": value,
            "device_uuid": device_uuid(mpn + "|" + value),
            "library_uuid": library_uuid(family),
            "source_ref": source_ref,
            "placement_group": block,
            "placement": {
                "x": x,
                "y": y,
                "rotation": rotation,
                "rationale": rationale,
            },
        }
        if fixture_only:
            component["stress_basis"] = stress_basis or "extra rail loading on a real named net"
        if shared_device_justification:
            component["shared_device_justification"] = shared_device_justification
        self.components.append(component)
        self.block_refs[block].append(ref)
        return ref

    def net(
        self,
        name: str,
        kind: str,
        render: str,
        endpoints: list[tuple[str, str, str]],
        source_ref: dict,
        *,
        high_fanout: bool = False,
    ) -> None:
        if name in self.nets:
            existing = self.nets[name]
            have = {(item["ref"], item["pin"]) for item in existing["endpoints"]}
            for ref, pin, pin_name in endpoints:
                if (ref, pin) not in have:
                    existing["endpoints"].append({"ref": ref, "pin": pin, "pin_name": pin_name})
                    have.add((ref, pin))
            if high_fanout:
                existing["high_fanout"] = True
            if render == "explicit_wire":
                existing["render"] = "explicit_wire"
            return
        self.nets[name] = {
            "name": name,
            "kind": kind,
            "render": render,
            "high_fanout": high_fanout,
            "source_ref": {k: v for k, v in source_ref.items() if k != "requirement_type"},
            "endpoints": [
                {"ref": ref, "pin": pin, "pin_name": pin_name}
                for ref, pin, pin_name in endpoints
            ],
        }

    def pair(
        self,
        name: str,
        left: tuple[str, str, str],
        right: tuple[str, str, str],
        source_ref: dict,
        kind: str = "signal",
        render: str = "explicit_wire",
    ) -> None:
        self.net(name, kind, render, [left, right], source_ref)


def populate(b: Builder) -> None:
    # --- Power entry ---
    b.add("J1", "power_entry", "POWER_ENTRY", "power", "USB4105-GF-A", "USB-C-PWR",
          SRC["power"], "USB-C power/data entry at the trunk source")
    b.add("F1", "usb_ferrite", "POWER_ENTRY", "passive", "BLM21PG221SN1D", "220ohm@100MHz",
          SRC["power"], "Ferrite on VBUS immediately after the connector")
    b.add("D1", "usb_tvs", "POWER_ENTRY", "protection", "USBLC6-2SC6", "TVS",
          SRC["usb"], "ESD/TVS across the USB power arrival")
    b.add("U1", "usb_efuse", "POWER_ENTRY", "power", "TPS259474L", "eFuse",
          SRC["tps25947"], "eFuse is the contract protection block after USB entry",
          shared_device_justification="same TPS25947 device on two independent eFuse roles: USB trunk and LED branch")
    b.add("C1", "efuse_cin", "POWER_ENTRY", "passive", "GRM21BR61E226ME44L", "22uF",
          SRC["tps25947"], "Input bulk beside the eFuse VIN pin")
    b.add("C2", "efuse_cout", "POWER_ENTRY", "passive", "GRM21BR61E226ME44L", "22uF",
          SRC["tps25947"], "Output bulk on 5V_PROTECTED beside the eFuse VOUT pin")
    b.add("R1", "efuse_ilim", "POWER_ENTRY", "passive", "RC0402FR-071K33L", "1.33k",
          SRC["tps25947"], "ILIM resistor at the eFuse current-limit pin")
    b.add("R2", "efuse_en", "POWER_ENTRY", "passive", "RC0402FR-07100KL", "100k",
          SRC["tps25947"], "Enable pull-up on the eFuse EN pin")

    b.pair("5V_USB", ("J1", "A4", "VBUS"), ("F1", "1", "1"), SRC["power"], "power")
    b.pair("5V_USB_FILTERED", ("F1", "2", "2"), ("U1", "IN", "IN"), SRC["power"], "power")
    b.net("5V_PROTECTED", "power", "explicit_wire", [
        ("U1", "OUT", "OUT"), ("C2", "1", "1"), ("D1", "1", "1"),
    ], SRC["power"], high_fanout=True)
    b.pair("USB_EFUSE_ILIM", ("U1", "ILIM", "ILIM"), ("R1", "1", "1"), SRC["tps25947"])
    b.pair("USB_EFUSE_EN", ("U1", "EN", "EN"), ("R2", "1", "1"), SRC["tps25947"], "control")
    b.net("GND", "ground", "explicit_wire", [
        ("J1", "A1", "GND"), ("U1", "GND", "GND"), ("C1", "2", "2"), ("C2", "2", "2"),
        ("D1", "2", "2"), ("R1", "2", "2"), ("R2", "2", "2"),
    ], SRC["power"], high_fanout=True)
    b.net("5V_USB_FILTERED", "power", "labelled_net", [("C1", "1", "1")], SRC["tps25947"])

    # --- Sense ---
    b.add("RSH1", "trunk_shunt", "POWER_SENSE", "passive", "WSHP2818R0100FEA", "10mohm",
          SRC["power"], "Kelvin shunt in the 5 V trunk after the eFuse")
    b.add("U2", "trunk_ina", "POWER_SENSE", "support_ic", "INA226AIDGSR", "INA226",
          SRC["ina"], "INA226 beside the shunt for high-side Kelvin sense")
    b.add("C3", "ina_vcc", "POWER_SENSE", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["ina"], "INA226 VCC decoupling")
    b.add("C4", "ina_bypass", "POWER_SENSE", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["ina"], "INA226 local bypass")
    b.add("R3", "ina_alert", "POWER_SENSE", "passive", "RC0402FR-0710KL", "10k",
          SRC["ina"], "ALERT pull-up to 3V3")
    b.add("R4", "ina_i2c_pu_a", "POWER_SENSE", "passive", "RC0402FR-074K7L", "4.7k",
          SRC["ina"], "SDA pull-up at the power-monitor")

    b.net("5V_PROTECTED", "power", "explicit_wire", [
        ("RSH1", "1", "1"), ("U2", "VIN+", "VIN+"),
    ], SRC["power"], high_fanout=True)
    b.net("5V_SYS", "power", "explicit_wire", [
        ("RSH1", "2", "2"), ("U2", "VBUS", "VBUS"), ("U2", "VIN-", "VIN-"),
    ], SRC["power"], high_fanout=True)
    b.net("GND", "ground", "explicit_wire", [
        ("U2", "GND", "GND"), ("C3", "2", "2"), ("C4", "2", "2"),
    ], SRC["ina"], high_fanout=True)
    b.net("3V3", "power", "labelled_net", [
        ("U2", "VS+", "VS+"), ("C3", "1", "1"), ("C4", "1", "1"),
    ], SRC["ina"])

    # --- Buck ---
    b.add("U3", "sys_buck", "POWER_BUCK", "power", "TPS62913RPUR", "TPS62913",
          SRC["tps62913"], "3.3 V buck at the conversion node of the power tree")
    b.add("L1", "buck_inductor", "POWER_BUCK", "passive", "XGL4030-222MEC", "2.2uH",
          SRC["tps62913"], "Buck inductor between SW and 3V3")
    b.add("C5", "buck_cin", "POWER_BUCK", "passive", "GRM21BR61E226ME44L", "22uF",
          SRC["tps62913"], "Buck input bulk at VIN")
    b.add("C6", "buck_cout_a", "POWER_BUCK", "passive", "GRM21BR61A476ME15L", "47uF",
          SRC["tps62913"], "First 3V3 output bulk at the inductor arrival")
    b.add("C7", "buck_cout_b", "POWER_BUCK", "passive", "GRM21BR61A476ME15L", "47uF",
          SRC["tps62913"], "Second 3V3 output bulk for the system rail")
    b.add("C8", "buck_hf", "POWER_BUCK", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["tps62913"], "High-frequency 3V3 ceramic at the buck output")
    b.add("R5", "buck_fb_hi", "POWER_BUCK", "passive", "RC0402FR-07100KL", "100k",
          SRC["tps62913"], "Feedback upper resistor at FB")
    b.add("R6", "buck_fb_lo", "POWER_BUCK", "passive", "RC0402FR-0732K4L", "32.4k",
          SRC["tps62913"], "Feedback lower resistor at FB to ground")
    b.add("C9", "buck_ff", "POWER_BUCK", "passive", "GRM1555C1H101JA01D", "100pF",
          SRC["tps62913"], "Feed-forward capacitor across the upper feedback resistor")
    b.add("R7", "buck_en", "POWER_BUCK", "passive", "RC0402FR-07100KL", "100k",
          SRC["tps62913"], "Buck enable pull-up to 5V_SYS")
    b.add("C10", "buck_ss", "POWER_BUCK", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["tps62913"], "Soft-start capacitor at SS")

    b.net("5V_SYS", "power", "explicit_wire", [
        ("U3", "VIN", "VIN"), ("C5", "1", "1"), ("R7", "1", "1"),
    ], SRC["power"], high_fanout=True)
    b.pair("BUCK_SW", ("U3", "SW", "SW"), ("L1", "1", "1"), SRC["tps62913"], "power")
    b.net("3V3", "power", "explicit_wire", [
        ("L1", "2", "2"), ("C6", "1", "1"), ("C7", "1", "1"), ("C8", "1", "1"),
        ("R5", "1", "1"), ("U2", "VS+", "VS+"),
    ], SRC["power"], high_fanout=True)
    b.net("BUCK_FB", "signal", "explicit_wire", [
        ("U3", "FB", "FB"), ("R5", "2", "2"), ("R6", "1", "1"),
    ], SRC["tps62913"])
    b.pair("BUCK_EN", ("U3", "EN", "EN"), ("R7", "2", "2"), SRC["tps62913"], "control")
    b.pair("BUCK_SS", ("U3", "SS", "SS"), ("C10", "1", "1"), SRC["tps62913"])
    b.net("3V3", "power", "labelled_net", [("C9", "1", "1")], SRC["tps62913"])
    b.net("BUCK_FB", "signal", "labelled_net", [("C9", "2", "2")], SRC["tps62913"])
    b.net("GND", "ground", "explicit_wire", [
        ("U3", "GND", "GND"), ("C5", "2", "2"), ("C6", "2", "2"), ("C7", "2", "2"),
        ("C8", "2", "2"), ("R6", "2", "2"), ("C10", "2", "2"),
    ], SRC["tps62913"], high_fanout=True)

    # --- LED power ---
    b.add("U4", "led_efuse", "POWER_LED", "power", "TPS259474L", "eFuse",
          SRC["tps25947"], "Dedicated LED-branch eFuse after 5V_SYS",
          shared_device_justification="same TPS25947 device on two independent eFuse roles: USB trunk and LED branch")
    b.add("C11", "led_efuse_c", "POWER_LED", "passive", "GRM21BR61E226ME44L", "22uF",
          SRC["led"], "LED eFuse output bulk before the left/right split")
    b.add("R8", "led_ilim", "POWER_LED", "passive", "RC0402FR-073K48L", "3.48k",
          SRC["tps25947"], "LED eFuse ILIM for the 0.95 A envelope")
    b.add("FB1", "led_l_bead", "POWER_LED", "passive", "BLM21PG221SN1D", "220ohm@100MHz",
          SRC["led"], "Ferrite into the left LED 5 V rail")
    b.add("FB2", "led_r_bead", "POWER_LED", "passive", "BLM21PG221SN1D", "220ohm@100MHz",
          SRC["led"], "Ferrite into the right LED 5 V rail")
    b.add("C12", "led_l_bulk", "POWER_LED", "passive", "GRM21BR61E226ME44L", "22uF",
          SRC["led"], "Left LED rail bulk at the connector feed")
    b.add("C13", "led_r_bulk", "POWER_LED", "passive", "GRM21BR61E226ME44L", "22uF",
          SRC["led"], "Right LED rail bulk at the connector feed")

    b.net("5V_SYS", "power", "explicit_wire", [("U4", "IN", "IN")], SRC["led"], high_fanout=True)
    b.pair("5V_LED_COMMON", ("U4", "OUT", "OUT"), ("C11", "1", "1"), SRC["led"], "power")
    b.net("5V_LED_COMMON", "power", "explicit_wire", [
        ("FB1", "1", "1"), ("FB2", "1", "1"),
    ], SRC["led"])
    b.net("+5V_LED_L", "power", "explicit_wire", [
        ("FB1", "2", "2"), ("C12", "1", "1"),
    ], SRC["led"], high_fanout=True)
    b.net("+5V_LED_R", "power", "explicit_wire", [
        ("FB2", "2", "2"), ("C13", "1", "1"),
    ], SRC["led"], high_fanout=True)
    b.pair("LED_EFUSE_ILIM", ("U4", "ILIM", "ILIM"), ("R8", "1", "1"), SRC["tps25947"])
    b.net("GND", "ground", "explicit_wire", [
        ("U4", "GND", "GND"), ("C11", "2", "2"), ("C12", "2", "2"), ("C13", "2", "2"), ("R8", "2", "2"),
    ], SRC["led"], high_fanout=True)

    # --- MIC / NFC power branches ---
    b.add("U5", "mic_ldo", "POWER_BRANCH", "power", "TLV75533PDBVR", "3V3-LDO",
          SRC["mic"], "Switched low-noise 3V3_MIC LDO owned with RT1062 capture")
    b.add("C14", "mic_ldo_in", "POWER_BRANCH", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["mic"], "MIC LDO input ceramic")
    b.add("C15", "mic_ldo_out", "POWER_BRANCH", "passive", "GRM155R60J106ME44D", "10uF",
          SRC["mic"], "MIC LDO output bulk")
    b.add("Q1", "mic_load_sw", "POWER_BRANCH", "power", "DMG2305UX", "P-FET",
          SRC["mic"], "MIC_PWR_EN load switch in the 3V3_MIC path")
    b.add("R9", "mic_en_gate", "POWER_BRANCH", "passive", "RC0402FR-07100KL", "100k",
          SRC["mic"], "Gate resistor on MIC_PWR_EN")
    b.add("FB3", "nfc_bead", "POWER_BRANCH", "passive", "BLM21PG221SN1D", "220ohm@100MHz",
          SRC["nfc"], "Ferrite from 5V_SYS into the NFC 5 V filter")
    b.add("C16", "nfc_bulk", "POWER_BRANCH", "passive", "GRM21BR61E226ME44L", "22uF",
          SRC["nfc"], "NFC 5 V bulk after the ferrite")
    b.add("C17", "nfc_hf", "POWER_BRANCH", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["nfc"], "NFC 5 V high-frequency ceramic")

    b.net("5V_SYS", "power", "explicit_wire", [
        ("U5", "IN", "IN"), ("C14", "1", "1"), ("FB3", "1", "1"),
    ], SRC["power"], high_fanout=True)
    b.pair("3V3_MIC_REG", ("U5", "OUT", "OUT"), ("Q1", "S", "S"), SRC["mic"], "power")
    b.net("3V3_MIC", "power", "explicit_wire", [
        ("Q1", "D", "D"), ("C15", "1", "1"),
    ], SRC["mic"], high_fanout=True)
    b.pair("MIC_PWR_EN", ("Q1", "G", "G"), ("R9", "1", "1"), SRC["mic"], "control")
    b.net("NFC_5V", "power", "explicit_wire", [
        ("FB3", "2", "2"), ("C16", "1", "1"), ("C17", "1", "1"),
    ], SRC["nfc"], high_fanout=True)
    b.net("GND", "ground", "explicit_wire", [
        ("U5", "GND", "GND"), ("C14", "2", "2"), ("C15", "2", "2"),
        ("C16", "2", "2"), ("C17", "2", "2"), ("R9", "2", "2"),
    ], SRC["power"], high_fanout=True)

    # --- RT1062 core ---
    b.add("U6", "rt1062", "RT_CORE", "processor", "MIMXRT1062DVJ6B", "FITTED",
          SRC["rt_pkg"], "Frozen Option-C compute at the centre of the RT cluster")
    b.add("U7", "rt_reset", "RT_CORE", "support_ic", "TPS3808G33DBVR", "RESET",
          SRC["debug"], "External reset supervisor on POR_B as NXP recommends")
    b.add("R10", "boot_mode0", "RT_CORE", "passive", "RC0402FR-07100KL", "100k",
          SRC["debug"], "BOOT_MODE0 strap beside GPIO_AD_B0_04")
    b.add("R11", "boot_mode1", "RT_CORE", "passive", "RC0402FR-07100KL", "100k",
          SRC["debug"], "BOOT_MODE1 strap beside GPIO_AD_B0_05")
    b.add("C18", "por_cap", "RT_CORE", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["debug"], "POR_B local capacitor at the supervisor")
    b.add("R12", "por_pull", "RT_CORE", "passive", "RC0402FR-0710KL", "10k",
          SRC["debug"], "POR_B pull-up to 3V3")
    b.add("SW1", "manual_reset", "RT_CORE", "option", "PTS645SM43SMTR92LFS", "RESET",
          SRC["debug"], "Manual reset on the POR_B wired-OR")
    b.add("C19", "rt_vddhigh", "RT_CORE", "passive", "GRM155R60J106ME44D", "10uF",
          SRC["rt_ds"], "VDD_HIGH_IN bulk at the RT1062 analog rail")

    b.net("3V3", "power", "explicit_wire", [
        ("U6", "DCDC_IN", "DCDC_IN"), ("U6", "VDD_HIGH_IN", "VDD_HIGH_IN"),
        ("U7", "VDD", "VDD"), ("R12", "1", "1"), ("C19", "1", "1"),
    ], SRC["rt_ds"], high_fanout=True)
    b.net("GND", "ground", "explicit_wire", [
        ("U6", "VSS", "VSS"), ("U7", "GND", "GND"), ("C18", "2", "2"),
        ("C19", "2", "2"), ("R10", "2", "2"), ("R11", "2", "2"),
    ], SRC["rt_ds"], high_fanout=True)
    b.net("POR_B", "control", "explicit_wire", [
        ("U6", "POR_B", "POR_B"), ("U7", "RESET", "RESET"),
        ("C18", "1", "1"), ("R12", "2", "2"), ("SW1", "1", "1"),
    ], SRC["debug"], high_fanout=True)
    b.pair("BOOT_MODE0", ("U6", "AD_B0_04", "GPIO_AD_B0_04"), ("R10", "1", "1"), SRC["debug"], "control")
    b.pair("BOOT_MODE1", ("U6", "AD_B0_05", "GPIO_AD_B0_05"), ("R11", "1", "1"), SRC["debug"], "control")
    b.net("GND", "ground", "labelled_net", [("SW1", "2", "2")], SRC["debug"])
    b.pair("MIC_PWR_EN", ("U6", "AD_B1_00", "GPIO_AD_B1_00"), ("R9", "1", "1"), SRC["mic"], "control", "labelled_net")

    # --- RT decoupling (NXP internal DCDC / rail table, representative fitted set) ---
    for idx, (ref, role, value, mpn, pin) in enumerate((
        ("C20", "rt_dcdc_in_hf", "100nF", "GRM155R71C104KA88D", "DCDC_IN"),
        ("C21", "rt_dcdc_in_bulk", "4.7uF", "GRM155R60J475ME47D", "DCDC_IN"),
        ("C22", "rt_soc_hf", "100nF", "GRM155R71C104KA88D", "VDD_SOC_IN"),
        ("C23", "rt_soc_bulk", "10uF", "GRM155R60J106ME44D", "VDD_SOC_IN"),
        ("C24", "rt_gpio1_hf", "100nF", "GRM155R71C104KA88D", "NVCC_GPIO"),
        ("C25", "rt_gpio2_hf", "100nF", "GRM155R71C104KA88D", "NVCC_GPIO"),
        ("C26", "rt_gpio_bulk", "4.7uF", "GRM155R60J475ME47D", "NVCC_GPIO"),
        ("C27", "rt_snvs", "100nF", "GRM155R71C104KA88D", "VDD_SNVS_IN"),
        ("C28", "rt_usb_otg1", "100nF", "GRM155R71C104KA88D", "VDD_USB_CAP"),
        ("C29", "rt_adc", "100nF", "GRM155R71C104KA88D", "VDDA_ADC_3P3"),
        ("C30", "rt_pll", "100nF", "GRM155R71C104KA88D", "NVCC_PLL"),
        ("C31", "rt_dcdc_out", "4.7uF", "GRM155R60J475ME47D", "DCDC_LP"),
        ("C32", "rt_vddhigh_hf", "100nF", "GRM155R71C104KA88D", "VDD_HIGH_IN"),
        ("C33", "rt_nvcc_sd0", "100nF", "GRM155R71C104KA88D", "NVCC_SD0"),
        ("C34", "rt_nvcc_sd1", "100nF", "GRM155R71C104KA88D", "NVCC_SD1"),
    ), start=1):
        b.add(ref, role, "RT_DECOUPLE", "passive", mpn, value, SRC["rt_ds"],
              "NXP rail decoupling beside the %s pin group" % pin)
        rail = "3V3" if pin != "DCDC_LP" else "1V15_CORE"
        kind = "power"
        if pin == "DCDC_LP":
            b.net("1V15_CORE", "power", "labelled_net", [
                ("U6", "DCDC_LP", "DCDC_LP"), (ref, "1", "1"),
            ], SRC["rt_ds"])
        else:
            b.net("3V3", "power", "labelled_net", [
                ("U6", pin, pin), (ref, "1", "1"),
            ], SRC["rt_ds"])
        b.net("GND", "ground", "labelled_net", [(ref, "2", "2")], SRC["rt_ds"], high_fanout=True)

    # --- Clock / memory ---
    b.add("Y1", "rt_xtal", "RT_CLOCK_MEM", "clock", "XRCGB24M000F3A00R0", "24MHz",
          SRC["rt_ds"], "24 MHz crystal beside the RT1062 oscillator pins")
    b.add("C35", "xtal_c1", "RT_CLOCK_MEM", "passive", "GRM1555C1H180JA01D", "18pF",
          SRC["rt_ds"], "Load capacitor on XTALI")
    b.add("C36", "xtal_c2", "RT_CLOCK_MEM", "passive", "GRM1555C1H180JA01D", "18pF",
          SRC["rt_ds"], "Load capacitor on XTALO")
    b.add("R13", "xtal_r", "RT_CLOCK_MEM", "passive", "RC0402FR-070RL", "0R",
          SRC["rt_ds"], "Optional series resistor on XTALO")
    b.add("U8", "qspi_flash", "RT_CLOCK_MEM", "support_ic", "IS25WP064A-JBLE", "64Mbit",
          SRC["rt_ds"], "QSPI flash on FlexSPI as on the NXP EVKB boot path")
    b.add("C37", "flash_vcc", "RT_CLOCK_MEM", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["rt_ds"], "Flash VCC decoupling")
    b.add("C38", "flash_bulk", "RT_CLOCK_MEM", "passive", "GRM155R60J106ME44D", "10uF",
          SRC["rt_ds"], "Flash bulk beside VCC")
    b.add("R14", "flash_wp", "RT_CLOCK_MEM", "passive", "RC0402FR-0710KL", "10k",
          SRC["rt_ds"], "Flash WP pull-up")

    b.pair("XTALI", ("U6", "XTALI", "XTALI"), ("Y1", "1", "1"), SRC["rt_ds"], "clock")
    b.pair("XTALO", ("U6", "XTALO", "XTALO"), ("R13", "1", "1"), SRC["rt_ds"], "clock")
    b.pair("XTALO_Y", ("R13", "2", "2"), ("Y1", "2", "2"), SRC["rt_ds"], "clock")
    b.net("XTALI", "clock", "labelled_net", [("C35", "1", "1")], SRC["rt_ds"])
    b.net("XTALO_Y", "clock", "labelled_net", [("C36", "1", "1")], SRC["rt_ds"])
    b.net("3V3", "power", "labelled_net", [
        ("U8", "VCC", "VCC"), ("C37", "1", "1"), ("C38", "1", "1"), ("R14", "1", "1"),
    ], SRC["rt_ds"], high_fanout=True)
    b.net("GND", "ground", "labelled_net", [
        ("C35", "2", "2"), ("C36", "2", "2"), ("U8", "VSS", "VSS"),
        ("C37", "2", "2"), ("C38", "2", "2"),
    ], SRC["rt_ds"], high_fanout=True)
    # Y1 is two-terminal crystal — do not invent pin 3. Ground the load caps only.
    b.pair("FLEXSPI_SCLK", ("U6", "SD_B1_07", "FLEXSPI_A_SCLK"), ("U8", "SCK", "SCK"), SRC["rt_ds"])
    b.pair("FLEXSPI_SS0", ("U6", "SD_B1_06", "FLEXSPI_A_SS0"), ("U8", "CS", "CS#"), SRC["rt_ds"])
    b.pair("FLEXSPI_D0", ("U6", "SD_B1_08", "FLEXSPI_A_DATA0"), ("U8", "SI", "SI"), SRC["rt_ds"])
    b.pair("FLEXSPI_D1", ("U6", "SD_B1_09", "FLEXSPI_A_DATA1"), ("U8", "SO", "SO"), SRC["rt_ds"])
    b.pair("FLASH_WP", ("U8", "WP", "WP#"), ("R14", "2", "2"), SRC["rt_ds"], "control")

    # --- RT debug ---
    b.add("J4", "debug_connector", "RT_DEBUG", "connector", "FTSH-105-01-L-DV-K", "10PIN-1.27",
          SRC["debug"], "Cortex 10-pin 1.27 mm SWD header local to the RT1062")
    b.add("R15", "swdclk_series", "RT_DEBUG", "passive", "RC0402FR-0722RL", "22R",
          SRC["debug"], "Series resistor on SWCLK at the header")
    b.add("R16", "swdio_series", "RT_DEBUG", "passive", "RC0402FR-0722RL", "22R",
          SRC["debug"], "Series resistor on SWDIO at the header")
    b.add("J5", "rt_uart_header", "RT_DEBUG", "connector", "PREC004SAAN-RC", "1x4",
          SRC["debug"], "Direct BootROM UART header independent of ESP32_S3")
    b.add("R17", "uart_tx_series", "RT_DEBUG", "passive", "RC0402FR-0722RL", "22R",
          SRC["debug"], "Series resistor on LPUART1 TX")
    b.add("R18", "uart_rx_series", "RT_DEBUG", "passive", "RC0402FR-0722RL", "22R",
          SRC["debug"], "Series resistor on LPUART1 RX")

    b.pair("SWD_SWCLK", ("U6", "AD_B0_07", "JTAG_TCK_SWDCLK"), ("R15", "1", "1"), SRC["debug"])
    b.pair("SWD_SWCLK_H", ("R15", "2", "2"), ("J4", "4", "SWCLK"), SRC["debug"])
    b.pair("SWD_SWDIO", ("U6", "AD_B0_06", "JTAG_TMS_SWDIO"), ("R16", "1", "1"), SRC["debug"])
    b.pair("SWD_SWDIO_H", ("R16", "2", "2"), ("J4", "2", "SWDIO"), SRC["debug"])
    b.net("3V3", "power", "labelled_net", [("J4", "1", "VTref")], SRC["debug"])
    b.net("GND", "ground", "labelled_net", [("J4", "3", "GND"), ("J5", "4", "GND")], SRC["debug"])
    b.pair("LPUART1_TX", ("U6", "AD_B0_12", "GPIO_AD_B0_12"), ("R17", "1", "1"), SRC["debug"])
    b.pair("LPUART1_TX_H", ("R17", "2", "2"), ("J5", "1", "TX"), SRC["debug"])
    b.pair("LPUART1_RX", ("U6", "AD_B0_13", "GPIO_AD_B0_13"), ("R18", "1", "1"), SRC["debug"])
    b.pair("LPUART1_RX_H", ("R18", "2", "2"), ("J5", "2", "RX"), SRC["debug"])
    b.net("POR_B", "control", "labelled_net", [("J4", "10", "nRESET")], SRC["debug"])

    # --- ESP32-S3 ---
    b.add("U9", "esp32_s3", "ESP_CORE", "processor", "ESP32-S3-WROOM-1-N16R8", "FITTED",
          SRC["s3_hdg"], "Option-C radio module on the carrier with mandatory antenna clearance")
    b.add("C39", "s3_3v3_hf", "ESP_CORE", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["s3_hdg"], "Module 3V3 high-frequency decoupling")
    b.add("C40", "s3_3v3_bulk", "ESP_CORE", "passive", "GRM155R60J106ME44D", "10uF",
          SRC["s3_hdg"], "Module 3V3 bulk")
    b.add("C41", "s3_3v3_bulk2", "ESP_CORE", "passive", "GRM21BR61A476ME15L", "47uF",
          SRC["s3_hdg"], "Second module bulk per Espressif power guidance")
    b.add("R19", "s3_en_pu", "ESP_CORE", "passive", "RC0402FR-0710KL", "10k",
          SRC["s3_hdg"], "CHIP_PU/EN pull-up")
    b.add("C42", "s3_en_c", "ESP_CORE", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["s3_hdg"], "EN delay capacitor")
    b.add("R20", "s3_boot_pu", "ESP_CORE", "passive", "RC0402FR-0710KL", "10k",
          SRC["s3_hdg"], "GPIO0/BOOT pull-up")
    b.add("SW2", "s3_boot", "ESP_CORE", "option", "PTS645SM43SMTR92LFS", "BOOT",
          SRC["s3_hdg"], "Manual BOOT button on GPIO0")
    b.add("SW3", "s3_en", "ESP_CORE", "option", "PTS645SM43SMTR92LFS", "EN",
          SRC["s3_hdg"], "Manual EN button")
    b.add("J6", "s3_uart0", "ESP_CORE", "connector", "PREC004SAAN-RC", "1x4",
          SRC["s3_hdg"], "Retained UART0 download access beside the module")

    b.net("3V3", "power", "explicit_wire", [
        ("U9", "3V3", "3V3"), ("C39", "1", "1"), ("C40", "1", "1"), ("C41", "1", "1"),
        ("R19", "1", "1"), ("R20", "1", "1"), ("J6", "1", "3V3"),
    ], SRC["s3_hdg"], high_fanout=True)
    b.net("GND", "ground", "explicit_wire", [
        ("U9", "GND", "GND"), ("C39", "2", "2"), ("C40", "2", "2"), ("C41", "2", "2"),
        ("C42", "2", "2"), ("J6", "4", "GND"), ("SW2", "2", "2"), ("SW3", "2", "2"),
    ], SRC["s3_hdg"], high_fanout=True)
    b.net("ESP_EN", "control", "explicit_wire", [
        ("U9", "EN", "EN"), ("R19", "2", "2"), ("C42", "1", "1"), ("SW3", "1", "1"),
        ("J6", "3", "EN"),
    ], SRC["s3_hdg"])
    b.net("ESP_GPIO0", "control", "explicit_wire", [
        ("U9", "IO0", "IO0"), ("R20", "2", "2"), ("SW2", "1", "1"),
    ], SRC["s3_hdg"])
    b.pair("ESP_UART0_TX", ("U9", "TXD0", "TXD0"), ("J6", "2", "TX"), SRC["s3_hdg"])

    # --- Service USB ---
    b.add("J7", "service_usb_connector", "ESP_USB", "connector", "USB4105-GF-A", "USB-C-S3",
          SRC["usb"], "Service USB owned by ESP32_S3")
    b.add("U10", "usb_esd", "ESP_USB", "protection", "USBLC6-2SC6", "TVS",
          SRC["usb"], "USB ESD at the connector before the module PHY")
    b.add("C43", "usb_cc1", "ESP_USB", "passive", "GRM1555C1H101JA01D", "100pF",
          SRC["usb"], "CC1 noise capacitor")
    b.add("C44", "usb_cc2", "ESP_USB", "passive", "GRM1555C1H101JA01D", "100pF",
          SRC["usb"], "CC2 noise capacitor")
    b.add("R21", "usb_cc1_rd", "ESP_USB", "passive", "RC0402FR-075K1L", "5.1k",
          SRC["usb"], "CC1 Rd for UFP")
    b.add("R22", "usb_cc2_rd", "ESP_USB", "passive", "RC0402FR-075K1L", "5.1k",
          SRC["usb"], "CC2 Rd for UFP")
    b.add("FB4", "s3_usb_bead", "ESP_USB", "passive", "BLM21PG221SN1D", "220ohm@100MHz",
          SRC["usb"], "VBUS ferrite on the service USB 5 V arrival")

    b.pair("USB_DP", ("J7", "A6", "DP"), ("U10", "I_1", "I/O1"), SRC["usb"])
    b.pair("USB_DM", ("J7", "A7", "DM"), ("U10", "I_2", "I/O2"), SRC["usb"])
    b.pair("USB_DP_S3", ("U10", "O_1", "I/O1_DEV"), ("U9", "USB_D_P", "USB_D+"), SRC["usb"])
    b.pair("USB_DM_S3", ("U10", "O_2", "I/O2_DEV"), ("U9", "USB_D_N", "USB_D-"), SRC["usb"])
    b.pair("S3_VBUS", ("J7", "A4", "VBUS"), ("FB4", "1", "1"), SRC["usb"], "power")
    b.pair("S3_VBUS_F", ("FB4", "2", "2"), ("U9", "VBUS", "VBUS"), SRC["usb"], "power", "labelled_net")
    b.pair("USB_CC1", ("J7", "A5", "CC1"), ("R21", "1", "1"), SRC["usb"])
    b.pair("USB_CC2", ("J7", "B5", "CC2"), ("R22", "1", "1"), SRC["usb"])
    b.net("USB_CC1", "signal", "labelled_net", [("C43", "1", "1")], SRC["usb"])
    b.net("USB_CC2", "signal", "labelled_net", [("C44", "1", "1")], SRC["usb"])
    b.net("GND", "ground", "labelled_net", [
        ("J7", "A1", "GND"), ("U10", "GND", "GND"), ("R21", "2", "2"),
        ("R22", "2", "2"), ("C43", "2", "2"), ("C44", "2", "2"),
    ], SRC["usb"], high_fanout=True)

    # --- K1BR SPI ---
    b.add("R23", "k1br_sck", "K1BR", "passive", "RC0402FR-0722RL", "22R",
          SRC["k1br"], "SPI SCK series resistor on the bridge seam")
    b.add("R24", "k1br_mosi", "K1BR", "passive", "RC0402FR-0722RL", "22R",
          SRC["k1br"], "SPI MOSI series resistor, RT1062 master toward ESP32_S3")
    b.add("R25", "k1br_miso", "K1BR", "passive", "RC0402FR-0722RL", "22R",
          SRC["k1br"], "SPI MISO series resistor, ESP32_S3 slave toward RT1062")
    b.add("R26", "k1br_cs", "K1BR", "passive", "RC0402FR-0722RL", "22R",
          SRC["k1br"], "SPI CS series resistor")
    b.add("R27", "k1br_irq", "K1BR", "passive", "RC0402FR-0722RL", "22R",
          SRC["k1br"], "Optional slave-attention series resistor")
    b.add("C45", "k1br_decap", "K1BR", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["k1br"], "Local 3V3 decoupling at the bridge resistor cluster")
    b.add("TP1", "k1br_sck_tp", "K1BR", "testpoint", "5001", "TP",
          SRC["k1br"], "SCK test point on the bridge")
    b.add("TP2", "k1br_cs_tp", "K1BR", "testpoint", "5001", "TP",
          SRC["k1br"], "CS test point on the bridge")

    b.pair("K1BR_SCK_RT", ("U6", "SD_B0_00", "LPSPI1_SCK"), ("R23", "1", "1"), SRC["k1br"])
    b.pair("K1BR_SCK", ("R23", "2", "2"), ("U9", "IO12", "IO12"), SRC["k1br"])
    b.pair("K1BR_MOSI_RT", ("U6", "SD_B0_02", "LPSPI1_SDO"), ("R24", "1", "1"), SRC["k1br"])
    b.pair("K1BR_MOSI", ("R24", "2", "2"), ("U9", "IO11", "IO11"), SRC["k1br"])
    b.pair("K1BR_MISO_S3", ("U9", "IO13", "IO13"), ("R25", "1", "1"), SRC["k1br"])
    b.pair("K1BR_MISO", ("R25", "2", "2"), ("U6", "SD_B0_03", "LPSPI1_SDI"), SRC["k1br"])
    b.pair("K1BR_CS_RT", ("U6", "SD_B0_01", "LPSPI1_PCS0"), ("R26", "1", "1"), SRC["k1br"])
    b.pair("K1BR_CS", ("R26", "2", "2"), ("U9", "IO10", "IO10"), SRC["k1br"])
    b.pair("K1BR_IRQ_S3", ("U9", "IO14", "IO14"), ("R27", "1", "1"), SRC["k1br"], "control")
    b.pair("K1BR_IRQ", ("R27", "2", "2"), ("U6", "AD_B1_01", "GPIO_AD_B1_01"), SRC["k1br"], "control")
    b.net("K1BR_SCK", "signal", "labelled_net", [("TP1", "1", "1")], SRC["k1br"])
    b.net("K1BR_CS", "signal", "labelled_net", [("TP2", "1", "1")], SRC["k1br"])
    b.net("3V3", "power", "labelled_net", [("C45", "1", "1")], SRC["k1br"])
    b.net("GND", "ground", "labelled_net", [("C45", "2", "2"), ("TP1", "2", "2"), ("TP2", "2", "2")], SRC["k1br"])

    # --- Audio ADC ---
    b.add("U11", "audio_frontend", "AUDIO_ADC", "major_ic", "TLV320ADC6120IRTER", "FITTED",
          SRC["tlv"], "Evaluation ADC on the RT1062 SAI/TDM path")
    b.add("C46", "adc_avdd", "AUDIO_ADC", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["tlv"], "AVDD decoupling at the ADC")
    b.add("C47", "adc_iovdd", "AUDIO_ADC", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["tlv"], "IOVDD decoupling at the ADC")
    b.add("C48", "adc_areg", "AUDIO_ADC", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["tlv"], "AREG decoupling")
    b.add("C49", "adc_dreg", "AUDIO_ADC", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["tlv"], "DREG decoupling")
    b.add("C50", "adc_avdd_bulk", "AUDIO_ADC", "passive", "GRM155R60J106ME44D", "10uF",
          SRC["tlv"], "AVDD bulk")
    b.add("R28", "adc_sda_pu", "AUDIO_ADC", "passive", "RC0402FR-074K7L", "4.7k",
          SRC["tlv"], "I2C SDA pull-up at the ADC")
    b.add("R29", "adc_scl_pu", "AUDIO_ADC", "passive", "RC0402FR-074K7L", "4.7k",
          SRC["tlv"], "I2C SCL pull-up at the ADC")
    b.add("C51", "adc_vref", "AUDIO_ADC", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["tlv"], "VREF decoupling at the ADC")

    b.net("3V3", "power", "explicit_wire", [
        ("U11", "AVDD", "AVDD"), ("U11", "IOVDD", "IOVDD"),
        ("C46", "1", "1"), ("C47", "1", "1"), ("C50", "1", "1"),
        ("R28", "1", "1"), ("R29", "1", "1"),
    ], SRC["tlv"], high_fanout=True)
    b.net("GND", "ground", "explicit_wire", [
        ("U11", "GND", "GND"), ("C46", "2", "2"), ("C47", "2", "2"),
        ("C48", "2", "2"), ("C49", "2", "2"), ("C50", "2", "2"), ("C51", "2", "2"),
    ], SRC["tlv"], high_fanout=True)
    b.pair("ADC_AREG", ("U11", "AREG", "AREG"), ("C48", "1", "1"), SRC["tlv"], "power")
    b.pair("ADC_DREG", ("U11", "DREG", "DREG"), ("C49", "1", "1"), SRC["tlv"], "power")
    b.net("I2C_SDA", "bus", "explicit_wire", [
        ("U11", "SDA", "SDA"), ("R28", "2", "2"), ("U2", "SDA", "SDA"), ("R4", "1", "1"),
    ], SRC["audio"], high_fanout=True)
    b.net("I2C_SCL", "bus", "explicit_wire", [
        ("U11", "SCL", "SCL"), ("R29", "2", "2"), ("U2", "SCL", "SCL"),
    ], SRC["audio"], high_fanout=True)
    b.pair("ADC_VREF", ("U11", "VREF", "VREF"), ("C51", "1", "1"), SRC["tlv"], "power")
    b.pair("INA_ALERT", ("U2", "ALERT", "ALERT"), ("R3", "2", "2"), SRC["ina"], "control")
    b.net("3V3", "power", "labelled_net", [("R3", "1", "1"), ("R4", "2", "2")], SRC["ina"])

    # --- Audio clocks / isolation ---
    b.add("R31", "mclk_series", "AUDIO_CLOCK", "passive", "RC0402FR-0722RL", "22R",
          SRC["audio"], "Series option on AUDIO_MCLK from RT1062")
    b.add("R32", "bclk_series", "AUDIO_CLOCK", "passive", "RC0402FR-0722RL", "22R",
          SRC["audio"], "Series option on AUDIO_BCLK")
    b.add("R33", "fsync_series", "AUDIO_CLOCK", "passive", "RC0402FR-0722RL", "22R",
          SRC["audio"], "Series option on AUDIO_FSYNC")
    b.add("R34", "mclk_iso", "AUDIO_CLOCK", "option", "RC0402FR-070RL", "0R",
          SRC["audio"], "0R that can open to isolate RT1062 MCLK for laboratory drive")
    b.add("R35", "bclk_iso", "AUDIO_CLOCK", "option", "RC0402FR-070RL", "0R",
          SRC["audio"], "0R isolator on BCLK")
    b.add("R36", "fsync_iso", "AUDIO_CLOCK", "option", "RC0402FR-070RL", "0R",
          SRC["audio"], "0R isolator on FSYNC")
    b.add("J8", "ext_audio_clk", "AUDIO_CLOCK", "connector", "PREC004SAAN-RC", "1x4",
          SRC["audio"], "Laboratory clock injection header")
    b.add("R37", "dout_series", "AUDIO_CLOCK", "passive", "RC0402FR-0722RL", "22R",
          SRC["audio"], "TDM/I2S DOUT series toward RT1062 SAI")
    b.add("TP3", "mclk_tp", "AUDIO_CLOCK", "testpoint", "5001", "TP",
          SRC["audio"], "MCLK test access")
    b.add("C52", "clk_term", "AUDIO_CLOCK", "passive", "GRM1555C1H101JA01D", "100pF",
          SRC["audio"], "Optional MCLK snubber at the header")

    b.pair("AUDIO_MCLK_RT", ("U6", "AD_B1_15", "SAI1_MCLK"), ("R31", "1", "1"), SRC["clock"], "clock")
    b.pair("AUDIO_MCLK_ISO", ("R31", "2", "2"), ("R34", "1", "1"), SRC["audio"], "clock")
    b.net("AUDIO_MCLK", "clock", "explicit_wire", [
        ("R34", "2", "2"), ("U11", "MICBIAS_GPI2", "MCLK"), ("J8", "1", "MCLK"), ("TP3", "1", "1"),
    ], SRC["audio"])
    b.pair("AUDIO_BCLK_RT", ("U6", "AD_B1_14", "SAI1_RX_BCLK"), ("R32", "1", "1"), SRC["clock"], "clock")
    b.pair("AUDIO_BCLK_ISO", ("R32", "2", "2"), ("R35", "1", "1"), SRC["audio"], "clock")
    b.net("AUDIO_BCLK", "clock", "explicit_wire", [
        ("R35", "2", "2"), ("U11", "BCLK", "BCLK"), ("J8", "2", "BCLK"),
    ], SRC["audio"])
    b.pair("AUDIO_FSYNC_RT", ("U6", "AD_B1_13", "SAI1_RX_SYNC"), ("R33", "1", "1"), SRC["clock"], "clock")
    b.pair("AUDIO_FSYNC_ISO", ("R33", "2", "2"), ("R36", "1", "1"), SRC["audio"], "clock")
    b.net("AUDIO_FSYNC", "clock", "explicit_wire", [
        ("R36", "2", "2"), ("U11", "FSYNC", "FSYNC"), ("J8", "3", "FSYNC"),
    ], SRC["audio"])
    b.pair("AUDIO_DOUT_ADC", ("U11", "SDOUT", "DOUT"), ("R37", "1", "1"), SRC["audio"])
    b.pair("AUDIO_DOUT", ("R37", "2", "2"), ("U6", "AD_B1_12", "SAI1_RX_DATA00"), SRC["audio"])
    b.net("AUDIO_MCLK", "clock", "labelled_net", [("C52", "1", "1")], SRC["audio"])
    b.net("GND", "ground", "labelled_net", [
        ("J8", "4", "GND"), ("C52", "2", "2"),
    ], SRC["audio"])

    # --- Microphone XOR ---
    b.add("J9", "mic_flex", "AUDIO_MIC", "connector", "FH12-10S-0.5SH", "FFC-10",
          SRC["mic"], "IM69D130 flex connector")
    b.add("R38", "pdm_adc_clk", "AUDIO_MIC", "option", "RC0402FR-070RL", "0R",
          SRC["mic"], "0R enabling PDM clock into the TLV320 path")
    b.add("R39", "pdm_adc_dat", "AUDIO_MIC", "option", "RC0402FR-070RL", "0R",
          SRC["mic"], "0R enabling PDM data into the TLV320 path")
    b.add("R40", "pdm_rt_clk", "AUDIO_MIC", "option", "RC0402FR-07DNP", "DNP",
          SRC["mic"], "DNP 0R for the direct-RT SAI PDM clock path")
    b.add("R41", "pdm_rt_dat", "AUDIO_MIC", "option", "RC0402FR-07DNP", "DNP",
          SRC["mic"], "DNP 0R for the direct-RT SAI PDM data path")
    b.add("C53", "mic_flex_vdd", "AUDIO_MIC", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["mic"], "Local 3V3_MIC at the flex")
    b.add("FB5", "mic_flex_bead", "AUDIO_MIC", "passive", "BLM15AG221SN1D", "220ohm@100MHz",
          SRC["mic"], "Bead on 3V3_MIC at the flex")
    b.add("TP4", "pdm_clk_tp", "AUDIO_MIC", "testpoint", "5001", "TP",
          SRC["mic"], "PDM clock test point")
    b.add("TP5", "pdm_dat_tp", "AUDIO_MIC", "testpoint", "5001", "TP",
          SRC["mic"], "PDM data test point")

    b.net("3V3_MIC", "power", "explicit_wire", [
        ("FB5", "1", "1"),
    ], SRC["mic"], high_fanout=True)
    b.pair("3V3_MIC_FLEX", ("FB5", "2", "2"), ("J9", "1", "VDD"), SRC["mic"], "power")
    b.net("3V3_MIC_FLEX", "power", "labelled_net", [("C53", "1", "1")], SRC["mic"])
    b.net("GND", "ground", "labelled_net", [
        ("J9", "2", "GND"), ("C53", "2", "2"),
    ], SRC["mic"])
    b.net("PDM_CLK", "clock", "explicit_wire", [
        ("J9", "3", "CLK"), ("R38", "1", "1"), ("R40", "1", "1"), ("TP4", "1", "1"),
    ], SRC["mic"])
    b.net("PDM_DAT", "signal", "explicit_wire", [
        ("J9", "4", "DATA"), ("R39", "1", "1"), ("R41", "1", "1"), ("TP5", "1", "1"),
    ], SRC["mic"])
    b.pair("PDM_CLK_ADC", ("R38", "2", "2"), ("U11", "GPIO1", "PDMCLK"), SRC["audio"], "clock")
    b.pair("PDM_DAT_ADC", ("R39", "2", "2"), ("U11", "IN2P_GPI1", "PDMDIN1"), SRC["audio"])
    b.pair("PDM_CLK_RT", ("R40", "2", "2"), ("U6", "AD_B1_11", "SAI2_RX_BCLK"), SRC["mic"], "clock")
    b.pair("PDM_DAT_RT", ("R41", "2", "2"), ("U6", "AD_B1_10", "SAI2_RX_DATA"), SRC["mic"])

    # --- NFC ---
    b.add("U12", "nfc_frontend", "NFC", "major_ic", "ST25R3916B-AQWT", "FITTED",
          SRC["nfc"], "Carrier-side NFC front end; RF never crosses a module connector")
    b.add("Y2", "nfc_xtal", "NFC", "clock", "ABM12-117-27.120MHZ-T3", "27.12MHz",
          SRC["nfc"], "27.12 MHz crystal beside ST25R3916B")
    b.add("C54", "nfc_xtal_c1", "NFC", "passive", "GRM1555C1H100JA01D", "10pF",
          SRC["st_an"], "Crystal load on XTI")
    b.add("C55", "nfc_xtal_c2", "NFC", "passive", "GRM1555C1H100JA01D", "10pF",
          SRC["st_an"], "Crystal load on XTO")
    b.add("C56", "nfc_vdd", "NFC", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["nfc"], "VDD decoupling")
    b.add("C57", "nfc_vsp_a", "NFC", "passive", "GRM155R60J106ME44D", "10uF",
          SRC["nfc"], "Transmitter supply bulk")
    b.add("C58", "nfc_vsp_hf", "NFC", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["nfc"], "Transmitter supply HF ceramic")
    b.add("L2", "nfc_emi_l", "NFC", "passive", "LQW15AN5N6C10D", "5.6nH",
          SRC["st_an"], "RFO EMI inductor")
    b.add("C59", "nfc_emi_c", "NFC", "passive", "GRM1555C1H220JA01D", "22pF",
          SRC["st_an"], "RFO EMI capacitor")
    b.add("C60", "nfc_match_cs", "NFC", "passive", "GRM1555C1H330JA01D", "33pF",
          SRC["st_an"], "Matching Cs; value remains TUNE_TBD")
    b.add("C61", "nfc_match_cp", "NFC", "passive", "GRM1555C1H470JA01D", "47pF",
          SRC["st_an"], "Matching Cp; value remains TUNE_TBD")
    b.add("L3", "nfc_match_l", "NFC", "passive", "LQW15AN33NG00D", "33nH",
          SRC["st_an"], "Matching inductor; value remains TUNE_TBD")
    b.add("R42", "nfc_damp", "NFC", "passive", "RC0402FR-072R2L", "2.2R",
          SRC["st_an"], "RFO damping")
    b.add("J10", "nfc_antenna", "NFC", "connector", "U.FL-R-SMT-1", "U.FL",
          SRC["nfc"], "Antenna terminals on the carrier")
    b.add("R43", "nfc_irq_pu", "NFC", "passive", "RC0402FR-074K7L", "4.7k",
          SRC["nfc"], "NFC_IRQ pull-up to 3V3")

    b.net("NFC_5V", "power", "explicit_wire", [
        ("U12", "VSP_A", "VSP_A"), ("C57", "1", "1"), ("C58", "1", "1"),
    ], SRC["nfc"], high_fanout=True)
    b.net("3V3", "power", "explicit_wire", [
        ("U12", "VDD", "VDD"), ("C56", "1", "1"), ("R43", "1", "1"),
    ], SRC["nfc"], high_fanout=True)
    b.net("GND", "ground", "explicit_wire", [
        ("U12", "GND", "GND"), ("C54", "2", "2"), ("C55", "2", "2"),
        ("C56", "2", "2"), ("C57", "2", "2"), ("C58", "2", "2"), ("C59", "2", "2"),
        ("C61", "2", "2"),
    ], SRC["nfc"], high_fanout=True)
    b.pair("NFC_XTI", ("U12", "XTI", "XTI"), ("Y2", "1", "1"), SRC["nfc"], "clock")
    b.pair("NFC_XTO", ("U12", "XTO", "XTO"), ("Y2", "2", "2"), SRC["nfc"], "clock")
    b.net("NFC_XTI", "clock", "labelled_net", [("C54", "1", "1")], SRC["st_an"])
    b.net("NFC_XTO", "clock", "labelled_net", [("C55", "1", "1")], SRC["st_an"])
    b.net("I2C_SDA", "bus", "labelled_net", [("U12", "SDA", "SDA"), ("U9", "IO1", "IO1")], SRC["nfc"], high_fanout=True)
    b.net("I2C_SCL", "bus", "labelled_net", [("U12", "SCL", "SCL"), ("U9", "IO2", "IO2")], SRC["nfc"], high_fanout=True)
    b.net("NFC_IRQ", "control", "explicit_wire", [
        ("U12", "IRQ", "IRQ"), ("R43", "2", "2"), ("U9", "IO4", "IO4"),
    ], SRC["nfc"])
    b.pair("NFC_RFO1", ("U12", "RFO1", "RFO1"), ("L2", "1", "1"), SRC["st_an"])
    b.pair("NFC_EMI", ("L2", "2", "2"), ("R42", "1", "1"), SRC["st_an"])
    b.net("NFC_EMI", "signal", "labelled_net", [("C59", "1", "1")], SRC["st_an"])
    b.pair("NFC_MATCH_IN", ("R42", "2", "2"), ("C60", "1", "1"), SRC["st_an"])
    b.pair("NFC_MATCH_L", ("C60", "2", "2"), ("L3", "1", "1"), SRC["st_an"])
    b.pair("NFC_ANT", ("L3", "2", "2"), ("J10", "1", "ANT"), SRC["nfc"])
    b.net("NFC_ANT", "signal", "labelled_net", [
        ("C61", "1", "1"), ("U12", "RFI1", "RFI1"),
    ], SRC["st_an"])
    b.net("GND", "ground", "labelled_net", [("J10", "2", "GND")], SRC["nfc"])

    # --- Motion ---
    b.add("U13", "accelerometer", "MOTION", "major_ic", "LIS2DH12TR", "FITTED",
          SRC["lis2"], "Working accelerometer candidate; contract freezes the XOR matrix, not the MPN")
    b.add("C62", "acc_vdd", "MOTION", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["lis2"], "Accelerometer VDD decoupling")
    b.add("C63", "acc_vddio", "MOTION", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["lis2"], "Accelerometer VDD_IO decoupling")
    b.add("R44", "acc_sda_rt", "MOTION", "option", "RC0402FR-070RL", "0R",
          SRC["motion"], "0R assigning SDA to RT1062")
    b.add("R45", "acc_sda_s3", "MOTION", "option", "RC0402FR-07DNP", "DNP",
          SRC["motion"], "DNP 0R that would assign SDA to ESP32_S3")
    b.add("R46", "acc_scl_rt", "MOTION", "option", "RC0402FR-070RL", "0R",
          SRC["motion"], "0R assigning SCL to RT1062")
    b.add("R47", "acc_scl_s3", "MOTION", "option", "RC0402FR-07DNP", "DNP",
          SRC["motion"], "DNP 0R that would assign SCL to ESP32_S3")
    b.add("R48", "acc_irq_rt", "MOTION", "option", "RC0402FR-070RL", "0R",
          SRC["motion"], "0R assigning INT1 to RT1062")
    b.add("R49", "acc_irq_s3", "MOTION", "option", "RC0402FR-07DNP", "DNP",
          SRC["motion"], "DNP 0R that would assign INT1 to ESP32_S3")
    b.add("R50", "acc_sda_pu", "MOTION", "passive", "RC0402FR-074K7L", "4.7k",
          SRC["motion"], "Local I2C pull-up at the accelerometer")

    b.net("3V3", "power", "explicit_wire", [
        ("U13", "VDD", "VDD"), ("U13", "VDD_IO", "VDD_IO"),
        ("C62", "1", "1"), ("C63", "1", "1"), ("R50", "1", "1"),
    ], SRC["motion"], high_fanout=True)
    b.net("GND", "ground", "explicit_wire", [
        ("U13", "GND", "GND"), ("C62", "2", "2"), ("C63", "2", "2"),
    ], SRC["motion"], high_fanout=True)
    b.net("MOTION_SDA", "bus", "explicit_wire", [
        ("U13", "SDA", "SDA"), ("R44", "1", "1"), ("R45", "1", "1"), ("R50", "2", "2"),
    ], SRC["motion"])
    b.net("MOTION_SCL", "bus", "explicit_wire", [
        ("U13", "SCL", "SCL"), ("R46", "1", "1"), ("R47", "1", "1"),
    ], SRC["motion"])
    b.net("MOTION_INT1", "control", "explicit_wire", [
        ("U13", "INT1", "INT1"), ("R48", "1", "1"), ("R49", "1", "1"),
    ], SRC["motion"])
    b.net("I2C_SDA", "bus", "labelled_net", [("R44", "2", "2")], SRC["motion"], high_fanout=True)
    b.net("I2C_SCL", "bus", "labelled_net", [("R46", "2", "2")], SRC["motion"], high_fanout=True)
    b.net("I2C_SDA", "bus", "labelled_net", [("R45", "2", "2")], SRC["motion"])
    b.net("I2C_SCL", "bus", "labelled_net", [("R47", "2", "2")], SRC["motion"])
    b.pair("MOTION_INT_RT", ("R48", "2", "2"), ("U6", "AD_B1_02", "GPIO_AD_B1_02"), SRC["motion"], "control")
    b.pair("MOTION_INT_S3", ("R49", "2", "2"), ("U9", "IO5", "IO5"), SRC["motion"], "control", "labelled_net")

    # --- LED data ---
    b.add("U14", "led_shift_l", "LED_DATA", "support_ic", "SN74AHCT1G125DBVR", "FITTED",
          SRC["led"], "3.3 V to 5 V shifter on left strip data",
          shared_device_justification="two identical single-gate 5 V buffers, one per LED channel")
    b.add("U15", "led_shift_r", "LED_DATA", "support_ic", "SN74AHCT1G125DBVR", "FITTED",
          SRC["led"], "3.3 V to 5 V shifter on right strip data",
          shared_device_justification="two identical single-gate 5 V buffers, one per LED channel")
    b.add("J2", "led_connector", "LED_DATA", "connector", "B3B-XH-A-3PZZ", "XH-3",
          SRC["led"], "Left LED connector J2 owned by RT1062")
    b.add("J3", "led_connector_r", "LED_DATA", "connector", "B3B-XH-A-3PZZ", "XH-3",
          SRC["led"], "Right LED connector J3 owned by RT1062")
    b.add("R51", "led_l_series", "LED_DATA", "passive", "RC0402FR-0733RL", "33R",
          SRC["led"], "Series resistor on left 5 V data")
    b.add("R52", "led_r_series", "LED_DATA", "passive", "RC0402FR-0733RL", "33R",
          SRC["led"], "Series resistor on right 5 V data")
    b.add("C64", "shift_l_vcc", "LED_DATA", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["led"], "Left shifter VCC decoupling on +5V_LED_L")
    b.add("C65", "shift_r_vcc", "LED_DATA", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["led"], "Right shifter VCC decoupling on +5V_LED_R")
    b.add("R53", "shift_l_oe", "LED_DATA", "passive", "RC0402FR-0710KL", "10k",
          SRC["led"], "Left shifter OE pull-down so the buffer is on")
    b.add("R54", "shift_r_oe", "LED_DATA", "passive", "RC0402FR-0710KL", "10k",
          SRC["led"], "Right shifter OE pull-down")

    b.pair("LED_D0_3V3", ("U6", "B0_00", "GPIO_B0_00"), ("U14", "A", "A"), SRC["led"])
    b.pair("LED_D1_3V3", ("U6", "B0_01", "GPIO_B0_01"), ("U15", "A", "A"), SRC["led"])
    b.pair("LED_D0_5V", ("U14", "Y", "Y"), ("R51", "1", "1"), SRC["led"])
    b.pair("LED_D1_5V", ("U15", "Y", "Y"), ("R52", "1", "1"), SRC["led"])
    b.pair("LED_D0_J", ("R51", "2", "2"), ("J2", "2", "DIN"), SRC["led"])
    b.pair("LED_D1_J", ("R52", "2", "2"), ("J3", "2", "DIN"), SRC["led"])
    b.net("+5V_LED_L", "power", "explicit_wire", [
        ("U14", "VCC", "VCC"), ("C64", "1", "1"), ("J2", "1", "5V"),
    ], SRC["led"], high_fanout=True)
    b.net("+5V_LED_R", "power", "explicit_wire", [
        ("U15", "VCC", "VCC"), ("C65", "1", "1"), ("J3", "1", "5V"),
    ], SRC["led"], high_fanout=True)
    b.net("GND", "ground", "explicit_wire", [
        ("U14", "GND", "GND"), ("U15", "GND", "GND"), ("C64", "2", "2"),
        ("C65", "2", "2"), ("J2", "3", "GND"), ("J3", "3", "GND"),
        ("R53", "2", "2"), ("R54", "2", "2"),
    ], SRC["led"], high_fanout=True)
    b.pair("LED_OE_L", ("U14", "OE", "OE#"), ("R53", "1", "1"), SRC["led"], "control")
    b.pair("LED_OE_R", ("U15", "OE", "OE#"), ("R54", "1", "1"), SRC["led"], "control")
    b.add("RT1", "led_therm_l", "LED_DATA", "passive", "NCP15XH103F03RC", "10k-NTC",
          SRC["led"], "Left LED thermal sense required by domain D06")
    b.add("RT2", "led_therm_r", "LED_DATA", "passive", "NCP15XH103F03RC", "10k-NTC",
          SRC["led"], "Right LED thermal sense required by domain D06")
    b.pair("LED_THERM_L", ("RT1", "1", "1"), ("U6", "AD_B1_04", "GPIO_AD_B1_04"), SRC["led"])
    b.pair("LED_THERM_R", ("RT2", "1", "1"), ("U6", "AD_B1_05", "GPIO_AD_B1_05"), SRC["led"])
    b.net("GND", "ground", "labelled_net", [("RT1", "2", "2"), ("RT2", "2", "2")], SRC["led"])

    # --- Options ---
    b.add("R55", "option_link", "OPTIONS", "option", "RC0402FR-070RL", "0R",
          SRC["debug"], "Fitted option link on a named validation strap")
    b.add("R56", "option_usb_audio", "OPTIONS", "option", "RC0402FR-07DNP", "DNP",
          SRC["usb"], "DNP link reserved for the USB-audio experiment")
    b.add("R57", "option_ext_mclk", "OPTIONS", "option", "RC0402FR-07DNP", "DNP",
          SRC["audio"], "DNP link that would hard-wire laboratory MCLK")
    b.add("R58", "option_s3_log", "OPTIONS", "option", "RC0402FR-070RL", "0R",
          SRC["debug"], "Fitted link enabling VAL debug-fabric UART observe")
    b.add("J11", "option_header", "OPTIONS", "connector", "PREC006SAAN-RC", "1x6",
          SRC["debug"], "Named option and strap header")
    b.add("TP6", "opt_tp", "OPTIONS", "testpoint", "5001", "TP",
          SRC["debug"], "Option-rail test point")

    b.pair("OPT_BOOT_REC", ("R55", "1", "1"), ("J11", "1", "REC"), SRC["debug"], "control")
    b.pair("OPT_BOOT_REC_RT", ("R55", "2", "2"), ("U6", "AD_B1_03", "GPIO_AD_B1_03"), SRC["debug"], "control")
    b.pair("OPT_USB_AUD", ("R56", "1", "1"), ("J11", "2", "USBAUD"), SRC["usb"], "signal")
    b.pair("OPT_USB_AUD_RT", ("R56", "2", "2"), ("U6", "USB_OTG1_DN", "USB_OTG1_DN"), SRC["usb"], "signal", "labelled_net")
    b.pair("OPT_MCLK", ("R57", "1", "1"), ("J11", "3", "MCLK"), SRC["audio"], "clock")
    b.net("AUDIO_MCLK", "clock", "labelled_net", [("R57", "2", "2")], SRC["audio"])
    b.pair("OPT_S3_LOG", ("R58", "1", "1"), ("J11", "4", "S3LOG"), SRC["debug"], "signal")
    b.net("ESP_UART0_TX", "signal", "labelled_net", [("R58", "2", "2")], SRC["debug"])
    b.net("3V3", "power", "labelled_net", [("J11", "5", "3V3"), ("TP6", "1", "1")], SRC["debug"])
    b.net("GND", "ground", "labelled_net", [("J11", "6", "GND")], SRC["debug"])

    # --- Debug fabric extras ---
    b.add("R59", "s3_por_series", "DEBUG_FABRIC", "passive", "RC0402FR-07100RL", "100R",
          SRC["debug"], "ESP32_S3 may pull POR_B low through this series resistor")
    b.add("Q2", "s3_por_od", "DEBUG_FABRIC", "support_ic", "2N7002", "N-FET",
          SRC["debug"], "Open-drain POR_B request so ESP32_S3 never drives POR_B high")
    b.add("R60", "s3_por_gate", "DEBUG_FABRIC", "passive", "RC0402FR-07100RL", "100R",
          SRC["debug"], "Gate resistor on the POR_B request FET")
    b.add("SW4", "serial_dl", "DEBUG_FABRIC", "option", "PTS645SM43SMTR92LFS", "SDL",
          SRC["debug"], "ESP32_S3-independent Serial Downloader path")
    b.add("R61", "sdl_mode0", "DEBUG_FABRIC", "passive", "RC0402FR-0710KL", "10k",
          SRC["debug"], "Manual Serial Downloader forces BOOT_MODE0")
    b.add("R62", "pwr_valid_pu", "DEBUG_FABRIC", "passive", "RC0402FR-0710KL", "10k",
          SRC["debug"], "RT power-valid pull-up toward ESP32_S3")
    b.add("U16", "pwr_valid", "DEBUG_FABRIC", "support_ic", "TPS3808G33DBVR", "PGOOD",
          SRC["debug"], "Power-valid supervisor sourced from the 3V3 rail, not inferred")
    b.add("C66", "pwr_valid_c", "DEBUG_FABRIC", "passive", "GRM155R71C104KA88D", "100nF",
          SRC["debug"], "Power-valid supervisor decoupling")

    b.pair("S3_POR_REQ", ("U9", "IO6", "IO6"), ("R60", "1", "1"), SRC["debug"], "control")
    b.pair("S3_POR_GATE", ("R60", "2", "2"), ("Q2", "G", "G"), SRC["debug"], "control")
    b.pair("S3_POR_OD", ("Q2", "D", "D"), ("R59", "1", "1"), SRC["debug"], "control")
    b.net("POR_B", "control", "labelled_net", [("R59", "2", "2")], SRC["debug"], high_fanout=True)
    b.net("GND", "ground", "labelled_net", [
        ("Q2", "S", "S"), ("SW4", "2", "2"), ("C66", "2", "2"), ("U16", "GND", "GND"),
    ], SRC["debug"], high_fanout=True)
    b.pair("SDL_SW", ("SW4", "1", "1"), ("R61", "1", "1"), SRC["debug"], "control")
    b.net("BOOT_MODE0", "control", "labelled_net", [("R61", "2", "2")], SRC["debug"])
    b.net("3V3", "power", "labelled_net", [
        ("U16", "VDD", "VDD"), ("C66", "1", "1"), ("R62", "1", "1"),
    ], SRC["debug"], high_fanout=True)
    b.net("RT_PWR_VALID", "control", "explicit_wire", [
        ("U16", "RESET", "RESET"), ("R62", "2", "2"), ("U9", "IO7", "IO7"),
    ], SRC["debug"])

    add_stress(b)


def add_stress(b: Builder) -> None:
    """Extra rail loading only. Never a second processor, frontend or regulator."""
    baseline = sum(1 for component in b.components if not component["fixture_only"])
    needed = max(200, math.ceil(1.20 * baseline))
    extra = needed - len(b.components)
    rails = [
        ("3V3", "POWER_BUCK", "L1", "2", "2"),
        ("5V_SYS", "POWER_SENSE", "U2", "VBUS", "VBUS"),
        ("3V3_MIC", "POWER_BRANCH", "Q1", "D", "D"),
        ("NFC_5V", "NFC", "U12", "VSP_A", "VSP_A"),
        ("+5V_LED_L", "LED_DATA", "U14", "VCC", "VCC"),
        ("+5V_LED_R", "POWER_LED", "FB2", "2", "2"),
        ("3V3", "RT_DECOUPLE", "U6", "NVCC_GPIO", "NVCC_GPIO"),
        ("3V3", "ESP_CORE", "U9", "3V3", "3V3"),
        ("3V3", "AUDIO_ADC", "U11", "IOVDD", "IOVDD"),
        ("3V3", "MOTION", "U13", "VDD", "VDD"),
        ("5V_PROTECTED", "POWER_ENTRY", "U1", "OUT", "OUT"),
    ]
    for index in range(extra):
        rail, block, src_ref, pin, pin_name = rails[index % len(rails)]
        ref = "CS%02d" % (index + 1)
        b.add(
            ref, "stress_rail_load", block, "passive",
            "GRM155R71C104KA88D", "100nF", SRC["stress"],
            "Extra 100 nF on %s at the %s circuit to hold edit load" % (rail, block),
            fixture_only=True,
            stress_basis="twenty-percent qualification stress as extra capacitive load on a real rail",
        )
        b.net(rail, "power", "labelled_net", [(ref, "1", "1"), (src_ref, pin, pin_name)], SRC["stress"])
        b.net("GND", "ground", "labelled_net", [(ref, "2", "2")], SRC["stress"], high_fanout=True)


def finish_pins(b: Builder) -> None:
    """Every two-terminal part must use both pins; leftovers get a named local return."""
    used = defaultdict(set)
    for net in b.nets.values():
        for endpoint in net["endpoints"]:
            used[endpoint["ref"]].add(endpoint["pin"])
    by_ref = {component["ref"]: component for component in b.components}
    for ref, component in by_ref.items():
        if component["class"] not in {"passive", "protection", "option", "testpoint"}:
            continue
        pins = used[ref]
        if "1" in pins and "2" not in pins:
            b.net("GND", "ground", "labelled_net", [(ref, "2", "2")], SRC["power"], high_fanout=True)
        elif "2" in pins and "1" not in pins:
            b.net("3V3", "power", "labelled_net", [(ref, "1", "1")], SRC["power"])


def emit(b: Builder) -> dict:
    finish_pins(b)
    components = b.components
    nets = list(b.nets.values())
    baseline = sum(1 for component in components if not component["fixture_only"])
    blocks = []
    for block_id, refs in b.block_refs.items():
        domain = DOMAIN_OF_BLOCK[block_id]
        ref_set = set(refs)
        net_names = [
            net["name"] for net in nets
            if any(endpoint["ref"] in ref_set for endpoint in net["endpoints"])
        ]
        xs = [component["placement"]["x"] for component in components if component["ref"] in ref_set]
        ys = [component["placement"]["y"] for component in components if component["ref"] in ref_set]
        blocks.append({
            "id": block_id,
            "domain": domain,
            "component_refs": sorted(refs),
            "net_names": net_names,
            "placement_intent": PLACEMENT_INTENT[block_id],
            "source_ref": {k: v for k, v in SRC["power"].items() if k != "requirement_type"}
            if domain == "POWER" else {
                "document": "architecture and contracts for %s" % domain,
                "revision": "2026-08-28",
                "locator": block_id,
                "url_or_path": "architecture/DOMAINS-OF-CONCERN.md",
            },
            "bounds": {
                "x1": min(xs) - 40,
                "y1": min(ys) - 40,
                "x2": max(xs) + 80,
                "y2": max(ys) + 80,
            },
        })

    visual_transactions = []
    for number, block in enumerate(blocks, start=1):
        if len(block["component_refs"]) > 40:
            raise SystemExit("block %s exceeds 40 components" % block["id"])
        visual_transactions.append({
            "id": "VISUAL_TRANSACTION_%02d" % number,
            "block_ids": [block["id"]],
            "component_refs": block["component_refs"],
            "stop_for_screenshot_inspection": True,
            "intended_delta": "Place and wire the complete %s circuit" % block["id"],
            "screenshot_path": "evidence/VAL-G2-2026-08-28/transactions/%s.png" % block["id"].lower(),
            "readback_path": "evidence/VAL-G2-2026-08-28/transactions/%s.json" % block["id"].lower(),
            "inspection_criteria": [
                "the block reads as a circuit, not a repeated symbol bank",
                "all parts of this block stay inside the declared bounds",
                "power arrives from the source side and loads leave toward their destination",
                "wires land only on the planned pins for this block",
            ],
        })

    return {
        "schema_version": 1,
        # D-042 permanently retired live qualification-project execution.  Regeneration
        # must never recreate a write-authorising plan state.
        "plan_state": "RETIRED_BY_D_042",
        "project_name": "K1-CORE-VAL-SINGLE-SHEET-QUAL",
        "population_method": "CIRCUIT_BLOCKS_FROM_PRIMARY_SOURCES",
        "generic_device_fallback": False,
        "uniform_grid_placement": False,
        "option_c_estimated_symbols": baseline,
        "planned_symbols": len(components),
        "estimate_sources": [
            "architecture/POWER-ARCHITECTURE.md",
            "architecture/CLOCK-ARCHITECTURE.md",
            "contracts/audio-interface.md",
            "contracts/microphone-interface.md",
            "contracts/led-interface.md",
            "contracts/nfc-interface.md",
            "contracts/motion-interface.md",
            "contracts/usb-interface.md",
            "contracts/k1br-bridge.md",
            "contracts/debug-fabric.md",
            "authority/01-DECISION-REGISTER.md",
            "NXP IMXRT1060CEC / MIMXRT1060-EVKB",
            "Espressif ESP32-S3 Hardware Design Guidelines",
            "TI TLV320ADC6120 / TPS62913 / INA226 / TPS25947",
            "ST AN5240 / ST25R3916B / LIS2DH12",
        ],
        "components": components,
        "nets": nets,
        "power_tree_nets": ["5V_PROTECTED", "5V_SYS", "3V3", "+5V_LED_L", "+5V_LED_R", "3V3_MIC", "NFC_5V"],
        "stub_only_wiring": False,
        "blocks": blocks,
        "visual_transactions": visual_transactions,
        "library_bind_note": (
            "device_uuid and library_uuid are stable MPN/value bind keys. "
            "VAL-G2.0B must resolve each unique MPN through EasyEDA search_library_devices "
            "and rewrite the UUIDs before the first place."
        ),
    }


def main() -> None:
    builder = Builder()
    populate(builder)
    plan = emit(builder)
    OUT.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    baseline = plan["option_c_estimated_symbols"]
    print("WROTE", OUT)
    print("BASELINE", baseline)
    print("PLANNED", plan["planned_symbols"])
    print("N_TEST", max(200, math.ceil(1.20 * baseline)))
    print("NETS", len(plan["nets"]))
    print("BLOCKS", len(plan["blocks"]))
    print("EXPLICIT", sum(1 for net in plan["nets"] if net["render"] == "explicit_wire"))
    print("HIGH_FANOUT", sum(1 for net in plan["nets"] if net.get("high_fanout")))


if __name__ == "__main__":
    main()
