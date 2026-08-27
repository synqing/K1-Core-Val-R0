---
contract: k1br
status: RATIFIED
transport_class: COMMAND_STATE_TELEMETRY
master: RT1062
slave: ESP32_S3
physical_link: SPI
forbidden_payloads:
  - RAW_PCM
  - RAW_PDM
  - AUDIO_FEATURES
  - RENDER_BUFFER
  - PIXEL_BUFFER
  - CRGB
---

# K1BR — inter-MCU bridge contract

RT1062 is the polling SPI master and owns canonical applied state. ESP32_S3 requests changes;
RT1062 validates, applies and reports canonical state.

## Allowed classes

ESP32_S3 to RT1062: command request, parameter update request, state snapshot request,
time and identity probe.

RT1062 to ESP32_S3: acknowledgement or rejection, canonical applied-state update, bounded health
and diagnostic telemetry, build and board identity.

## Forbidden payloads

Raw PCM, raw PDM, audio feature frames, effect render buffers, pixel or CRGB buffers, LED frame
data, pointers, native structs, compiler padding and vendor SDK types.

This boundary is what makes Option C deterministic. It is also expensive to move later, so it is
not relaxed for convenience. A USB-audio stream terminating on ESP32_S3 cannot be forwarded to
RT1062 across this seam — see `usb-interface.md`.

## Required behaviour

Bounded queues and payload sizes. No synchronous wait from RT1062 render or audio work.
Idempotent retry for commands. Explicit duplicate, old, malformed, unsupported and overflow
outcomes. Deterministic reset and state resynchronisation. Counters for accepted, rejected,
corrupt, duplicate, stale, overflow and reset.
