---
contract: usb
status: RATIFIED
receptacle_count: 1
receptacles: [J1-PWR1]
third_receptacle: FORBIDDEN
second_receptacle: FORBIDDEN
hub: USB2422
hub_ports_non_removable: [DN1, DN2]
service_usb_owner: ESP32_S3
service_usb_path: USB2422_DN2
service_usb_connector: J1-PWR1
rt_usb_owner: RT1062
rt_usb_path: USB2422_DN1
rt_usb_controller: USB_OTG1
primary_power_inlet: J1-PWR1
j1_type_c_role: SINK
vbus_detect_source: 5V_USB
downstream_vbus_power_islands: FORBIDDEN
downstream_vbus_validity_switch: TPS2052B
ufp_powered_hub_wp: USB-IF_REV_0_9_NOT_CERT
s3_recovery_uart: J6-ESP
s3_usb_xor_header: DNP_OPTIONAL
usb_audio: EXPERIMENT_ONLY
usb_audio_termination: USB2422_DN1_RT1062
differential_impedance_ohm: 90
authority: D-049
j1_receptacle: GSWITCH_GT-USB-7005A
j1_selected_mpn: GSWITCH_GT-USB-7005A
j1_selected_lcsc: C5250872
j1_pin_family: USB_C_24P_USB2_SINK
superspeed_routing: FORBIDDEN
cc_protection: IEC_ESD_ONLY
---

# USB interface contract

One USB-C receptacle plus an embedded USB2422. No second receptacle. No third. D-049
(`RATIFIED` after H GREEN 2026-08-29).

| Path | Owner | Carries | Powers the board |
| --- | --- | --- | --- |
| `J1-PWR1` | Type-C sink + hub upstream | Primary 5 V inlet, CC policy, USB2 D+/D− into USB2422 US | Yes |
| USB2422 DN1 | RT1062 | HS device on USB OTG1, non-removable | No — local rails stay `5V_SYS` / 3V3 |
| USB2422 DN2 | ESP32_S3 | FS native USB (GPIO20/19), non-removable | No — local rails stay `5V_SYS` / 3V3 |

Every USB statement in this repository names its path. "USB" without a receptacle or hub
port is not authority. `J7-ESP` does not exist on this contract. S3 service USB is hub
DN2, seen by the host through `J1-PWR1`.

This is **not** the tombstoned idea of a single USB owned by ESP32-S3 with RT1062 data
only across K1BR. Both processors remain USB devices.

## `J1-PWR1` — power inlet, Type-C sink, hub upstream

J1 is the only USB-C and the primary 5 V inlet for the whole board. USB2 data on J1 is
**hub upstream**, not a termination on RT1062.

D+/D− leave the receptacle through connector-class ESD onto `USB_DP_UP` / `USB_DM_UP`
and land on USB2422 upstream. They no longer terminate on RT USB OTG1.

J1 remains a Type-C **sink**: Rd 5.1 kΩ on CC1/CC2, current-advertisement sense, eFuse /
INA / throttle. The hub does **not** replace source-policy. The sink must stay inside
the CC advertisement (Default / 1.5 A / 3.0 A). A 5 A receptacle is headroom, not a
licence to draw 5 A from a non-PD source.

### 24-pin family contract (`USB_C_24P_USB2_SINK`)

This is a family contract, not a frozen EasyEDA cache part. MPN is
`GSWITCH_GT-USB-7005A` / `C5250872`, **bound** by D-050 geometric section
(STEP SMT datum, 0.280 mm bottom keepout, D-012 unchanged). TE `2129691-1` /
`C590834` is archived fallback only.

```text
A4/A9/B4/B9     → 5V_USB
A1/A12/B1/B12   → GND
SHELL / shield  → explicit GND or chassis strategy (D-050)
A6+B6           → low-C ESD → USB_DP_UP → USB2422 US
A7+B7           → low-C ESD → USB_DM_UP → USB2422 US
A5 / B5 CC1/CC2 → Rd + capability sense + CC-PROTECTION → throttle
SBU1 / SBU2     → NC
all SSTX/SSRX   → NC
```

USB2422 is USB 2.0. SuperSpeed routing is forbidden. Do not route SuperSpeed or SBU
"for later". `cc_protection` is `IEC_ESD_ONLY` (`CC-PROTECTION.md`).

Hub `VBUS_DET` is taken from actual inlet `5V_USB` through a high-Z divider. Tying
`VBUS_DET` to always-on `5V_SYS` or `3V3` is forbidden.

## USB2422 — embedded hub

Part family: Microchip USB2422 (industrial QFN-24 intended; LCSC confirmation is a
later procurement step). Strap mode. No EEPROM required. No external 1.2 V rail.
Internal 1.2 V / CRFILT / PLLFILT must not feed external circuitry. Integrated USB
terminations.

- DN1 = RT1062 USB OTG1, HS, non-removable.
- DN2 = ESP32-S3 GPIO20/19, FS, non-removable.
- `NON_REM[1:0] = 10` via strap **resistors** (sampled at reset). `11` is reserved.
- `CFG_SEL` low for strap mode. Default = self-powered.
- Connector-class ESD and the 5 pF budget sit on the **upstream** pair only.
- 3V3 budget includes USB2422 IHCH2: 70 mA typical / 89 mA max with an HS host and
  two downstream ports.

