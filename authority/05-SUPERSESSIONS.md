# Supersessions

Every entry records what was replaced, by what, and why. A document that merely mentions a topic
never supersedes an explicit earlier ruling on that topic without an entry here.

| Date | Superseded | Replaced by | Reason |
| --- | --- | --- | --- |
| 2026-08-24 | Monolithic ESP32-S3 as the K1 compute architecture | Dual-MCU: RT1062 plus ESP32-S3 radio bridge | ESP32-S3 compute wall |
| 2026-08-27 | Monolithic ESP32-S3 as a new-hardware candidate | Legacy parity oracle role only | Q0-A reaffirmed |
| 2026-08-27 | "SSCM-1 pin map v1.0 frozen" (2026-08-14) | SSCM-1 v2 reconstruction from present requirements | v1.0 could not be located in K1.hardware or SpectraSynq-Instrument-Spine; a contract that cannot be located is not frozen |
| 2026-08-27 | "EE CORE stays on JLC 3313 1.0 mm" (2026-08-20) | 1.60 mm, six layers | Validation platform carries RF, USB, high-current LED, audio and instrumentation |
| 2026-08-27 | master-plan v3 phrasing "AP-only Wi-Fi/radio bridge" [quoted-superseded] | `AP` = Audio Processing only; Wi-Fi access point spelled `WIFI_AP` / `SOFTAP` / `ACCESS_POINT` | Two architecture concepts shared a two-letter acronym inside authority files |
| 2026-08-27 | master-plan v3 listing REST and WebSocket framing as an ESP32-S3 responsibility | BLE-MIDI current, Wi-Fi surface parked | The 6-Aug ratification was explicit; a later ownership list is not a superseding ruling |
| 2026-08-27 | Hierarchical or per-domain schematic sheets | Exactly one schematic sheet, domains separated visually | The board exists to reason about domain interactions, which hierarchy conceals |
| 2026-08-27 | Three parallel board-envelope studies (105 / 115 / 125 mm) | One contraction study in `pcb/floorplan/FLOORPLAN-STUDY.md` | Three lanes produce one answer three times |
| 2026-08-27 | 21-script bootstrap harness plan | Two non-vacuous checks at VAL-G0 | Checks written before their artefacts exist become stubs, and stubs pass |
| 2026-08-27 | ESP32_S3 as radio-only on this board | Product role unchanged (radio and control); K1-CORE-VAL additionally grants a validation-only debug and service role | D13.1 needs a service endpoint. Scoped exception, not a product architecture change: no RT1062 real-time function moves |
| 2026-08-27 | Wi-Fi transport wholly unavailable on this board | Raw Wi-Fi and TCP permitted for VAL Debug Fabric instrumentation only | The product control plane is unchanged and stays parked; only an engineering transport is unlocked, and its interference is itself a measurement |
| 2026-08-27 | "Six layers preserves JLCPCB Economic PCBA eligibility" | Withdrawn. Economic is single-sided placement only; authorised double-sided placement commits the board to Standard PCBA at any layer count | The argument was factually void, and the layer-count conclusion does not depend on it |
| 2026-08-27 | Justifying a weak PDN case from interface clock rates | PDN demand is set by transient-current spectrum, edge rates, load steps, decoupling parasitics and rail target impedance | Bus bit rate is not PDN bandwidth; a slow clock with a fast edge carries content far above its fundamental |

