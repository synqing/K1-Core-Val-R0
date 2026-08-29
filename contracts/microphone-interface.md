---
contract: microphone
status: RATIFIED
part: IM69D130
power_enable_owner: RT1062
pdm_clock_hz: 3072000
pdm_route_population: XOR
pdm_adc_path: FIT_DEFAULT
pdm_direct_rt_path: DNP_ALTERNATE
authority: D-051
---

# Microphone interface contract

IM69D130 on a flex interface. `MIC_PWR_EN` and the switched `3V3_MIC` rail belong with the
capture owner, RT1062, because enable sequencing and capture are one concern.

PDM clock target is 3.072 MHz, matching the established IM69D130 operating point and the
48 kHz output family.

Two population routes exist and are mutually exclusive. A 0R / DNP matrix enforces the XOR so
both routes can never load the PDM bus simultaneously. The chosen route is recorded on the
single schematic sheet beside the circuit, not in a separate document.

That XOR is the **microphone-lane** implementation comparison (`MIC_ADC` versus `MIC_DIRECT`).
It is not “dual audio”. Dual-input architecture is the switched stereo 3.5 mm AUX lane plus
this PDM lane, through one TLV320ADC6120, as ratified in `contracts/audio-interface.md` and
D-051. The experimental direct-PDM branch terminates on RT1062, not ESP32-S3.
