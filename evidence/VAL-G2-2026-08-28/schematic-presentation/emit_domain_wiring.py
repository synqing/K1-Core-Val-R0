#!/usr/bin/env python3
"""Emit hub-correct domain wiring drawings (D01 grammar).

Electrical source: HOLD identity + PIN-CONTRACT / H0f-CLOSE / usb-interface.md.
Geometry here is presentation only. It is not an EasyEDA mutation.
"""
from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).with_name("DOMAIN-WIRING.html")


def svg_head(w: int, h: int, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="{title}">'
        "<style>"
        "text{font-family:ui-monospace,Menlo,monospace}"
        ".t{fill:#c00;font:700 22px Space Mono,ui-monospace,monospace}"
        ".z{fill:#c00;font:700 12px Space Mono,ui-monospace,monospace}"
        ".n{fill:#1565c0;font:700 11px ui-monospace,monospace}"
        ".p{fill:#111;font:10px ui-monospace,monospace}"
        ".d{fill:#111;font:10px ui-monospace,monospace}"
        ".k{fill:#333;font:10px ui-monospace,monospace}"
        ".w{stroke:#0a7a3e;stroke-width:1.6;fill:none}"
        ".g{stroke:#111;stroke-width:1.4;fill:none}"
        ".box{fill:#fff;stroke:#111;stroke-width:1.6}"
        ".note{fill:#333;font:11px ui-sans-serif,Helvetica,sans-serif}"
        "</style>"
    )


def wire(x1, y1, x2, y2) -> str:
    return f'<line class="w" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'


def poly(*pts) -> str:
    d = "M " + " L ".join(f"{x} {y}" for x, y in pts)
    return f'<path class="w" d="{d}"/>'


def gnd(x, y) -> str:
    return (
        f'<path class="g" d="M {x} {y} v 8"/>'
        f'<path class="g" d="M {x-10} {y+8} h 20"/>'
        f'<path class="g" d="M {x-7} {y+12} h 14"/>'
        f'<path class="g" d="M {x-4} {y+16} h 8"/>'
    )


def vcc(x, y, name: str) -> str:
    return (
        f'<path class="g" d="M {x} {y} v -10"/>'
        f'<circle cx="{x}" cy="{y-12}" r="2.2" fill="#111"/>'
        f'<text class="n" x="{x+6}" y="{y-10}">{name}</text>'
    )


def label(x, y, text: str, anchor="start") -> str:
    return f'<text class="n" x="{x}" y="{y}" text-anchor="{anchor}">{text}</text>'


def pin_txt(x, y, text: str, anchor="start") -> str:
    return f'<text class="p" x="{x}" y="{y}" text-anchor="{anchor}">{text}</text>'


def res_h(x, y, w, ref, val) -> str:
    return (
        f'<rect class="box" x="{x}" y="{y-7}" width="{w}" height="14" rx="1"/>'
        f'<text class="d" x="{x+w/2}" y="{y-10}" text-anchor="middle">{ref}</text>'
        f'<text class="k" x="{x+w/2}" y="{y+24}" text-anchor="middle">{val}</text>'
    )


def res_v(x, y, h, ref, val) -> str:
    return (
        f'<rect class="box" x="{x-7}" y="{y}" width="14" height="{h}" rx="1"/>'
        f'<text class="d" x="{x+12}" y="{y+h/2}">{ref}</text>'
        f'<text class="k" x="{x+12}" y="{y+h/2+12}">{val}</text>'
    )


def cap_h(x, y, ref, val) -> str:
    return (
        f'<path class="g" d="M {x} {y} h 8"/>'
        f'<path class="g" d="M {x+8} {y-10} v 20"/>'
        f'<path class="g" d="M {x+14} {y-10} v 20"/>'
        f'<path class="g" d="M {x+14} {y} h 8"/>'
        f'<text class="d" x="{x+11}" y="{y-14}" text-anchor="middle">{ref}</text>'
        f'<text class="k" x="{x+11}" y="{y+26}" text-anchor="middle">{val}</text>'
    )


def cap_v(x, y, ref, val) -> str:
    return (
        f'<path class="g" d="M {x} {y} v 6"/>'
        f'<path class="g" d="M {x-10} {y+6} h 20"/>'
        f'<path class="g" d="M {x-10} {y+12} h 20"/>'
        f'<path class="g" d="M {x} {y+12} v 6"/>'
        f'<text class="d" x="{x+14}" y="{y+12}">{ref}</text>'
        f'<text class="k" x="{x+14}" y="{y+24}">{val}</text>'
    )


def diode(x, y, ref, val) -> str:
    return (
        f'<path class="g" d="M {x} {y} h 8"/>'
        f'<path class="g" d="M {x+8} {y-8} v 16 l 14 -8 z" fill="#111"/>'
        f'<path class="g" d="M {x+22} {y-8} v 16"/>'
        f'<path class="g" d="M {x+22} {y} h 8"/>'
        f'<text class="d" x="{x+15}" y="{y-12}" text-anchor="middle">{ref}</text>'
        f'<text class="k" x="{x+15}" y="{y+22}" text-anchor="middle">{val}</text>'
    )


def ic(x, y, w, h, title, left, right) -> str:
    bits = [f'<rect class="box" x="{x}" y="{y}" width="{w}" height="{h}"/>']
    bits.append(
        f'<text class="d" x="{x+w/2}" y="{y+16}" text-anchor="middle">{title}</text>'
    )
    n = max(len(left), 1)
    for i, (num, name) in enumerate(left):
        py = y + 28 + i * ((h - 40) / max(n - 1, 1) if n > 1 else 0)
        bits.append(f'<line class="g" x1="{x-10}" y1="{py}" x2="{x}" y2="{py}"/>')
        bits.append(pin_txt(x + 4, py + 3, f"{num} {name}"))
    n = max(len(right), 1)
    for i, (num, name) in enumerate(right):
        py = y + 28 + i * ((h - 40) / max(n - 1, 1) if n > 1 else 0)
        bits.append(f'<line class="g" x1="{x+w}" y1="{py}" x2="{x+w+10}" y2="{py}"/>')
        bits.append(pin_txt(x + w - 4, py + 3, f"{name} {num}", "end"))
    return "".join(bits)


