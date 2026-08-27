---
contract: usb
status: RATIFIED
service_usb_owner: ESP32_S3
usb_audio: EXPERIMENT_ONLY
usb_audio_termination: RT1062_DIRECT_OR_NAMED_EXCEPTION
differential_impedance_ohm: 90
---

# USB interface contract

## Service USB

Flashing, configuration, serial and debug, and recovery.

ESP32_S3 owns service USB. It creates no K1BR audio-payload obligation, but it retains normal
connector, ESD, signal-integrity, RF-separation, pin-ownership and Option-B interconnect costs:
fixed native-USB pin ownership, connector and ESD placement, differential routing with a
continuous return path, separation from the 2.4 GHz zone, possible SSCM-1 crossing implications
under Option B, and interrupt and service-firmware cost.

## USB audio

Experimental. Not a baseline R0 requirement.

K1BR forbids raw PCM, so a USB-audio stream terminating on ESP32_S3 cannot be forwarded to
RT1062 without dismantling the boundary that justified Option C. If USB audio stays in scope it
terminates directly on RT1062 — which carries two USB 2.0 OTG controllers with integrated PHY
interfaces (NXP IMXRT1060CEC) — or a named diagnostic exception to K1BR is written and recorded
in the decision register.

**Open risk R1.** Terminating USB audio on RT1062 places a USB device stack and its interrupts
inside the same real-time domain as capture, processing and render. The K1BR rule forbidding
synchronous waits governs the bridge, not a USB peripheral ISR. Either budget that intrusion
explicitly and measure it, or keep USB audio out of R0 scope.

## Routing

90 ohm differential, equal-length parallel routing over continuous reference ground, minimum
layer transitions, paired return vias where a transition is unavoidable. Keep USB activity away
from the 2.4 GHz antenna region.
