# Source register

```text
SSCM1_RECOVERY_STATE = COMPLETE_NOT_FOUND
SSCM1_V1_AUTHORITY = UNRECOVERED_UNFROZEN
SSCM1_V2 = REQUIREMENTS_DRIVEN_REPLACEMENT
```

## Vendor and primary

| Organisation | Source | Used for |
| --- | --- | --- |
| NXP | i.MX RT1060 datasheet, IMXRT1060CEC | Three SAI modules; no MICFIL or PDM decimation peripheral; two USB 2.0 OTG controllers with integrated PHY |
| Texas Instruments | TLV320ADC6120 datasheet and product page | 113 dB fixed / 123 dB DRE; TDM/I2S/LJ; master or slave; PDM inputs |
| Texas Instruments | ADC6120EVM-PDK user's guide, SBAU359 | External ASI mode via J7; external PDM access |
| Texas Instruments | TPS62913 datasheet, SLUSEA4 | PG is open-drain and requires an external pull-up when used; NR/SS requires a soft-start capacitor to GND; low-noise/low-ripple buck used for the 3V3 rail. Basis for D-045 (`R75-PWR2` 10k `BUCK_PG`→`3V3`; `C10-PWR2` 100 nF `BUCK_SS`→GND) |
| STMicroelectronics | ST25R3916B datasheet | I2C_EN high selects the I2C host interface and floating is not a valid strap; `VDD_A`, `VDD_D`, `VDD_RF`, `VDD_AM`, `VDD_DR` and `AGDC` are internal-regulator OUTPUTS and must not be driven from `NFC_5V` or `3V3`; 27.12 MHz crystal. Basis for D-046 and D-047 |
| STMicroelectronics | STEVAL-ST25R3916B reference design | 2.2 µF GRM155R60J225ME15D on each internal-regulator rail to GND; reference topology for the K1 NFC decoupling row `C92-NFC`…`C97-NFC`. Basis for D-047 |
| Espressif | ESP32-S3 hardware design guidelines | Antenna at edge or carrier cut-away; clearance; 90 ohm USB differential |
| Espressif | ESP32-S3 PCB layout design guidelines, https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html | Three antenna-placement arrangements — antenna overhanging the board perimeter, edge-connected notch, fully internal cavity; keep USB and other high-speed traces physically away from the antenna region; the 15 mm figure is an END-PRODUCT antenna clearance recommendation, not a PCB keepout rectangle. Study input for `architecture/G3-FLOORPLAN-DOCTRINE.md`; see the 2026-08-28 keepout tombstone in `authority/05-SUPERSESSIONS.md` |
| STMicroelectronics | AN5240, ST25R391x layout | Continuous ground under matching; short symmetric RFO/RFI; no vias in matching path |
| JLCPCB | Controlled-impedance stack-up catalogue | JLC06161H-3313 construction |
| JLCPCB | Current general PCB capability table | Headline BGA, local multilayer spacing and filled/plated-over via-in-pad capability; not K1 design rules |
| JLCPCB | BGA Design Guidelines, updated 2025-12-27 | BGA-specific conventional and filled-through-via guidance to reconcile with NXP and assembly requirements at VAL-G3 |
| EasyEDA | Pro user guide, schematic settings | No schematic area limit; recommends fewer than 100 components per page |
| Nabu Casa | Home Assistant Voice PE released KiCad (`home-assistant-voice-pe`), CERN-OHL-P v2 | Patterns-only specimen: optionality, observability, EVT→release regulator swap. Not a K1 parts list. v1.0 PDF power tree (SY80004/ETA3410) is stale versus released KiCad. See `docs/agent/VOICE-PE-SPECIMEN-VAL-R0.md`. |

## Internal

| Repository | Used for | Status |
| --- | --- | --- |
| SpectraSynq-K1-DualMCU-Firmware | Processor ownership, K1BR contract, forbidden payloads and SSCM-1 authority check | Read at commit 4e985c6; no recovered SSCM-1 interface authority |
| K1.hardware | SSCM-1 recovery attempt | Historical K1-M2B/module fragments and placeholder mapping found; frozen SSCM-1 v1 specification not found |
| SpectraSynq-Instrument-Spine | SSCM-1 recovery attempt | Prior search not reproducible in current review because checkout was unavailable |
| EasyEDA disposable `K1-Core-Val-R0-G2.1-BULK-CANDIDATE` (`dcd7e3cab2a24b9aa6e531d2b62e1b6f`) | G2.1 electrical reference / EasyEDA normalisation oracle (D-048) | IMPORTED_NOT_CANONICAL; import receipt NOT YET ACCEPTED; not product canonical; not JLCPCB handoff |
| K1-AUDIO-EVAL-R0 complete design-input package (33 files; `K1-AUDIO-EVAL-R0_COMPLETE_PACKAGE.zip`) | Source authority for dual-input audio: switched stereo 3.5 mm TRS, laboratory XOR, IM69D130 through TLV320ADC6120, 48 kHz four-slot TDM, ADC/direct PDM XOR. Failed to migrate the analogue lane into the VAL-R0 mainboard contract until D-051. | READ 2026-08-30 from the package on disk. Daughterboard FPC / ESP32 direct-PDM / EVAL GPIO map are **not** copied. Direct-PDM on VAL-R0 terminates at RT1062. Jack MPN remains candidate (`PJ-3537S-SMT` / `C2689709`), not bound. |

## Unresolved

```text
OPTION_C_SYMBOL_ESTIMATE = RESOLVED
VAL_G2_0_FIXTURE_DEFINITION = RETIRED_BY_D_042
VAL_G2_0_EDA_EXECUTION = TERMINATED_BY_D_042
```

Corrected 2026-08-28: `N_estimated_symbols_option_C = 181` baseline symbols counted from
the Option-C power tree, frozen RT1062 package, ESP32-S3 module support, ratified contracts and
the vendor support circuits they require. The retained stress plan contains 218 symbols and 119
named nets after the non-existent ADC strap was removed; it does not meet the historical 120-net
threshold. See `schematic/single-sheet-qualification/FIXTURE-PLAN.json`.
D-042 terminated live qualification-project actuation. Canonical actuation is controlled by its
separate mutation state file and append-only ledger. Static source-register prose is not a runtime
write permit.

Voice PE (D-043) is patterns-only. It does not change these qualification tokens or the 181
baseline count. See `docs/agent/VOICE-PE-SPECIMEN-VAL-R0.md` and
`evidence/VAL-G2-2026-08-28/CURRENT-STATE-RECEIPT.md`.

- Current shipping ESP32-S3 headroom. Never measured post int64-GDFT promotion.

## Closed absence

- SSCM-1 v1.0 interface specification: bounded recovery complete, not found. Historical fragments
  are not the missing contract. No further recovery action is authorised while Option B is
  deferred.
