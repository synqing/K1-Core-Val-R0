# Terminology

## AP

`AP` means **Audio Processing**. Only.

A Wi-Fi access point is written `WIFI_AP`, `SOFTAP` or `ACCESS_POINT`. The bare phrase
"AP-only radio bridge" is forbidden in every authority-bearing document and in every guard. [quoted-superseded]

## Processor names

Never write "the processor", "the MCU" or "the chip" where ownership matters. [quoted-superseded]
Write `RT1062` or `ESP32_S3` explicitly. Ownership language that does not name a part is not
authority.

## Wireless

- `BLE-MIDI` — the current wireless control plane.
- Wi-Fi, REST and WebSocket — parked. Not current. Not authority.
- The 2.4 GHz RF zone is a physical requirement, not a protocol choice.

## Bridge

`K1BR` — the SPI seam between ESP32_S3 and RT1062. Class: command, state, telemetry.

## Gates

`VAL` means Validation. Gates run VAL-G0 through VAL-G8.

## Checker exemptions

A line that must quote banned or superseded language carries the marker `[quoted-superseded]`.
`check_terminology.py` skips those lines and reports how many exemptions it honoured, so an
exemption can never hide a violation silently. Use it only where quoting the banned text is the
point of the sentence.
