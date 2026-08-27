---
contract: microphone
status: RATIFIED
part: IM69D130
power_enable_owner: RT1062
pdm_clock_hz: 3072000
---

# Microphone interface contract

IM69D130 on a flex interface. `MIC_PWR_EN` and the switched `3V3_MIC` rail belong with the
capture owner, RT1062, because enable sequencing and capture are one concern.

PDM clock target is 3.072 MHz, matching the established IM69D130 operating point and the
48 kHz output family.

Two population routes exist and are mutually exclusive. A 0R / DNP matrix enforces the XOR so
both routes can never load the PDM bus simultaneously. The chosen route is recorded on the
single schematic sheet beside the circuit, not in a separate document.
