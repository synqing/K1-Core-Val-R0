# Domains of concern

## Physical and electrical

| ID | Domain |
| --- | --- |
| D01 | Compute and memory |
| D02 | 2.4 GHz RF |
| D03 | Power entry and protection |
| D04 | Power conversion and distribution |
| D05 | Power measurement and supervision |
| D06 | LED power, data and thermal feedback |
| D07 | Audio electronics |
| D08 | Acoustics and microphone mechanics |
| D09 | NFC and 13.56 MHz RF |
| D10 | Motion and inertial |
| D11 | USB data |
| D12 | Interconnect, expansion and service |
| D13 | Instrumentation and validation |

## Cross-cutting

| ID | Concern |
| --- | --- |
| D14 | Stack, ground, SI, PI and EMC |
| D15 | Thermal |
| D16 | Mechanical and enclosure |
| D17 | Manufacturing and DFM |
| D18 | Hardware to firmware contract |

D14 to D18 govern the other domains rather than occupying their own schematic rectangles.

## Effect of VAL-G1

Under Option B, D01 physically leaves the Core and roughly half of its relationships become
connector-crossing constraints rather than placement constraints. The domain-interaction matrix
therefore cannot be authored as a single Core authority until VAL-G1 closes. Conditional entries
live in `authority/02-Q0-B-vs-C.md` in the meantime.