def frame(x, y, w, h, title) -> str:
    return (
        f'<rect class="box" x="{x}" y="{y}" width="{w}" height="{h}" fill="none"/>'
        f'<text class="z" x="{x+10}" y="{y+16}">{title}</text>'
    )


def d01_power_entry() -> str:
    w, h = 1480, 780
    s = [svg_head(w, h, "1. Power entry")]
    s.append('<text class="t" x="24" y="36">1. POWER ENTRY + PROTECTION — hub</text>')
    s.append(
        '<text class="note" x="24" y="56">'
        "J1 GT-USB-7005A / C5250872 · C1 = 1.0 µF on 5V_USB · data far-side = USB_DP_UP / USB_DM_UP · not USB_DP_RT"
        "</text>"
    )
    s.append(frame(20, 72, 420, 520, "INLET"))
    s.append(ic(70, 120, 200, 360, "J1-PWR1  GT-USB-7005A", [
        ("SH", "SHIELD"),
        ("A1/B1", "GND"),
        ("A12/B12", "GND"),
        ("A4/B4", "VBUS"),
        ("A9/B9", "VBUS"),
        ("A5", "CC1"),
        ("B5", "CC2"),
        ("A6/B6", "DP"),
        ("A7/B7", "DN"),
        ("A8/B8", "SBU NC"),
        ("SS", "SS NC"),
    ], []))
    s.append(wire(40, 148, 70, 148))
    s.append(gnd(40, 148))
    s.append(wire(40, 188, 70, 188))
    s.append(gnd(40, 188))
    s.append(wire(40, 228, 70, 228))
    s.append(gnd(40, 228))
    # VBUS
    s.append(wire(280, 248, 360, 248))
    s.append(wire(360, 248, 360, 200))
    s.append(label(368, 196, "5V_USB"))
    s.append(cap_v(360, 200, "C1-PWR1", "1.0µF"))
    s.append(gnd(360, 236))
    s.append(wire(360, 248, 430, 248))
    s.append(diode(360, 300, "D3-USB", "SMF5.0A"))
    s.append(wire(360, 248, 360, 300))
    s.append(wire(390, 300, 430, 300))
    s.append(gnd(430, 300))
    s.append(wire(430, 248, 430, 340))
    s.append(res_v(430, 340, 70, "R80-USB", "4.7k"))
    s.append(gnd(430, 410))
    # CC
    s.append(wire(280, 328, 340, 328))
    s.append(res_h(340, 328, 70, "RCC1-PWR1", "5.1k Rd"))
    s.append(wire(410, 328, 430, 328))
    s.append(gnd(430, 328))
    s.append(label(250, 324, "USB_CC1", "end"))
    s.append(wire(280, 368, 340, 368))
    s.append(res_h(340, 368, 70, "RCC2-PWR1", "5.1k Rd"))
    s.append(wire(410, 368, 430, 368))
    s.append(gnd(430, 368))
    s.append(label(250, 364, "USB_CC2", "end"))
    s.append('<text class="note" x="40" y="610">CC sense RCC1S/RCC2S TUNE_TBD stay on J1. No J7 Rd.</text>')

    s.append(frame(460, 72, 380, 520, "ESD + 0Ω"))
    s.append(ic(500, 150, 220, 280, "D1-PWR1  USBLC6-2SC6", [
        ("1", "I/O1  DP J1"),
        ("3", "I/O2  DN J1"),
        ("2", "GND"),
        ("5", "Vbus"),
    ], [
        ("6", "I/O1' UP"),
        ("4", "I/O2' UP"),
    ]))
    s.append(poly((280, 408), (450, 408), (450, 178), (500, 178)))
    s.append(label(300, 400, "USB_DP_J1"))
    s.append(poly((280, 448), (438, 448), (438, 218), (500, 218)))
    s.append(label(300, 460, "USB_DN_J1"))
    s.append(wire(490, 258, 500, 258))
    s.append(gnd(490, 258))
    s.append(poly((360, 248), (470, 248), (470, 298), (500, 298)))
    s.append(wire(730, 178, 780, 178))
    s.append(res_h(780, 178, 70, "RUSB_DP", "0Ω"))
    s.append(wire(850, 178, 920, 178))
    s.append(label(928, 174, "USB_DP_UP"))
    s.append(wire(730, 218, 780, 218))
    s.append(res_h(780, 218, 70, "RUSB_DN", "0Ω"))
    s.append(wire(850, 218, 920, 218))
    s.append(label(928, 214, "USB_DM_UP"))

    s.append(frame(860, 250, 590, 342, "eFUSE + INA"))
    s.append(ic(900, 290, 220, 250, "U1-PWR1  TPS259474L", [
        ("1", "IN"),
        ("2", "EN/UVLO"),
        ("3", "OVLO"),
        ("4", "dVdt"),
        ("8", "GND"),
    ], [
        ("5", "OUT"),
        ("6", "PGTH"),
        ("7", "ILIM"),
        ("9", "PG"),
        ("10", "ITIMER"),
    ]))
    s.append(poly((430, 248), (860, 248), (860, 318), (900, 318)))
    s.append(label(700, 240, "5V_USB → U1.IN"))
    s.append(wire(890, 458, 900, 458))
    s.append(gnd(890, 458))
    s.append(wire(1130, 318, 1180, 318))
    s.append(label(1188, 314, "5V_PROTECTED"))
    s.append(cap_v(1180, 330, "C2-PWR1", "22µF KEEP"))
    s.append(gnd(1180, 366))
    s.append(cap_v(1230, 330, "C120-USB", "22µF ADD"))
    s.append(gnd(1230, 366))
    s.append(wire(1180, 318, 1230, 318))
    s.append(res_v(1130, 370, 50, "R1-PWR1", "1.24k ILIM"))
    s.append(gnd(1130, 420))
    s.append(wire(1130, 398, 1130, 370))
    s.append(wire(1130, 358, 1120, 398))
    s.append(ic(1180, 430, 240, 140, "U2-PWR1  INA226", [
        ("10", "VIN+"),
        ("9", "VIN−"),
        ("8", "VBUS"),
        ("3", "VS"),
    ], [
        ("6", "SCL"),
        ("5", "SDA"),
        ("4", "ALERT"),
    ]))
    s.append(wire(1180, 318, 1180, 458))
    s.append(res_h(1180, 400, 80, "RSH1", "10mΩ"))
    s.append(wire(1260, 400, 1320, 400))
    s.append(label(1328, 396, "5V_SYS"))
    s.append(label(1420, 458, "I2C_SCL", "end"))
    s.append(label(1420, 478, "I2C_SDA", "end"))
    s.append(
        '<text class="note" x="24" y="720">'
        "Δ vs old D01: USB4105 retired (J1-USB4105-RETIRED). DVBUS-PWR1 deleted; D3-USB is the inlet TVS. "
        "D1 far side is hub US, not RT OTG1. C1 is U22 CIN, not 22 µF."
        "</text>"
    )
    s.append(
        '<text class="note" x="24" y="742">'
        "U1 setpoints remain the living eFuse network (R63/R2/R64, R65/R66, C67, C2). PG net PWR_ENTRY_PG_RT_IOMUX_TBD."
        "</text>"
    )
    s.append("</svg>")
    return "".join(s)


