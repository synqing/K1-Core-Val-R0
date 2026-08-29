# DEC-USB-HUB mutation campaign — T16 through T24

Write target: disposable hub `K1-Core-Val-R0-G2.1-HUB-CANDIDATE`
`41c8e6523576456582ea35958b3684ed`, page `1435cb46f39e48c8a8aadbb84ca81603`.
Live `64325d0e` was never focused. PCB `59bef7e87cff4cd580561703b62d8c19`
was never converted. J6-ESP six pins were not touched. T14 / T15 / T23a
were skipped as ordered.

Gate: `hub-lane/MUTATION-STATE.json`. Last closed
`T24-save-hygiene-2026-08-29`. State **READY**. Hash after close
`2975845:437afeab`.

## What happened

The remaining USB-C service island was lifted, then deleted, then the
leftover nets were cleared. GPIO15 stays on `USB_5V_VALID` only. J1
SuperSpeed and SBU, hub pin 6, and RT CHD_B / OTG2 now carry NC flags.
No SuperSpeed net names were added.

## Closed this run

| ID | Stage | After hash | Result |
| --- | --- | --- | --- |
| T16 | wire | `3066999:d2e7ec2e` (then restamp) | R85 470 Ω `USB_5V_VALID` → U9.8 only. Already closed before this stretch. |
| T17 | wire | `3056663:1318895e` | J7 island lifted off CC / DP / DM / `S3_VBUS`. J1 CC kept. |
| T18 | delete | `3047588:59f64829` | J7-ESP gone. J1 present. |
| T19 | delete | `3025378:38e0e9f2` | U10, C43, C44 gone. |
| T20 | delete | `2995560:b8c45ae1` | R73, R74, R71, R72 gone. TUNE pair kept. |
| T21 | delete | `2978756:b64f6915` | R21, R22 gone. `USB_CC1` / `USB_CC2` = J1 `ebrw*` only. |
| T22 | delete | `2969526:dbba3ddd` | J7-only nets empty. DVBUS-PWR1 gone. `S3_VBUS` zero members. PHY `USB_DP_S3` / `USB_DM_S3` kept. |
| T23 | text | `2975845:be7827b8` | J1 SBU + SuperSpeed NC. Hub pin 6 NC. U6 N12 / N7 / P6 / P7 NC. No frames. |
| T24 | text | `2975845:437afeab` | Saved. One sheet. J6 six pins still GND / 3V3 / UART / EN / GPIO0. Waiver copy without J7 SBU: `DRC-WAIVERS.json`. |

T10–T13c were not repeated.

## ERC

Independent ERC: `unclassified_fatals=0`, `real_defects_open=0`,
`hub_census_ok=True`. Graph:
`anchors/hub-electrical-graph.json`. Disposition:
`anchors/erc-disposition-hub.json`.

Host `sch_Drc.check` returned **14 fatal / 49 warn** with **no item text**.
The API only exposes `check()`. Those 14 host fatals are **not classified**.
The written `anchors/schDrcLog-hub.txt` records that gap as Info so the
oracle 9/19 placeholder injection does not run.

## What is true now

- J7 and its island parts are gone.
- J1 remains. CC nets are J1-side only.
- S3 USB is TUNE → GPIO20/19. GPIO15 is `USB_5V_VALID`.
- RT USB is DN1 + `RT_USB_VBUS` on N6.
- XOR R94 FIT / R95 DNP unchanged.
- Live product was not written.

## What is left

1. Official freeze was **retracted**. `TAP_VBUS` and `TAP_REF` share wire
   `e34ae57efe3e3790`, including `1460,1010–1580,1010` across U23 IN+/IN−.
   See `HUB-FREEZE-RECEIPT.md`.
2. T25: split those nets onto separate wires. Then re-ERC and freeze.
3. G2.2 from the new freeze. `JLC-SCH-READY` stays Captain-only.
