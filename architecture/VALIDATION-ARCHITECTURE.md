# Validation architecture

## Gates

| Gate | Purpose |
| --- | --- |
| VAL-G0 | Project bootstrap and authority |
| VAL-G1 | Option B versus Option C close |
| VAL-G2 | Single-sheet native schematic |
| JLC-SCH-READY | VAL-G2 close gate: electrically frozen, professionally readable, EasyEDA-stable one-sheet. Unblocks RFQ/package and schematic handoff preparation only. |
| JLC-LAYOUT-READY | Later gate: `JLC-SCH-READY` plus layout-relevant IOMUX, footprints, DXF/mechanics, pad count, JLC source package. Unblocks paid JLCPCB placement/routing. |
| VAL-G3 | Mechanical envelope and domain floorplan |
| VAL-G4 | Real component placement and locks |
| VAL-G5 | Layer stack, net rules, planes, SI and PI |
| VAL-G6 | Routing and DRC |
| VAL-G7 | Fabrication-output proof |
| VAL-G8 | Silicon bring-up and validation |

## Independent audio programme

These lanes do not touch the Core and are not gated on VAL-G1. They are not a
substitute for the mainboard audio contract. D-051 restores VAL-R0 Core audio as
dual-input (switched stereo 3.5 mm AUX plus IM69D130 PDM through `U11-AUD`). The
independent L0–L2 programme still characterises converter and SAI behaviour off
the Core; it does not authorise omitting AUX from the Core graph.

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

## Test access (VAL mule)

A validation board needs documented safe observability, not a standalone test-point symbol
on every net.

Count these as legitimate test access: dedicated probe or pogo pad; fitted debug-connector
pin; service-header pin; 0R or source-termination resistor pad; option-jumper pad; accessible
IC test node.

Dedicated pads are preferred on power rails, POR/reset, boot straps, power-good / fault /
INA alert, and slow ownership or select lines.

SWD, UART, K1BR, PDM and audio clocks need access. A fitted 10-pin Cortex header is the SWD
interface; do not add extra SWDIO/SWCLK stubs merely to satisfy a count. Series or isolation
resistor pads are access.

Do not place casual probe stubs on USB differential pairs, NFC RF/matching, or other
impedance-sensitive lines.

Census of existing mechanisms:
`evidence/VAL-G2-2026-08-28/VOICE-PE-TEST-ACCESS-CENSUS.md`.
Voice PE is precedent only; it does not invent K1 pads.

## Current-ESP32-S3 baseline

Measure post-GDFT behaviour under the real shipping workload: frame timing percentiles, worst
frame, deadline misses, ISR time, audio-task timing, radio off and on, heap, PSRAM, headroom.

**Open risk R2.** The compute-wall premise rests on a 13 July capture that predates the int64
GDFT promotion, and shipping headroom has never actually been measured. This baseline does not
reopen Q0-A — render and radio coexistence is independent of headroom — but the RT1062 port
target cannot be sized without knowing the figure being stepped up from.