def d02_usb_hub() -> str:
    w, h = 1480, 920
    s = [svg_head(w, h, "2. USB hub")]
    s.append('<text class="t" x="24" y="36">2. USB2422 HUB + F6-B VALIDITY — new</text>')
    s.append(
        '<text class="note" x="24" y="56">'
        "NON_REM[1:0]=10 · CFG_SEL low · F6_VALIDITY_SOURCE=5V0_USB_VALID · GPIO15=USB_5V_VALID via R85"
        "</text>"
    )
    s.append(frame(20, 72, 720, 520, "U20-USB USB2422T-I/MJ"))
    s.append(ic(80, 110, 280, 430, "U20-USB", [
        ("20", "DP_UP"),
        ("19", "DM_UP"),
        ("4", "DP_DN1"),
        ("3", "DM_DN1"),
        ("5", "DP_DN2"),
        ("2", "DM_DN2"),
        ("16", "VBUS_DET"),
        ("7", "PRTPWR1"),
        ("11", "PRTPWR2"),
        ("8", "OCS1_N"),
        ("12", "OCS2_N"),
        ("6", "NC"),
    ], [
        ("1", "VDD33"),
        ("9", "VDD33"),
        ("18", "VDD33"),
        ("10", "CRFILT"),
        ("23", "PLLFILT"),
        ("24", "RBIAS"),
        ("22", "XTALIN"),
        ("21", "XTALOUT"),
        ("15", "RESET_N"),
        ("14", "CFG_SEL"),
        ("13", "NON_REM1"),
        ("17", "NON_REM0"),
    ]))
    s.append(wire(20, 138, 80, 138))
    s.append(label(18, 134, "USB_DP_UP", "end"))
    s.append(wire(20, 174, 80, 174))
    s.append(label(18, 170, "USB_DM_UP", "end"))
    s.append(wire(20, 210, 80, 210))
    s.append(label(18, 206, "USB_DP_DN1 → U6 L8", "end"))
    s.append(wire(20, 246, 80, 246))
    s.append(label(18, 242, "USB_DM_DN1 → U6 M8", "end"))
    s.append(wire(20, 282, 80, 282))
    s.append(label(18, 278, "USB_DP_DN2 → R94", "end"))
    s.append(wire(20, 318, 80, 318))
    s.append(label(18, 314, "USB_DM_DN2 → R94", "end"))
    s.append(wire(20, 354, 80, 354))
    s.append(label(18, 350, "USB_VBUS_DET", "end"))
    s.append(wire(20, 390, 80, 390))
    s.append(label(18, 386, "USB_PRTPWR1", "end"))
    s.append(wire(20, 426, 80, 426))
    s.append(label(18, 422, "USB_PRTPWR2", "end"))
    s.append(wire(20, 462, 80, 462))
    s.append(label(18, 458, "USB_OCS1_N", "end"))
    s.append(wire(20, 498, 80, 498))
    s.append(label(18, 494, "USB_OCS2_N", "end"))

    s.append(vcc(380, 138, "3V3"))
    s.append(cap_v(420, 138, "C104", "100n p1"))
    s.append(gnd(420, 174))
    s.append(cap_v(460, 138, "C105", "1µF p9"))
    s.append(gnd(460, 174))
    s.append(cap_v(500, 138, "C106", "100n p18"))
    s.append(gnd(500, 174))
    s.append(cap_v(540, 210, "C100", "1µF CRFILT"))
    s.append(gnd(540, 246))
    s.append(cap_v(580, 246, "C101", "100n PLL"))
    s.append(gnd(580, 282))
    s.append(res_v(540, 300, 60, "R77", "12k 1%"))
    s.append(gnd(540, 360))
    s.append(wire(370, 390, 540, 300))
    s.append(ic(600, 300, 120, 90, "Y3-USB 24MHz", [("1", "XIN"), ("3", "XOUT")], []))
    s.append(cap_v(620, 400, "C102", "12p"))
    s.append(gnd(620, 436))
    s.append(cap_v(660, 400, "C103", "12p"))
    s.append(gnd(660, 436))
    s.append(res_v(400, 470, 50, "R88", "100k CFG low"))
    s.append(gnd(400, 520))
    s.append(res_v(450, 430, 50, "R89", "100k NR1 hi"))
    s.append(vcc(450, 430, "3V3"))
    s.append(res_v(500, 470, 50, "R90", "100k NR0 lo"))
    s.append(gnd(500, 520))
    s.append(res_v(370, 420, 50, "R91", "10k RESET"))
    s.append(vcc(370, 420, "3V3"))

    s.append(frame(760, 72, 700, 250, "U22 LDO  +  VBUS_DET"))
    s.append(ic(800, 100, 200, 180, "U22-USB  TPS7A2550", [
        ("6", "IN"),
        ("4", "EN"),
        ("5", "GND"),
        ("2", "NC→GND"),
        ("3", "PG NC"),
    ], [
        ("1", "OUT"),
    ]))
    s.append(wire(760, 128, 800, 128))
    s.append(label(758, 124, "5V_USB", "end"))
    s.append(wire(760, 164, 800, 164))
    s.append(cap_v(1040, 120, "C121", "100n HF"))
    s.append(gnd(1040, 156))
    s.append(wire(1010, 148, 1100, 148))
    s.append(label(1108, 144, "5V0_USB_VALID"))
    s.append(cap_v(1100, 160, "C122", "2.2µF"))
    s.append(gnd(1100, 196))
    s.append(res_h(800, 310, 80, "R78", "100k"))
    s.append(wire(760, 310, 800, 310))
    s.append(label(758, 306, "5V_USB", "end"))
    s.append(wire(880, 310, 940, 310))
    s.append(label(820, 300, "USB_VBUS_DET"))
    s.append(res_h(940, 310, 80, "R79", "100k"))
    s.append(gnd(1020, 310))

    s.append(frame(760, 340, 700, 250, "KILL-B + AND"))
    s.append(ic(800, 370, 180, 160, "U23-USB  TLV7031", [
        ("3", "IN+ TAP_VBUS"),
        ("4", "IN− TAP_REF"),
        ("2", "GND"),
        ("5", "V+ 3V3"),
    ], [
        ("1", "OUT"),
    ]))
    s.append(res_h(760, 398, 70, "R81", "169k"))
    s.append(res_v(840, 540, 40, "R82", "100k"))
    s.append(gnd(840, 580))
    s.append(res_h(760, 434, 70, "R83", "100k from 3V3"))
    s.append(res_v(900, 540, 40, "R84", "100k"))
    s.append(gnd(900, 580))
    s.append(wire(990, 410, 1040, 410))
    s.append(label(1048, 406, "USB_5V_VALID"))
    s.append(res_h(1100, 410, 70, "R85", "470Ω"))
    s.append(wire(1170, 410, 1240, 410))
    s.append(label(1248, 406, "U9.8 GPIO15"))
    s.append(ic(1040, 450, 140, 120, "U24  1G08", [("1", "PRTPWR1"), ("3", "VALID")], [("4", "EN1")]))
    s.append(ic(1200, 450, 140, 120, "U25  1G08", [("1", "PRTPWR2"), ("3", "VALID")], [("4", "EN2")]))

    s.append(frame(20, 610, 1440, 250, "U21-USB TPS2052BDR  — validity switch, not MCU power"))
    s.append(ic(80, 650, 240, 180, "U21-USB", [
        ("2", "IN"),
        ("3", "EN1"),
        ("4", "EN2"),
        ("1", "GND"),
    ], [
        ("7", "OUT1"),
        ("6", "OUT2"),
        ("8", "OC1"),
        ("5", "OC2"),
    ]))
    s.append(wire(60, 678, 80, 678))
    s.append(label(58, 674, "5V0_USB_VALID", "end"))
    s.append(wire(60, 714, 80, 714))
    s.append(label(58, 710, "USB_EN1", "end"))
    s.append(wire(60, 750, 80, 750))
    s.append(label(58, 746, "USB_EN2", "end"))
    s.append(gnd(70, 786))
    s.append(wire(330, 678, 420, 678))
    s.append(label(428, 674, "RT_USB_VBUS → U6 N6"))
    s.append(res_v(420, 700, 50, "R86", "4.7k"))
    s.append(gnd(420, 750))
    s.append(cap_v(480, 678, "CUSBVBUS-RTC", "1µF"))
    s.append(gnd(480, 714))
    s.append(wire(330, 714, 560, 714))
    s.append(label(568, 710, "S3_USB_VBUS_VALID  bleeder only"))
    s.append(res_v(560, 730, 50, "R87", "10k"))
    s.append(gnd(560, 780))
    s.append(wire(330, 750, 700, 750))
    s.append(label(708, 746, "USB_OCS1_N"))
    s.append(wire(330, 786, 700, 786))
    s.append(label(708, 782, "USB_OCS2_N"))
    s.append(
        '<text class="note" x="40" y="850">'
        "XOR: R94-USB 0Ω FIT hub DN2; R95-USB 0Ω DNP to J12-USB. S3 TUNE RUSB_S3_DP/DM 22Ω at GPIO20/19. "
        "D4-USB BAT54 DNP. Do not power cores from OUT1/OUT2."
        "</text>"
    )
    s.append("</svg>")
    return "".join(s)


