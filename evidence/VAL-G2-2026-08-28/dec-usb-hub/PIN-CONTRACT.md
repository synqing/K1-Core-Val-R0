# PIN-CONTRACT

Mutations that are not in this file are forbidden. Designators from `CENSUS.md`
reserved list (U20-USB / U21-USB / Y3-USB / R77-USB… / C100-USB…). Pin
numbers from `USB2422-PIN-EXTRACT.md`.

```text
EXECUTABLE = after H GREEN
D050_BOUND = GT-USB-7005A / C5250872
F6 = F6-B
F2 = F2-C
KILL = KILL-B
```

## G1 — nets

Keep: `5V_USB`, `5V_PROTECTED`, `5V_SYS`, `3V3`, `GND`, `USB_CC1`, `USB_CC2`
(J1-only after T21), existing eFuse / INA / throttle / CC-sense names.

Add:

| Net | Role |
| --- | --- |
| `USB_DP_UP` / `USB_DM_UP` | J1 after ESD → hub US (today `USB_DP_PROT` / `USB_DN_PROT` far side) |
| `USB_VBUS_DET` | hub detect tap |
| `USB_DP_DN1` / `USB_DM_DN1` | hub → RT OTG1 (replace `USB_DP_RT` / `USB_DN_RT`) |
| `USB_DP_DN2` / `USB_DM_DN2` | hub → S3 TUNE (replace `USB_DP_S3` / `USB_DM_S3` at the PHY) |
| `USB_REC_DP` / `USB_REC_DM` | XOR header only |
| `RT_USB_VBUS` | F6-B OUT1 |
| `S3_USB_VBUS_VALID` | F6-B OUT2 |
| `USB_PRTPWR1` / `USB_PRTPWR2` | hub → KILL-B AND |
| `USB_OCS1_N` / `USB_OCS2_N` | TPS2052B OC → hub |
| `USB_5V_VALID` | KILL-B comparator output (TLV7031) → GPIO15 and AND |
| `5V0_USB_VALID` | `F6_VALIDITY_SOURCE` — TPS7A2550DRVR OUT |
| `USB_EN1` / `USB_EN2` | U24/U25 Y → U21 EN1/EN2 |
| `TAP_VBUS` / `TAP_REF` | KILL-B divider taps |

Retire after T22 (zero members): `S3_VBUS`, `USB_DP`, `USB_DM`, `USB_DP_ESD`,
`USB_DM_ESD`. Rename `USB_DP_S3`/`USB_DM_S3` in place to DN2 **or** replace;
do not mix. `OPT_USB_AUD` stays a VAL strap — not OTG1.

## G2 — `U20-USB` USB2422 every pin

Census reserved block. Sequential next-free is U18; U18/U19 stay spare.

Pin numbers from `USB2422-PIN-EXTRACT.md` (DS00001726B). DN1 is pins **4/3**, not 3/2. DN2 is pins **5/2**.

| Pin | Symbol | Connect |
| --- | --- | --- |
| 1, 9, 18 | VDD33 | `3V3` + local 100 nF (pin 1), 1 µF (pin 9), 100 nF (pin 18) |
| ePad | VSS | GND, multiple vias |
| 20 | USBDP_UP | `USB_DP_UP` |
| 19 | USBDM_UP | `USB_DM_UP` |
| 4 | USBDP_DN1 | `USB_DP_DN1` |
| 3 | USBDM_DN1 | `USB_DM_DN1` |
| 5 | USBDP_DN2 | `USB_DP_DN2` |
| 2 | USBDM_DN2 | `USB_DM_DN2` |
| 16 | VBUS_DET | `USB_VBUS_DET` |
| 24 | RBIAS | `R77-USB` 12 kΩ ±1% to GND |
| 10 | CRFILT | `C100-USB` 1 µF to GND |
| 23 | PLLFILT | `C101-USB` 0.1 µF to GND |
| 22 / 21 | XTALIN / XTALOUT | `Y3-USB` 24 MHz + `C102-USB` / `C103-USB` from D11 |
| 15 | RESET_N | RC to 3V3; **not** floating |
| 14 | CFG_SEL | strap **low** (resistor to GND) |
| 13 | NON_REM1 | strap **high** (NON_REM[1:0] = **10**) |
| 17 | NON_REM0 / SUSP_IND | strap **low** at reset; after reset is SUSP_IND. Do not tie to VDD33. No SMBus / LOCAL_PWR. |
| 7 | PRTPWR1 / BC_EN1 | **Same pin.** At RESET_N negation: leave IPD (no pull-up) so BC_EN1 is off. After reset: output `USB_PRTPWR1` into KILL-B AND. |
| 11 | PRTPWR2 | `USB_PRTPWR2` into KILL-B AND |
| 8 / 12 | OCS1_N / OCS2_N | `USB_OCS1_N` / `USB_OCS2_N` |
| 6 | NC | NC flag |

