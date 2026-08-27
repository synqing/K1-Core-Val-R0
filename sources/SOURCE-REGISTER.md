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
| Espressif | ESP32-S3 hardware design guidelines | Antenna at edge or carrier cut-away; clearance; 90 ohm USB differential |
| STMicroelectronics | AN5240, ST25R391x layout | Continuous ground under matching; short symmetric RFO/RFI; no vias in matching path |
| JLCPCB | Controlled-impedance stack-up catalogue | JLC06161H-3313 construction |
| JLCPCB | Current general PCB capability table | Headline BGA, local multilayer spacing and filled/plated-over via-in-pad capability; not K1 design rules |
| JLCPCB | BGA Design Guidelines, updated 2025-12-27 | BGA-specific conventional and filled-through-via guidance to reconcile with NXP and assembly requirements at VAL-G3 |
| EasyEDA | Pro user guide, schematic settings | No schematic area limit; recommends fewer than 100 components per page |

## Internal

| Repository | Used for | Status |
| --- | --- | --- |
| SpectraSynq-K1-DualMCU-Firmware | Processor ownership, K1BR contract, forbidden payloads and SSCM-1 authority check | Read at commit 4e985c6; no recovered SSCM-1 interface authority |
| K1.hardware | SSCM-1 recovery attempt | Historical K1-M2B/module fragments and placeholder mapping found; frozen SSCM-1 v1 specification not found |
| SpectraSynq-Instrument-Spine | SSCM-1 recovery attempt | Prior search not reproducible in current review because checkout was unavailable |

## Unresolved

```text
OPTION_C_SYMBOL_ESTIMATE = UNRESOLVED
VAL_G2_0_FIXTURE_DEFINITION = REQUIRED_NOT_COMPLETE
VAL_G2_0_EDA_EXECUTION = BLOCKED_ON_FIXTURE_DEFINITION
```

The Option-C estimate is a hard input to VAL-G2.0A fixture definition. The 200-symbol floor may
not be substituted for an unknown estimate.

- Current shipping ESP32-S3 headroom. Never measured post int64-GDFT promotion.

## Closed absence

- SSCM-1 v1.0 interface specification: bounded recovery complete, not found. Historical fragments
  are not the missing contract. No further recovery action is authorised while Option B is
  deferred.
