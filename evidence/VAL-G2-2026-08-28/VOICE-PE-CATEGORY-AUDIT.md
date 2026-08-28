# Voice PE category audit vs current K1

Date: 2026-08-28. Categories only. No Voice PE MPNs. No authority edits in this file.

Sources: ratified K1 contracts and architecture; retired
`schematic/single-sheet-qualification/FIXTURE-PLAN.json` (181/218, `RETIRED_BY_D_042`);
live canonical census in `voice-pe-live-census.json` (222 component primitives, 141 unique NET attrs).

| Category | Retired fixture plan | Live canonical sheet | K1 contract | Verdict |
| --- | --- | --- | --- | --- |
| Main ICs | RT1062, ESP32-S3, ADC6120, NFC, IMU present | PWR/RTC/ESP/AUD/NFC/MOT/LED suffixes present | ownership matrix | **PRESENT** |
| Complete decoupling | RT_* bulk/HF, S3 3V3, ADC rails, NFC VSP | many C* in RTC/PWR/ESP | vendor support expected | **PARTIAL** — live sheet exists; this audit does not claim pin-complete decoupling |
| Reset / boot | `manual_reset`, `boot_mode0/1`, `s3_boot`, `s3_en`, POR parts | RTDBG / ESP / VAL tags | debug-fabric.md | **PRESENT** |
| Clocks | RT xtal, NFC xtal, audio MCLK/BCLK/FSYNC iso | AUD + RTC | clock + audio contracts | **PRESENT** |
| Flash | `qspi_flash` + VCC/WP/bulk | RTC suffix includes flash-class parts in plan | NXP boot | **PRESENT** in retired plan |
| ESD | `usb_tvs`, `usb_esd` | USB in ESP/PWR | usb-interface 90 Ω + ESD | **PARTIAL** — USB ESD present; no extra ESD invented for PDM/flex |
| Rail filtering / switches | USB eFuse, LED eFuse, MIC LDO + FET, NFC bead | PWR1/PWR2 | power architecture | **PRESENT** |
| Fault / power-good / measurement | INA226 + alert; `pwr_valid*` | INA in PWR1 | power tree | **PRESENT** |
| 0R / DNP isolation already required by K1 | PDM XOR R38–R41; motion R44–R49; clock iso R34–R36 | AUD/MOT tags | mic + motion + audio | **PRESENT** — already K1, not Voice PE cargo-cult |
| DNP tuning | 7 DNP values in retired plan | not re-enumerated here | option states | **PARTIAL** |
| Test access | 6 dedicated TPs (K1BR SCK/CS, MCLK, PDM CLK/DAT, option) | 8 TPs (ESP/AUD/VAL) | debug fabric + this doctrine | **PARTIAL** — see test-access census |
| Debug / recovery | SWD header, UART header, S3 UART0, SDL path | RTDBG | debug-fabric.md | **PRESENT** |
| Connector conditioning | USB CC, ferrite, LED XH, mic flex | J* count 11 live | contracts | **PRESENT** |
| Shield bonds | none | none named `USB_SHIELD` in live unique nets | USB contract has no shell menu | **ABSENT** — candidate only |
| Option-selection | R55–R58, J11 | VAL=14 | single-sheet states | **PARTIAL** |
| Source-termination footprints | K1BR series, LED 33R, audio series, SWD/UART series | series parts exist | K1BR ohms **TUNE** | **PARTIAL** — footprints representative, values not frozen |
| LED eFuse bypass | none | none | power tree has eFuse, no bypass | **ABSENT** — capability OPEN, no symbol |
| Stress-only extras | 37 `stress_rail_load` | not used as estimate drivers | qualification floors | **PRESENT** (stress, not baseline) |

## K1-native gaps this audit does **not** invent

If later canonical review finds missing reset support, pin-local decoupling, ESD, oscillator
load, boot flash, or power-good from **NXP / TI / Espressif / ST** references, the Option-C
estimate must move. That change would be source-derived K1 work, not a Voice PE count.

No missing K1-native support circuit is asserted here without a pin-level vendor check of the
live 222-symbol sheet. That check is VAL-G2.1 work, not this specimen lane.