def d03_power_reg() -> str:
    w, h = 1480, 640
    s = [svg_head(w, h, "3. Power conversion")]
    s.append('<text class="t" x="24" y="36">3. POWER CONVERSION + DISTRIBUTION</text>')
    s.append(frame(20, 60, 480, 520, "U3-PWR2 TPS62913  5V_SYS → 3V3"))
    s.append(ic(60, 100, 220, 280, "U3-PWR2", [
        ("2", "VIN"),
        ("10", "S-CONF"),
        ("1", "EN"),
        ("7", "NR/SS"),
        ("4", "PGND"),
        ("5", "PSNS"),
    ], [
        ("3", "SW"),
        ("9", "VO"),
        ("8", "FB"),
        ("6", "PG"),
    ]))
    s.append(wire(40, 128, 60, 128))
    s.append(label(38, 124, "5V_SYS", "end"))
    s.append(cap_v(40, 150, "C5", "22µF"))
    s.append(gnd(40, 186))
    s.append(res_h(40, 200, 60, "R7", "100k EN"))
    s.append(cap_v(40, 250, "C10", "100n SS"))
    s.append(gnd(40, 286))
    s.append(wire(290, 148, 360, 148))
    s.append(res_h(360, 148, 50, "L1", "2.2µH"))
    s.append(wire(410, 148, 470, 148))
    s.append(label(478, 144, "3V3"))
    s.append(cap_v(360, 180, "C6", "47µF"))
    s.append(gnd(360, 216))
    s.append(cap_v(400, 180, "C7", "47µF"))
    s.append(gnd(400, 216))
    s.append(res_h(360, 250, 50, "R5", "100k"))
    s.append(res_v(420, 250, 50, "R6", "32.4k"))
    s.append(gnd(420, 300))
    s.append(res_h(290, 320, 60, "R75", "10k PG"))
    s.append(vcc(360, 320, "3V3"))
    s.append(label(290, 310, "BUCK_PG"))

    s.append(frame(520, 60, 460, 280, "U17-PWR2 TPS2561  LED branches"))
    s.append(ic(560, 90, 200, 200, "U17-PWR2", [
        ("2/3", "IN"),
        ("4", "EN1"),
        ("5", "EN2"),
        ("7", "ILIM"),
    ], [
        ("9", "OUT1"),
        ("8", "OUT2"),
        ("10", "FAULT1#"),
        ("6", "FAULT2#"),
    ]))
    s.append(wire(540, 118, 560, 118))
    s.append(label(538, 114, "5V_SYS", "end"))
    s.append(label(538, 154, "LED_PWR_L_EN", "end"))
    s.append(label(538, 190, "LED_PWR_R_EN", "end"))
    s.append(res_v(540, 230, 40, "RILIM-LED", "59k"))
    s.append(gnd(540, 270))
    s.append(wire(770, 118, 850, 118))
    s.append(label(780, 108, "FB1 → +5V_LED_L"))
    s.append(wire(770, 154, 850, 154))
    s.append(label(780, 144, "FB2 → +5V_LED_R"))
    s.append(label(770, 190, "LED_FAULT_L_N"))
    s.append(label(770, 226, "LED_FAULT_R_N"))

    s.append(frame(520, 360, 460, 220, "MIC  U5 + Q1"))
    s.append(ic(560, 390, 160, 140, "U5-PWR2 TLV75533", [
        ("1", "IN"),
        ("3", "EN"),
    ], [
        ("5", "OUT"),
    ]))
    s.append(label(540, 418, "5V_SYS", "end"))
    s.append(label(740, 418, "3V3_MIC_REG"))
    s.append(ic(800, 390, 140, 140, "Q1 DMG2305UX", [("S", "REG"), ("G", "EN")], [("D", "3V3_MIC")]))
    s.append(label(800, 530, "MIC_PWR_EN  RT GPIO"))

    s.append(frame(1000, 60, 450, 280, "NFC_5V from 5V_SYS"))
    s.append(wire(1020, 140, 1080, 140))
    s.append(label(1020, 130, "5V_SYS"))
    s.append(res_h(1080, 140, 60, "FB3", "220Ω@100M"))
    s.append(wire(1140, 140, 1220, 140))
    s.append(label(1228, 136, "NFC_5V"))
    s.append(cap_v(1180, 160, "C16", "22µF"))
    s.append(gnd(1180, 196))
    s.append(cap_v(1220, 160, "C17", "100n"))
    s.append(gnd(1220, 196))
    s.append(
        '<text class="note" x="24" y="610">'
        "NFC rail stays on 5V_SYS, not 3V3_MIC. FAULT1# is not strapped to GND. R75 is required (D-045)."
        "</text>"
    )
    s.append("</svg>")
    return "".join(s)


