# Decision register

| ID | Date | Decision | Status | Source |
| --- | --- | --- | --- | --- |
| D-001 | 2026-08-24 | RT1062 owns audio capture, Audio Processing, VP, effects, render, pixels and LED output. ESP32-S3 is the radio bridge. | RATIFIED | dual-MCU ruling; master-plan v3 |
| D-002 | 2026-08-24 | Inter-MCU link is SPI. K1BR v1 framing frozen. | RATIFIED | K1-DM-010 |
| D-003 | 2026-08-27 | Q0-A reaffirmed. Monolithic ESP32-S3 is the legacy parity oracle, not a new-hardware candidate. | RATIFIED | Captain ruling |
| D-004 | 2026-08-27 | Live fork is Option B (carrier plus SSCM-1) versus Option C (RT1062 and ESP32-S3 on Core). | OPEN | Captain ruling |
| D-005 | 2026-08-27 | SSCM-1 v1.0 is no longer described as frozen. One bounded recovery pass, then author v2 from present requirements. | RATIFIED | Captain ruling |
| D-006 | 2026-08-27 | `AP` means Audio Processing only. | RATIFIED | Captain ruling |
| D-007 | 2026-08-06 | BLE-MIDI is the sole wireless control plane. Wi-Fi, REST and WebSocket are parked. | RATIFIED | 6-Aug ratification |
| D-008 | 2026-08-27 | ESP32-S3 RF zone stays mandatory regardless of protocol. BLE and Wi-Fi share the radio and antenna. | RATIFIED | Captain ruling |
| D-009 | 2026-08-27 | NFC RF front end stays carrier-side under both B and C. Only I2C and IRQ may cross SSCM-1. | RATIFIED | Captain ruling |
| D-010 | 2026-08-27 | Exactly one EasyEDA schematic sheet. Hierarchical sheets forbidden. | RATIFIED | Captain ruling |
| D-011 | 2026-08-27 | Single-sheet doctrine requires a measurable EasyEDA qualification before irreversible reliance. | RATIFIED | Captain ruling |
| D-012 | 2026-08-27 | 1.60 mm, six layers. The 1.00 mm-only assumption is retired. | RATIFIED | Captain ruling |
| D-013 | 2026-08-27 | Audio clock master defaults to RT1062, but external override capability is required. | RATIFIED | Captain ruling |
| D-014 | 2026-08-27 | Service USB to ESP32-S3. USB audio terminates on RT1062 or takes a named K1BR exception. Never PCM across the bridge. | RATIFIED | Captain ruling |
| D-015 | 2026-08-27 | Create a check when the artefact it checks first exists. No speculative stub harnesses. | RATIFIED | Captain ruling |
| D-016 | 2026-08-27 | One floorplan contraction study, not three parallel envelope documents. | RATIFIED | Captain ruling |
| D-017 | 2026-08-27 | RT1062 has no MICFIL or hardware PDM decimation peripheral. Direct PDM is SAI plus software decimation. | RATIFIED | NXP IMXRT1060CEC |
