---
contract: sscm1_v2
status: DRAFT
connector_candidate: M2_B_KEY_2280
recovered_v1: false
---

# SSCM-1 v2 — ownership boundary requirements

Requirements first. Pin assignment last.

## Crossings

| Crossing | Requirement |
| --- | --- |
| LED left and right | 2 fast-edge outputs. Signal integrity and return path, not just pin count. |
| IM69D130 direct PDM | CLK and DATA, ground between. |
| ADC6120 audio bus | BCLK, FSYNC, SDOUT, plus MCLK where the module is clock master. |
| Audio clock override | See the dedicated section below. Not generic GPIO. |
| Peripheral control | I2C. |
| NFC | Host bus and IRQ only. The 13.56 MHz path never crosses. |
| Accelerometer | I2C and IRQ, or a module-side sensor. |
| USB | One differential pair per processor-side USB function. |
| UART and debug | TX, RX, and which part owns the console. |
| Reset and boot | Per-part controls where both MCUs are module-side. |
| Module identity | `MODULE_EN`, `MODULE_PRESENT`, `MODULE_ID`. A carrier must know what it holds. |
| Power | Rails, current and sequencing. Carriers own the power domain. |
| Dual-MCU seam | Crosses only where the two MCUs are not colocated. Keeping them colocated is the strongest argument for Option B. |
| Debug Fabric UART, service to target | `VAL_RT_UART_S3_TO_RT` — one contact, ground adjacent. |
| Debug Fabric UART, target to service | `VAL_RT_UART_RT_TO_S3` — one contact, ground adjacent. |
| Recovery request | `RT_RECOVERY_REQ` — one contact. Legal as a single crossing **only** because target-local hardware decodes it into both boot-mode bits. |
| Reset request | `RT_RESET_REQ_N` — one contact, open drain into the target-local wired-OR. |
| Target power valid | `RT_POWER_GOOD` — one contact, from the target-local supervisor. |
| Spare | Real contingency. "All pins used" is how a module standard dies at its second product. |

## Audio clock override — must be answered, not counted

The override cannot be treated as three interchangeable GPIO. The v2 study must answer:

- Is the external clock source carrier-side, or introduced through the audio evaluation connector?
- Do `AUDIO_MCLK`, `AUDIO_BCLK` and `AUDIO_FSYNC` cross toward RT1062, and in which direction?
- Are those contacts input-only, output-only, or muxed and bidirectional?
- Where does clock-source selection occur, and what drives `AUDIO_CLK_SELECT`?
- Is `EXT_AUDIO_CLK_PRESENT` required?
- What happens electrically when the module is absent or unpowered?
- Are the clock lines isolated from an inactive driver?

Each clock contact requires adjacent ground, defined direction, source-series placement,
inactive-driver isolation, sensible connector grouping and test access.

## Estimated crossing

Roughly 20 to 24 signals before contingency, once MCLK and the microphone enable have owners.
Plausible against a 30-signal budget; not roomy. That budget was set on 2026-08-14, ten days
before the dual-MCU ruling existed.

## Stays module-local — does not consume crossings

SWD and JTAG, the raw `BOOT_MODE0`/`BOOT_MODE1` bits, the reset supervisor, the recovery decoder,
the passive boot straps, the UART arbitration and every manual override live **on the module with
the RT1062**. Exporting raw debug and boot pins across the connector is what this partitioning
exists to avoid. It also means an SSCM-1 module can be brought up and recovered on a bench
without a carrier, which materially increases the value of Option B.

Debug Fabric therefore adds approximately **five logical crossings**, not a dozen.

## Failure condition

If M.2 B-key cannot carry this crossing with grounds between clock groups, adequate power
contacts, correct RF placement where ESP32_S3 is module-mounted, sane boot and debug ownership,
and genuine spare capacity — Option B fails honestly at the requirements stage, before any copper.