def d04_rt_core() -> str:
    w, h = 1480, 620
    s = [svg_head(w, h, "4. RT1062 core")]
    s.append('<text class="t" x="24" y="36">4. RT1062 COMPUTE + CORE POWER</text>')
    s.append(ic(80, 80, 520, 420, "U6-RTC  MIMXRT1062DVJ6B", [
        ("L1/L2", "DCDC_IN  3V3"),
        ("K8", "DCDC_IN_Q  3V3"),
        ("K3", "DCDC_PSWITCH"),
        ("L4", "DCDC_SW"),
        ("J5", "DCDC_SENSE"),
        ("M1", "DCDC_LP GND"),
        ("N3", "TEST_MODE GND"),
        ("L8", "OTG1_DP  USB_DP_DN1"),
        ("M8", "OTG1_DN  USB_DM_DN1"),
        ("N6", "OTG1_VBUS  RT_USB_VBUS"),
    ], [
        ("SOC", "1V15_CORE"),
        ("NVCC", "3V3"),
        ("M7", "POR_B"),
        ("N9/P9", "RTC xtal GND"),
        ("L9", "ONOFF GND"),
    ]))
    s.append(res_h(40, 200, 50, "R79", "100k"))
    s.append(cap_v(40, 230, "C89", "100n"))
    s.append(gnd(40, 266))
    s.append(res_h(620, 200, 50, "L4", "DCDC L"))
    s.append(label(680, 196, "1V15_CORE"))
    s.append(ic(900, 80, 220, 180, "U7-RTC TPS3808G33", [
        ("1", "VDD 3V3"),
        ("3", "SENSE 3V3"),
        ("6", "MR#"),
        ("5", "CT"),
    ], [
        ("4", "RESET_N"),
    ]))
    s.append(label(1140, 140, "POR_B"))
    s.append(label(880, 160, "RT_RESET_REQ_N", "end"))
    s.append(
        '<text class="note" x="24" y="560">'
        "Δ vs old D03: N6 is RT_USB_VBUS + CUSBVBUS-RTC 1 µF, not NC/GND. USB pairs are hub DN1, not J1 far-side."
        "</text>"
    )
    s.append(
        '<text class="note" x="24" y="582">'
        "Decoupling matrix (C18–C89) stays on 1V15_CORE / 3V3 / VDD_*_CAP as in the freeze. POR_B lands M7."
        "</text>"
    )
    s.append("</svg>")
    return "".join(s)