## G3 — J1 retarget

Electrical contract is D050-4. **D-050 BOUND** on GT-USB-7005A / C5250872.
T00 uses `J1-GT-USB-7005A-FOOTPRINT-REBUILD.md`, never the EasyEDA cache.

Keep `D1-PWR1` USBLC6 (census: data ESD, not rail TVS). Far side of
`RUSB_DP-PWR1` / `RUSB_DN-PWR1` → `USB_DP_UP` / `USB_DM_UP` (default 0 Ω).
J1 CC stays J1 Rd + sense. J7 Rd removed. SBU/SS NC. Shell tabs per D050-4.
If D-050 later binds GT-USB-7005A, T00 replaces the symbol from an
independently rebuilt library part — never the EasyEDA cache.

## G3b — inlet capacitance (H12)

Derived from census E1.8, not instinct. See `VBUS-CONTRACT.md` F4b.

- C1-PWR1: **RETARGET** 22 µF → 1.0 µF on `5V_USB` (this **is** U22 CIN).
- C2-PWR1: **KEEP** 22 µF on `5V_PROTECTED`.
- C120-USB: **ADD** 22 µF on `5V_PROTECTED`.
- C121-USB: **ADD** 100 nF at U22 IN (HF only — not a second 1 µF).
- C122-USB: **ADD** 2.2 µF on `5V0_USB_VALID`.
- R80-USB: **ADD** 4.7 kΩ F8 bleeder on `5V_USB`.
- Do not move C2 onto the raw node. Do not leave 22 µF on `5V_USB`.
- Do not add a second microfarad on `5V_USB`.

## G4 — RT

- L8 ← `USB_DP_DN1`
- M8 ← `USB_DM_DN1` (not M6; census stray stub)
- N6 ← `RT_USB_VBUS` + `CUSBVBUS-RTC` retargeted (T12). No divider. 50 mA capable.
- N12 NC
- No series R on DN1 unless NXP HDG is cited (none)
- SWD / boot independent of the hub

## G4b — `U21-USB` TPS2052B every pin

Census reserved block. Do not use U19.

| Pin | Name | Connect |
| --- | --- | --- |
| 1 | GND | GND |
| 2 | IN | `5V0_USB_VALID` (`F6_VALIDITY_SOURCE`; do not default `5V_PROTECTED`) |
| 3 | EN1 | `USB_EN1` = U24.Y (PRTPWR1 AND `USB_5V_VALID`) |
| 4 | EN2 | `USB_EN2` = U25.Y (PRTPWR2 AND `USB_5V_VALID`) |
| 5 | OC2 | `USB_OCS2_N` (open-drain; hub pull-up) |
| 6 | OUT2 | `S3_USB_VBUS_VALID` + R87 10 kΩ bleeder. **Not** GPIO15 |
| 7 | OUT1 | `RT_USB_VBUS` + `CUSBVBUS-RTC` 1 µF + R86 4.7 kΩ |
| 8 | OC1 | `USB_OCS1_N` |

MPN **TPS2052BDR / C130049**, SOIC-8, EN **active-high**. Do not gang
channels. Do not power MCU cores from OUT1/OUT2.

KILL-B parts (named; `H0f-CLOSE.md`):

- U23-USB TLV7031DBVR / C2869832 — comparator on `3V3`, sense `5V_USB`
- U24-USB / U25-USB SN74LVC1G08DBVR / C7666 — EN1/EN2 AND
- U22-USB TPS7A2550DRVR / C2876265 — LDO; C1 is CIN; C121 100 nF HF; C122 2.2 µF COUT
- D3-USB SMF5.0A / C2758488 — new inlet TVS (do not revive DVBUS-PWR1)
- D4-USB BAT54 — DNP; never in series with IN

## G4c — `U22-USB` TPS7A2550DRVR every pin (fixed DRV, not adjustable)

