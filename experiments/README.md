# Experiments

Subdirectories are created when work actually begins, not in advance.

| Planned lane | Purpose | Gated on |
| --- | --- | --- |
| `audio/L0-SRC/` | Host-only 48 kHz sample-rate-conversion validation | nothing |
| `audio/L1-ADC6120-EVM/` | Converter characterisation on TI's AC-MB | EVM in hand |
| `audio/L2-RT1062-SAI/` | EVM external ASI into Teensy 4.1, raw 24/32-bit SAI and DMA | L1 |
| `audio/L3-K1-INTERFERENCE/` | Real K1 interference testing | Core geometry exists |
| `s3-baseline/` | Current post-GDFT ESP32-S3 performance reference | nothing |
| `val-g1-study/` | SSCM-1 recovery pass, then the B-vs-C escape-pressure study | nothing — this is what unblocks VAL-G1 |

L0, L1, L2 and the ESP32-S3 baseline are not gated on VAL-G1. None of them touch the Core.