def d05_boot() -> str:
    w, h = 1480, 560
    s = [svg_head(w, h, "5. Boot debug")]
    s.append('<text class="t" x="24" y="36">5. RT1062 BOOT + CLOCK + DEBUG</text>')
    s.append(ic(40, 80, 280, 280, "U6 FlexSPI / SWD / UART", [
        ("L3", "SS0"),
        ("M4", "SCLK"),
        ("P3", "D0"),
        ("N3", "D1"),
        ("R5", "D2"),
        ("P5", "D3"),
        ("F12", "SWCLK"),
        ("E14", "SWDIO"),
        ("L14", "LPUART1_TX"),
        ("M14", "LPUART1_RX"),
        ("G14", "BOOT_MODE0"),
        ("K14", "BOOT_MODE1"),
        ("P11", "XTALI"),
        ("M11", "XTALO"),
    ], []))
    s.append(ic(400, 80, 200, 220, "U8-RTDBG IS25LP064A", [
        ("1", "CE#"),
        ("6", "SCK"),
        ("5", "SI"),
        ("2", "SO"),
        ("3", "WP#"),
        ("7", "HOLD#"),
    ], [("8", "VCC 3V3")]))
    s.append(vcc(620, 120, "3V3"))
    s.append(ic(700, 80, 220, 200, "J4-RTDBG Cortex-10", [
        ("1", "VTref 3V3"),
        ("2", "SWDIO via R16 22R"),
        ("4", "SWCLK via R15 22R"),
        ("7", "RX via R18"),
        ("8", "TX via R17"),
        ("10", "RESET# POR_B"),
    ], []))
    s.append(ic(960, 80, 160, 140, "J5 UART 1x4", [("1", "TX_H"), ("2", "RX_H"), ("4", "GND")], []))
    s.append(ic(700, 320, 160, 100, "Y1 24MHz", [("1", "XTALI"), ("3", "XTALO")], []))
    s.append(res_h(400, 340, 60, "R10", "10k MODE0 L"))
    s.append(gnd(400, 380))
    s.append(res_h(500, 340, 60, "R11", "10k MODE1 H"))
    s.append(vcc(500, 320, "3V3"))
    s.append(
        '<text class="note" x="24" y="520">'
        "Internal boot FlexSPI: MODE1=1 MODE0=0. SDL button SW4-VAL pulls BOOT_MODE1, not MODE0."
        "</text>"
    )
    s.append("</svg>")
    return "".join(s)


def d06_s3() -> str:
    w, h = 1480, 620
    s = [svg_head(w, h, "6. ESP32-S3")]
    s.append('<text class="t" x="24" y="36">6. ESP32-S3 RADIO + SERVICE — no J7</text>')
    s.append(ic(60, 80, 360, 420, "U9-ESP  ESP32-S3-WROOM-1", [
        ("1", "VDD  3V3_S3_FILTERED"),
        ("3", "EN"),
        ("27", "IO0"),
        ("13", "IO19 USB_DM"),
        ("14", "IO20 USB_DP"),
        ("8", "IO15 USB_5V_VALID"),
        ("37", "TXD0"),
        ("36", "RXD0"),
        ("38", "SDA"),
        ("39", "SCL"),
        ("18-22", "K1BR via 22Ω"),
        ("4", "NFC_IRQ"),
        ("5", "MOTION_INT_S3"),
        ("6", "S3_POR_REQ"),
        ("7", "RT_PWR_VALID"),
    ], []))
    s.append(res_h(40, 140, 50, "FB6", "220Ω"))
    s.append(label(20, 130, "3V3"))
    s.append(ic(500, 80, 200, 180, "J6-ESP 1x6", [
        ("1", "GND"),
        ("2", "VCC 3V3"),
        ("3", "TX"),
        ("4", "RX"),
        ("5", "EN"),
        ("6", "IO0"),
    ], []))
    s.append(ic(740, 80, 200, 200, "USB from hub DN2", [
        ("R94", "0Ω FIT"),
        ("RUSB_S3_DP", "22Ω TUNE"),
        ("RUSB_S3_DM", "22Ω TUNE"),
        ("R85", "470Ω GPIO15"),
    ], []))
    s.append(label(960, 120, "USB_DP_DN2"))
    s.append(label(960, 150, "USB_DM_DN2"))
    s.append(label(960, 180, "USB_5V_VALID"))
    s.append(ic(500, 300, 200, 140, "SW2 BOOT / SW3 EN", [("SW2", "IO0"), ("SW3", "EN")], []))
    s.append(
        '<text class="note" x="24" y="560">'
        "J7-ESP is gone. No USBLC6 on a second Type-C. Service USB is hub DN2 into GPIO20/19. "
        "GPIO15 is USB_5V_VALID, not OUT2, not a VBUS divider on S3_VBUS."
        "</text>"
    )
    s.append(
        '<text class="note" x="24" y="582">'
        "K1BR: IO10–14 through R23–R27 22Ω to RT. Unused IO marked NC on the living sheet."
        "</text>"
    )
    s.append("</svg>")
    return "".join(s)


def d07_audio() -> str:
    w, h = 1480, 560
    s = [svg_head(w, h, "7. Audio")]
    s.append('<text class="t" x="24" y="36">7. AUDIO CAPTURE + CLOCK + MIC FLEX</text>')
    s.append(ic(40, 80, 280, 320, "U11-AUD  TLV320ADC6120", [
        ("9/16", "IOVDD/AVDD 3V3"),
        ("12", "SDA"),
        ("13", "SCL"),
        ("11", "PDM_CLK"),
        ("3", "PDM_DAT"),
        ("8", "SDOUT"),
        ("7", "BCLK"),
        ("6", "FSYNC"),
        ("19", "MCLK"),
    ], []))
    s.append(ic(400, 80, 200, 200, "J9-AUD FH12-10S", [
        ("1", "3V3_MIC_FLEX"),
        ("3", "PDM_CLK"),
        ("5", "PDM_DAT"),
        ("2/4/6", "GND"),
    ], []))
    s.append(res_h(400, 320, 50, "R38", "0Ω FIT CLK→ADC"))
    s.append(res_h(500, 320, 50, "R40", "10k DNP CLK→RT"))
    s.append(res_h(400, 360, 50, "R39", "0Ω FIT DAT→ADC"))
    s.append(res_h(500, 360, 50, "R41", "10k DNP DAT→RT"))
    s.append(ic(700, 80, 180, 140, "J8 clock tap", [
        ("1", "MCLK"),
        ("2", "BCLK"),
        ("3", "FSYNC"),
        ("4", "GND"),
    ], []))
    s.append(res_h(700, 260, 50, "R31", "22R MCLK"))
    s.append(res_h(770, 260, 50, "R32", "22R BCLK"))
    s.append(res_h(840, 260, 50, "R33", "22R FSYNC"))
    s.append(res_h(700, 300, 50, "R37", "0R DOUT"))
    s.append(label(900, 256, "→ RT SAI  IOMUX_TBD"))
    s.append(res_h(400, 420, 50, "FB5", "220Ω MIC"))
    s.append(label(380, 410, "3V3_MIC"))
    s.append(
        '<text class="note" x="24" y="520">'
        "XOR PDM: ADC path fitted, RT path DNP. AUDIO_DOUT must land on an RT port — not dead at R37."
        "</text>"
    )
    s.append("</svg>")
    return "".join(s)