| Pin | Name | Connect |
| --- | --- | --- |
| 1 | OUT | `5V0_USB_VALID` = U21.2 |
| 2 | NC | GND (fixed die; **not** NR/SS, **not** FB) |
| 3 | PG | NC (false-low in dropout at 4.75 V; not KILL-B) |
| 4 | EN | `5V_USB` (tied to IN; do not float) |
| 5 | GND | GND |
| 6 | IN | `5V_USB` (no series diode — Vf eats dropout) |
| EP | thermal | GND, vias |

## G4d — KILL-B comparator / AND

| Ref | Pin | Connect |
| --- | --- | --- |
| U23.3 IN+ | `TAP_VBUS` | R81 169 kΩ / R82 100 kΩ from `5V_USB` (k = 0.3717, VTH nom 4.439 V) |
| U23.4 IN− | `TAP_REF` | R83/R84 100 k / 100 k from `3V3` → 1.65 V |
| U23.1 OUT | `USB_5V_VALID` | → R85 470 Ω → U9.8 GPIO15, and U24.3 / U25.3 |
| U23.5 / U23.2 | `3V3` / GND | C123 100 nF |
| U24.1 / U24.3 | A / B | `USB_PRTPWR1`, `USB_5V_VALID` → U24.4 `USB_EN1` |
| U25.1 / U25.3 | A / B | `USB_PRTPWR2`, `USB_5V_VALID` → U25.4 `USB_EN2` |

## G5 — S3

Hub DN2 → XOR 0 Ω (path select) → `RUSB_S3_DP_TUNE` / `RUSB_S3_DM_TUNE`
(22 Ω or 33 Ω initial) at GPIO20/19. Optional DNP `CUSB_S3_DP_TUNE` /
`CUSB_S3_DM_TUNE`. GPIO15 ← **`USB_5V_VALID`** via R85 470 Ω (H0f Clock 1).
Do not sense OUT2 for the 3 ms pin. Delete J7 island (census list). Do not
reuse R73/R74 as TUNE.

## G6 — XOR (default)

`R94-USB` 0 Ω FIT hub DN2; `R95-USB` 0 Ω DNP to `J12-USB` 4-pad header
(not USB-C). Never fit both. Do **not** use R85/R86 — those are H0f
GPIO15 series (470 Ω) and RT bleeder (4.7 kΩ).

## G7 — J6

Census six-pin map. **Action: none.**

## G8 — BOM delta (provisional)

Add: USB2422T-I/MJ C622610; 24 MHz + load caps; 12 kΩ 1%; CRFILT/PLLFILT/VDD33
caps; RESET RC; R78/R79 100 kΩ VBUS_DET; NON_REM/CFG_SEL/BC_EN straps;
`R80-USB` 4.7 kΩ F8 bleeder; `C120-USB` 22 µF on `5V_PROTECTED`; TPS2052B
C130049 + TI caps; U22-USB TPS7A2550DRVR / C2876265 + C1-as-CIN + C121 100 nF
+ C122 2.2 µF; U23-USB TLV7031DBVR / C2869832 + R81 169 kΩ + R82–R84 + R85
470 Ω; U24/U25 SN74LVC1G08DBVR / C7666 + C123–C125; R86 4.7 kΩ on
`RT_USB_VBUS`; R87 10 kΩ on OUT2; D3-USB SMF5.0A; D4-USB BAT54 DNP;
optional 2× 0 Ω + `J12-USB`; S3 TUNE 22/33 Ω + optional DNP shunts. J1
GT-USB-7005A / C5250872 **bound**. CC-PROTECTION: IEC ESD only (no IC).
Netlist: `H0f-CLOSE.md`.

Inlet C (from `VBUS-CONTRACT.md` F4b, against `CENSUS.md`):

| Designator | Action |
| --- | --- |
| C1-PWR1 | **RETARGET value** 22 µF → **1.0 µF**, keep on `5V_USB` (U22 CIN) |
| C2-PWR1 | **KEEP** 22 µF on `5V_PROTECTED` |
| C120-USB | **ADD** 22 µF on `5V_PROTECTED` (relocated raw energy) |
| C121-USB | **ADD** 100 nF at U22 IN (not 1 µF) |
| C122-USB | **ADD** 2.2 µF on `5V0_USB_VALID` |
| R80-USB | **ADD** 4.7 kΩ bleeder `5V_USB`–GND |
| DVBUS-PWR1 | **DELETE** from placed island (already census DELETE) |

Delete: census E2 list. Do not delete J1. Do not keep SuperSpeed nets.

A stranger can execute T00–T24 from this file. T00 uses
`J1-GT-USB-7005A-FOOTPRINT-REBUILD.md`, never the EasyEDA cache.
