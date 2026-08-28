---
contract: usb
status: RATIFIED
receptacle_count: 2
receptacles: [J1-PWR1, J7-ESP]
third_receptacle: FORBIDDEN
service_usb_owner: ESP32_S3
service_usb_connector: J7-ESP
rt_direct_usb_owner: RT1062
rt_direct_usb_connector: J1-PWR1
rt_direct_usb_controller: USB_OTG1
primary_power_inlet: J1-PWR1
j1_type_c_role: SINK
j7_back_power: FORBIDDEN
usb_audio: EXPERIMENT_ONLY
usb_audio_termination: J1_RT1062_DIRECT
differential_impedance_ohm: 90
authority: D-044
---

# USB interface contract

Two USB-C receptacles. No third. D-044.

| Receptacle | Owner | Carries | Powers the board |
| --- | --- | --- | --- |
| `J1-PWR1` | RT1062 | Primary 5 V inlet **and** direct RT1062 USB2 data | Yes |
| `J7-ESP` | ESP32_S3 | Native service USB: flashing, serial and debug, recovery, configuration | No |

Every USB statement in this repository names its receptacle. "USB" without a receptacle is not
authority.

## `J1-PWR1` — power inlet and direct RT1062 USB2

J1 is the primary 5 V power inlet for the whole board and, on the same receptacle, the direct
RT1062 USB2 data port.

D+/D- terminate on RT1062 USB OTG1 through ESD and signal-integrity conditioning. That gives
RT-direct USB diagnostics and the experimental USB-audio lane without crossing K1BR. RT1062
carries two USB 2.0 OTG controllers with integrated PHY (NXP IMXRT1060CEC), so this path uses a
peripheral the frozen package already provides.

Because J1 consumes VBUS it is a Type-C **sink** and requires correct Type-C sink behaviour on
CC1/CC2 — pull-downs and current-advertisement detection per the Type-C sink requirements, not a
legacy USB-B power assumption.

VBUS detect and sense follow the NXP USB OTG1 reference exactly. This is a copy-the-reference
requirement, not an invention item: no VBUS-sense divider, comparator or enable arrangement may
be improvised at layout time.

## `J7-ESP` — ESP32_S3 native service USB

ESP32_S3 owns service USB: flashing, configuration, serial and debug, and recovery.

J7 does **not** power the K1 system and must not back-power the board. Reverse and back-feed
protection at J7 is a requirement, not a preference.

Service USB creates no K1BR audio-payload obligation, but it retains normal connector, ESD,
signal-integrity, RF-separation and pin-ownership costs: fixed native-USB pin ownership,
connector and ESD placement, differential routing with a continuous return path, separation from
the 2.4 GHz zone, and interrupt and service-firmware cost.

`J7-ESP` SBU1/SBU2 are intentional opens.

## K1BR is unchanged

K1BR remains command, state and telemetry only. It does not carry raw PCM. Nothing in D-044
relaxes that boundary — D-044 removes the need to relax it, by giving RT1062 its own external
USB port.

## USB audio

Experimental. Not a baseline R0 requirement.

USB audio terminates on `J1-PWR1` into RT1062 USB OTG1. That is now the stated termination, not
an open exception: the earlier "RT1062 direct **or** a named K1BR exception" branch is closed by
D-044, because the direct path exists on a receptacle the board already carries. No K1BR
audio-payload exception is required and none is granted.

**Open risk R1 stands.** Terminating USB audio on RT1062 places a USB device stack and its
interrupts inside the same real-time domain as capture, Audio Processing and render. The K1BR
rule forbidding synchronous waits governs the bridge, not a USB peripheral ISR. Either budget
that intrusion explicitly and measure it, or keep USB audio out of R0 scope. R1 is a real-time
budget risk, no longer a topology question.

## Routing

90 ohm differential on both receptacles, equal-length parallel routing over continuous reference
ground, minimum layer transitions, paired return vias where a transition is unavoidable. Keep
USB activity away from the 2.4 GHz antenna region — both pairs, not only the ESP32_S3 one.

J1 additionally carries the full board inlet current on the same connector as a differential
pair. Power-corridor geometry and the data pair are separate problems on one part and must not be
resolved by whichever is drawn first.