def d08_nfc() -> str:
    w, h = 1480, 560
    s = [svg_head(w, h, "8. NFC")]
    s.append('<text class="t" x="24" y="36">8. NFC FRONT END + ANTENNA</text>')
    s.append(ic(40, 80, 320, 360, "U12-NFC  ST25R3916B", [
        ("1", "VDD_IO 3V3"),
        ("2/9", "VDD NFC_5V"),
        ("8/10", "VDD_TX NFC_5V"),
        ("13", "RFO1"),
        ("15", "RFO2 NC"),
        ("22", "RFI1"),
        ("24", "RFI2 NC"),
        ("32", "SCL"),
        ("33", "SDA"),
        ("27", "IRQ → S3 IO4"),
        ("23", "I2C_EN"),
        ("4/5", "XTI/XTO"),
    ], []))
    s.append(res_h(380, 140, 50, "L2", "TUNE"))
    s.append(res_h(450, 140, 50, "R42", "TUNE"))
    s.append(cap_v(500, 160, "C60", "TUNE"))
    s.append(ic(560, 100, 140, 100, "J10 U.FL", [("1", "SIG"), ("2", "SHIELD")], []))
    s.append(gnd(700, 180))
    s.append(cap_v(500, 220, "CRFI1", "TUNE RX"))
    s.append(res_v(560, 220, 50, "RRFI1", "TUNE"))
    s.append(gnd(560, 270))
    s.append(ic(380, 280, 140, 100, "Y2 27.12MHz", [("1", "XTI"), ("3", "XTO")], []))
    s.append(res_h(380, 400, 50, "R76", "10k I2C_EN"))
    s.append(vcc(440, 400, "3V3"))
    s.append(
        '<text class="note" x="24" y="520">'
        "VDD on NFC_5V with VDD_TX. Crystal pin 3 is XTO. RX divider is required; do not strap RFI1 to the antenna node."
        "</text>"
    )
    s.append("</svg>")
    return "".join(s)


def d09_motion() -> str:
    w, h = 1480, 480
    s = [svg_head(w, h, "9. Motion")]
    s.append('<text class="t" x="24" y="36">9. MOTION / ACCELEROMETER</text>')
    s.append(ic(60, 80, 240, 240, "U13-MOT  LIS2DH12TR", [
        ("9/10", "VDD/VDD_IO 3V3"),
        ("2", "CS → 3V3 I2C"),
        ("3", "SA0 GND → 0x18"),
        ("5-8", "RES/GND"),
        ("1", "SCL"),
        ("4", "SDA"),
        ("12", "INT1"),
        ("11", "INT2 NC"),
    ], []))
    s.append(cap_v(40, 120, "C62", "100n"))
    s.append(gnd(40, 156))
    s.append(cap_v(40, 180, "C63", "100n"))
    s.append(gnd(40, 216))
    s.append(cap_v(40, 240, "CMOT-BULK", "10µF"))
    s.append(gnd(40, 276))
    s.append(res_h(360, 200, 50, "R46", "0Ω FIT SCL"))
    s.append(res_h(440, 200, 50, "R47", "10k DNP"))
    s.append(res_h(360, 250, 50, "R44", "0Ω FIT SDA"))
    s.append(res_h(440, 250, 50, "R45", "10k DNP"))
    s.append(res_h(360, 300, 50, "R48", "0Ω INT_RT"))
    s.append(res_h(440, 300, 50, "R49", "10k DNP S3"))
    s.append(label(540, 196, "I2C_SCL / I2C_SDA"))
    s.append(label(540, 296, "MOTION_INT_RT fitted"))
    s.append(
        '<text class="note" x="24" y="440">'
        "Default owner RT1062. INT2 stays NC. MOTION_INT_RT must land on an RT GPIO, not die at the resistor."
        "</text>"
    )
    s.append("</svg>")
    return "".join(s)


def d10_led() -> str:
    w, h = 1480, 560
    s = [svg_head(w, h, "10. LED")]
    s.append('<text class="t" x="24" y="36">10. LED DATA + TEMPERATURE</text>')
    s.append(ic(40, 80, 220, 180, "U14-LED  AHCT1G125 L", [
        ("2", "A LED_D0_3V3"),
        ("1", "OE# LED_OE_L"),
        ("5", "VCC +5V_LED_L"),
        ("3", "GND"),
    ], [
        ("4", "Y LED_D0_5V"),
    ]))
    s.append(res_v(40, 280, 40, "RLED_PD0", "10k"))
    s.append(gnd(40, 320))
    s.append(res_h(280, 140, 50, "R51", "33R TUNE"))
    s.append(ic(360, 80, 140, 120, "J2-LED XH-3", [
        ("1", "+5V_LED_L"),
        ("2", "DATA"),
        ("3", "GND"),
    ], []))
    s.append(ic(40, 340, 220, 180, "U15-LED  AHCT1G125 R", [
        ("2", "A LED_D1_3V3"),
        ("1", "OE# LED_OE_R"),
        ("5", "VCC +5V_LED_R"),
    ], [
        ("4", "Y LED_D1_5V"),
    ]))
    s.append(res_h(280, 400, 50, "R52", "33R TUNE"))
    s.append(ic(360, 340, 140, 120, "J3-LED XH-3", [
        ("1", "+5V_LED_R"),
        ("2", "DATA"),
        ("3", "GND"),
    ], []))
    s.append(res_h(600, 120, 50, "RNTC_L", "10k"))
    s.append(vcc(600, 100, "3V3"))
    s.append(res_v(680, 120, 50, "RT1", "10k NTC"))
    s.append(gnd(680, 170))
    s.append(label(700, 140, "LED_THERM_L  ADC IOMUX_TBD"))
    s.append(res_h(600, 220, 50, "RNTC_R", "10k"))
    s.append(res_v(680, 220, 50, "RT2", "10k NTC"))
    s.append(gnd(680, 270))
    s.append(label(700, 240, "LED_THERM_R  ADC IOMUX_TBD"))
    s.append(
        '<text class="note" x="24" y="540">'
        "Data pull-downs fitted. Temperature dividers complete. 33Ω series is TUNE_TBD. Enables default low."
        "</text>"
    )
    s.append("</svg>")
    return "".join(s)