### VBUS validity — F6-B default, not two power islands

Conventional downstream USB **power islands** are forbidden. Neither TPS2052B output
powers RT1062 or ESP32-S3.

VAL-R0 default is **F6-B** (TPS2052B) as a VBUS-**validity** switch:

- OUT1 feeds `USB_OTG1_VBUS` (tens of milliamps, not a core rail).
- OUT2 feeds only the S3 VBUS-monitor divider.
- IN = `F6_VALIDITY_SOURCE` = `5V0_USB_VALID` (U22-USB TPS7A2550DRVR /
  C2876265 from `5V_USB`). Do not default IN to `5V_PROTECTED` while eFuse
  OVLO is near 6 V and NXP `USB_OTG1_VBUS` absolute maximum is 5.50 V.
- PRTPWR / OCS may assist. They are **not** the host-unplug kill.
  `VBUS_DET` falling does **not** guarantee `PRTPWR` falling. An independent
  `5V_USB`-presence kill is mandatory.

F6-A (omit the switch) is the later shave path only.

`NON_REM` changes descriptors. It does not remove the need for a VBUS circuit and
is not the self-powered / embedded-device argument.

### USB2422 errata Anomaly 3 — named hold

Single-TT: if a high-speed split to one full-speed downstream port exceeds
288 bytes/µframe, the transaction translator can corrupt when another HS packet
arrives before the FS packets finish. No workaround. No future silicon. K1 has
one FS device (S3) **and** one HS device (RT). Concurrent RT HS — especially
isochronous USB audio — plus S3 FS is the hold. USB audio stays
`EXPERIMENT_ONLY`. Do not close this because "there is only one FS device".

USB-IF *Upstream Facing Port Powered Hub* white paper Rev 0.9 is recorded as
`USB-IF_REV_0_9_NOT_CERT`. It is not a certification basis.

## RT1062 behind the hub

OTG1 D+ / D− come from hub DN1 (`USB_DP_DN1` / `USB_DM_DN1`).

`USB_OTG1_VBUS` is a real 5 V analogue pin. IMXRT1060IEC: 4.40–5.50 V recommended,
absolute maximum 5.50 V, **25 mA typical per active USB interface / 50 mA** in the
same table, 1 µF to GND, no divider. A high-impedance GPIO divider cannot feed it.

Source is F6-B OUT1 (`RT_USB_VBUS`) under the VAL default. MCU-side PWR/OC pins on
RT1062 are unused for this path.

RT SWD and boot recovery stay reachable **without** the hub. USB-HID / serial
downloader through USB2422 is an engineering inference, not the brick path, and
not an NXP guarantee.

OTG2 stays unused.

## J7 does not exist

`J7-ESP` is deleted from this contract. There is no second Type-C, no second
connector ESD island, and no second CC / VBUS eFuse. ESP32-S3 service USB is
USB2422 DN2. The host sees S3 through `J1-PWR1`.

S3 recovery that must survive a dead or misconfigured hub is `J6-ESP`
(UART0 + EN + GPIO0 + 3V3 + GND). Optional 0 Ω XOR pads may offer a DNP USB
recovery header, mutually exclusive with DN2. True XOR only: never fit both
paths. Default is hub FIT, header DNP.

## K1BR is unchanged

K1BR remains command, state and telemetry only. It does not carry raw PCM,
features or pixels. Nothing in D-049 relaxes that boundary.

## USB audio

Experimental. Not a baseline R0 requirement.

USB audio terminates on USB2422 DN1 into RT1062 USB OTG1. It does not cross
K1BR. The earlier "direct J1 or a named K1BR exception" branch is closed by
giving RT1062 an external USB path **through the hub**, not by inventing a
bridge exception.

**Open risk R1 stands.** A USB device stack and its interrupts still sit in the
same real-time domain as capture, Audio Processing and render.

**Anomaly 3 stands.** Isochronous USB audio behind this Single-TT hub is not
proven. Characterise before claiming it works.

## Routing

90 ohm differential on **three** pairs: hub UP, DN1 and DN2. Equal-length
parallel routing over continuous reference ground, minimum layer transitions,
paired return vias where a transition is unavoidable. Keep USB activity away
from the 2.4 GHz antenna region.

Connector-class ESD only on the upstream pair. Internal DN1 / DN2 pairs do not
get a second connector TVS.

J1 still carries the full board inlet current on the same connector as the
upstream pair. Power-corridor geometry and the data pair are separate problems
on one part.

S3 PHY series TUNE (`RUSB_S3_DP_TUNE` / `RUSB_S3_DM_TUNE`, initial 22 Ω or
33 Ω) sits at GPIO20/19. XOR 0 Ω is path select only and is not a substitute
for TUNE.

## Recovery

- `J6-ESP` is mandatory. A dead hub must not brick S3.
- XOR USB header is optional and DNP by default. Mutually exclusive with DN2.
- No CP2102, CH340 or FTDI is added.
- RT SWD / boot pads stay independent of the hub.
