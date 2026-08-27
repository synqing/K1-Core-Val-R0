# Validation architecture

## Gates

| Gate | Purpose |
| --- | --- |
| VAL-G0 | Project bootstrap and authority |
| VAL-G1 | Option B versus Option C close |
| VAL-G2 | Single-sheet native schematic |
| VAL-G3 | Mechanical envelope and domain floorplan |
| VAL-G4 | Real component placement and locks |
| VAL-G5 | Layer stack, net rules, planes, SI and PI |
| VAL-G6 | Routing and DRC |
| VAL-G7 | Fabrication-output proof |
| VAL-G8 | Silicon bring-up and validation |

## Independent audio programme

These lanes do not touch the Core and are not gated on VAL-G1.

**L0 — software only.** Golden 48 kHz PCM through candidate sample-rate conversion into
12.8 kHz / 96, and into 24 kHz / 180 where that alternative stays live. Measure passband,
stopband, alias rejection, impulse response, phase, group delay, cost, descriptor output and
beat and onset behaviour. No silicon.

**L1 — ADC6120EVM-PDK on its own AC-MB.** Characterise the converter alone: DRE off and on,
fixed gain, silence floor, fades, threshold-hovering tones, impulses, clipping, stereo line,
and IM69D130 through ADC decimation. Isolates converter behaviour from firmware behaviour.

**L2 — EVM external ASI into Teensy 4.1.** Raw RT1062 SAI and DMA at 48 kHz, 24 or 32-bit.
Never a 16-bit application-level path. Also prove the custom 3.072 MHz PDM software-decimation
route. This proves audio ingress only and does not pull the bridge-transport hardware commitment
forward.

**L3 — real K1 interference.** Only after Core geometry exists: LED currents, buck operation,
BLE activity, NFC field, USB grounding, real flex lengths, enclosure. A custom audio validation
PCB may become worthwhile here, and its stack, connector, dimensions and placement derive from
the VAL-G1 outcome.

## Current-ESP32-S3 baseline

Measure post-GDFT behaviour under the real shipping workload: frame timing percentiles, worst
frame, deadline misses, ISR time, audio-task timing, radio off and on, heap, PSRAM, headroom.

**Open risk R2.** The compute-wall premise rests on a 13 July capture that predates the int64
GDFT promotion, and shipping headroom has never actually been measured. This baseline does not
reopen Q0-A — render and radio coexistence is independent of headroom — but the RT1062 port
target cannot be sized without knowing the figure being stepped up from.