def d11_val() -> str:
    w, h = 1480, 560
    s = [svg_head(w, h, "11. Validation")]
    s.append('<text class="t" x="24" y="36">11. DEBUG / RECOVERY + VALIDATION OPTIONS</text>')
    s.append(ic(40, 80, 220, 180, "U16-VAL TPS3808G33", [
        ("1", "VDD 3V3"),
        ("6", "SENSE 3V3"),
        ("3", "MR# 3V3"),
        ("4", "CT"),
        ("2", "GND"),
    ], [
        ("4", "RESET#"),
    ]))
    s.append(cap_v(40, 280, "C66", "100n CT"))
    s.append(label(280, 140, "RT_PWR_VALID → U9.7"))
    s.append(ic(400, 80, 200, 180, "Q2-VAL 2N7002", [
        ("G", "S3_POR_REQ via R60"),
        ("S", "GND"),
        ("D", "S3_POR_OD via R59"),
    ], []))
    s.append(label(620, 140, "POR_B"))
    s.append(ic(400, 300, 200, 160, "J11-VAL 1x6", [
        ("1", "OPT_BOOT_REC"),
        ("2", "OPT_USB_AUD DNP"),
        ("3", "OPT_MCLK DNP"),
        ("4", "OPT_S3_LOG"),
        ("5", "3V3"),
        ("6", "GND"),
    ], []))
    s.append(ic(680, 80, 200, 140, "SW4-VAL SDL", [("R61", "10k"), ("SW", "BOOT_MODE1")], []))
    s.append(gnd(680, 240))
    s.append(
        '<text class="note" x="24" y="500">'
        "J1-USB4105-RETIRED stays on the sheet as a retired symbol; it is not a second receptacle. "
        "OPT_USB_AUD is a VAL strap, not OTG1."
        "</text>"
    )
    s.append("</svg>")
    return "".join(s)


SECTIONS = [
    ("d01", "1. Power entry", "J1 · ESD · eFuse · INA", d01_power_entry),
    ("d02", "2. USB hub + F6-B", "USB2422 · LDO · KILL-B · TPS2052B", d02_usb_hub),
    ("d03", "3. Power conversion", "Buck · LED switch · MIC · NFC_5V", d03_power_reg),
    ("d04", "4. RT1062 core", "DCDC · POR · USB OTG1 on DN1", d04_rt_core),
    ("d05", "5. Boot + debug", "FlexSPI · SWD · UART · 24 MHz", d05_boot),
    ("d06", "6. ESP32-S3", "No J7 · DN2 TUNE · GPIO15 valid", d06_s3),
    ("d07", "7. Audio", "ADC6120 · XOR PDM · SAI", d07_audio),
    ("d08", "8. NFC", "ST25R3916B · matching TUNE", d08_nfc),
    ("d09", "9. Motion", "LIS2DH12 · XOR owner", d09_motion),
    ("d10", "10. LED + NTC", "AHCT · XH-3 · thermistors", d10_led),
    ("d11", "11. Validation", "U16 · cross-reset · options", d11_val),
]


def html() -> str:
    nav = "".join(
        f'<a href="#{sid}">{title}</a>' for sid, title, _sub, _fn in SECTIONS
    )
    cards = []
    for sid, title, sub, fn in SECTIONS:
        cards.append(
            f'<section id="{sid}" class="card">'
            f"<h2>{title}</h2>"
            f'<p class="sub">{sub}</p>'
            f"{fn()}"
            "</section>"
        )
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8"/>
<title>K1-CORE-VAL-R0 domain component wiring — hub</title>
<style>
  :root {{ --ink:#111; --paper:#f4f1ea; --red:#c00; }}
  body {{ margin:0; background:var(--paper); color:var(--ink);
         font:16px/1.45 ui-sans-serif,Helvetica,sans-serif; }}
  header {{ padding:20px 24px 12px; border-bottom:1px solid #222; background:#fff; }}
  h1 {{ margin:0 0 6px; font:700 22px Space Mono,ui-monospace,monospace; color:var(--red); }}
  .meta {{ max-width:90rem; }}
  nav {{ display:flex; flex-wrap:wrap; gap:8px 14px; margin-top:10px; }}
  nav a {{ color:#1565c0; font:700 13px ui-monospace,monospace; }}
  .card {{ background:#fff; margin:20px; padding:12px 12px 20px; border:1px solid #222; }}
  h2 {{ margin:0; font:700 18px Space Mono,ui-monospace,monospace; color:var(--red); }}
  .sub {{ margin:4px 0 12px; color:#333; }}
  svg {{ width:100%; height:auto; background:#fff; border:1px solid #ddd; }}
  @media print {{
    nav {{ display:none; }}
    .card {{ break-inside:avoid; margin:8px 0; }}
  }}
</style>
</head>
<body>
<header>
  <h1>K1-CORE-VAL-R0 · domain component wiring</h1>
  <p class="meta">Hub-correct successor to the dual-USB D01–D10 drawings. One Type-C
  (GT-USB-7005A), USB2422 US/DN1/DN2, no J7. Electrical identity from HOLD
  <code>55ed9ee948734a0e903f37744b51f3b8</code> plus PIN-CONTRACT / H0f-CLOSE.
  These drawings are the readable circuit grammar for G2.2. They are not an EasyEDA
  write and not <code>JLC-SCH-READY</code>.</p>
  <p class="meta">Scale: schematic symbols, not millimetres. Pin numbers from
  DS00001726B / H0f / NXP ball names. Old D01 USB4105 → RT data path is retired.</p>
  <nav>{nav}</nav>
</header>
{''.join(cards)}
</body>
</html>
"""


def main() -> None:
    OUT.write_text(html(), encoding="utf-8")
    print(f"wrote {OUT} bytes={OUT.stat().st_size}")


if __name__ == "__main__":
    main()
