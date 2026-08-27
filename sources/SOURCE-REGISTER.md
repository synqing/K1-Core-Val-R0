# Source register

## Vendor and primary

| Organisation | Source | Used for |
| --- | --- | --- |
| NXP | i.MX RT1060 datasheet, IMXRT1060CEC | Three SAI modules; no MICFIL or PDM decimation peripheral; two USB 2.0 OTG controllers with integrated PHY |
| Texas Instruments | TLV320ADC6120 datasheet and product page | 113 dB fixed / 123 dB DRE; TDM/I2S/LJ; master or slave; PDM inputs |
| Texas Instruments | ADC6120EVM-PDK user's guide, SBAU359 | External ASI mode via J7; external PDM access |
| Espressif | ESP32-S3 hardware design guidelines | Antenna at edge or carrier cut-away; clearance; 90 ohm USB differential |
| STMicroelectronics | AN5240, ST25R391x layout | Continuous ground under matching; short symmetric RFO/RFI; no vias in matching path |
| JLCPCB | Controlled-impedance stack-up catalogue | JLC06161H-3313 construction |
| EasyEDA | Pro user guide, schematic settings | No schematic area limit; recommends fewer than 100 components per page |

## Internal

| Repository | Used for | Status |
| --- | --- | --- |
| SpectraSynq-K1-DualMCU-Firmware | Processor ownership, K1BR contract, forbidden payloads | Read at commit 4e985c6 |
| K1.hardware | SSCM-1 recovery attempt | Searched, not found |
| SpectraSynq-Instrument-Spine | SSCM-1 recovery attempt | Searched, not found |

## Unresolved

- SSCM-1 v1.0 interface specification. One bounded recovery pass outstanding.
- Estimated Option C symbol count, required to size the single-sheet qualification fixture.
- Current shipping ESP32-S3 headroom. Never measured post int64-GDFT promotion.
