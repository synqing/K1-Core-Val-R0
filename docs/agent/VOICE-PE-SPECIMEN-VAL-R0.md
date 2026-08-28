# Voice PE specimen — K1-CORE-VAL-R0 re-derivation

Voice PE (Home Assistant Voice Preview Edition, Nabu Casa KiCad, CERN-OHL-P v2) is a
**pattern specimen**. It is not a K1 parts catalogue and it is not current K1 architecture.
Ratified as **D-043**.

External files (non-authoritative for this repo, even after a banner):

- `/Users/spectrasynq/SpectraSynq-EDA/pcb-knowledge/voice-pe-reference/VOICE-PE-EXTRACTION-REPORT.md`
- `/Users/spectrasynq/SpectraSynq-EDA/pcb-knowledge/voice-pe-reference/voice-pe-reference-patterns/SKILL.md`

Those files mix a strong forensic extraction with a **K1-CORE-R1C** translation (single S3,
M.2 / K1-USB-R0, WS2816C, Core-0 Goertzel, “do not add a second processor”). **Do not hand
§5 or that skill to Codex as live K1 authority.** Re-derive here.

The v1.0 schematic PDF still shows SY80004 / ETA3410. The released KiCad does not. Pin every
claim to the released KiCad, not the PDF.

## Evidence hierarchy

1. K1 ratified contract
2. Primary vendor reference / datasheet
3. Current K1 architecture
4. Voice PE as pattern precedent only
5. Never AI-generated circuit invention

Voice PE footprint count (~439) must never set `N_estimated_symbols_option_C`.

## Architecture — closed

Voice PE’s XMOS / ESP32-S3 split **confirms** current K1-CORE-VAL-R0:

```text
Voice PE : XMOS = deterministic audio/clock ; S3 = radio/application
K1-VAL   : RT1062 = deterministic audio/AP/render/LED ; S3 = radio/control/service
```

Option C selected. Option B / M.2 deferred. DVJ6B frozen. Six layers baseline. No XU316.
No hardware privacy mute in G2.0A.

Meta-principle (reasoning aid, not a new circuit): enforce a requirement at the lowest
physical layer that can enforce it; let higher layers observe it.

## What survived K1/vendor review (2026-08-28)

| Candidate | Ruling | Where it lives |
| --- | --- | --- |
| Test-**access** census (not one TP per net) | **ADOPTED** as validation doctrine | `architecture/VALIDATION-ARCHITECTURE.md` |
| PDM XOR / motion 0R / audio-clock isolation | **ALREADY K1** — do not re-mint as Voice PE 0R | existing contracts + retired fixture inventory |
| K1BR series ohms / Debug Fabric mux vs 0R | **NOT FROZEN** — representative / TUNE; mux vs jumper remains OPEN | `contracts/k1br-bridge.md`, `contracts/debug-fabric.md` |
| USB_SHIELD 1 MΩ ∥ 1 nF + hard-bond | **CANDIDATE / VALIDATION_DESIRABLE** — Voice PE values not frozen | specimen only; `contracts/usb-interface.md` untouched |
| LED-branch protection bypass | **CANDIDATE capability**; implementation **OPEN** | specimen only; no 0402 0R symbol |
| GNDA split island | **REJECTED** | already `pcb/LAYER-USE-POLICY.md` |
| Signals on L3 | **Not planned.** L3 is power-only by baseline. A documented VAL-G3/G5 exception may exist later for BGA escape. L2/L5 remain sacred. | no layer-policy edit this pass |
| RF plane-void trick | **REJECTED** (WROOM) | — |
| Voice PE mic 71 mm / taper | **REJECTED numbers**; acoustic geometry **principle** waits on K1 flex freeze | G3+ |
| Universal teardrops | **ADAPT** as a G6 finishing pass with DRC/geometry review | deferred |
| Service silk / fab impedance table | **ADOPT principle**; copper at G4/G5/G7 | deferred |
| Hardware mute | **OUT OF G2.0A** | product/UX later |
| Wi-Fi/BLE coexistence | **VAL-G8 experiment**, no new hardware | deferred |
| Alternate stacked footprints | **PRINCIPLE only**; no speculative second flash/regulator | — |

## External-repo banner

SpectraSynq-EDA was dirty (27 paths, including untracked `pcb-knowledge/voice-pe-reference/`).
A historical banner was written on the two Voice PE files. **That checkout was not committed.**
K1 does not wait on it. External mappings remain non-authoritative either way.

## This exercise does not write EasyEDA

D-042 terminated qualification-project mutation. Live EasyEDA is canonical
`K1-Core-Val-R0` / `64325d0e55e0435abd018defb0089a9b`. Receipt:
`evidence/VAL-G2-2026-08-28/CURRENT-STATE-RECEIPT.md`.

No USB shield network and no LED bypass part may be placed until a later K1-specific
implementation is chosen and gated.

## SciPy

Unused. Wrong lane.

## Deferred to later gates (do not execute from this lane)

- **G3 / G4:** service-function silk names; bind live `TP*-suffix` tags to functions.
- **G5:** fab / mechanical impedance table; L2 / L5 remain virgin (no routed signal or power
  tracks); L3 stays power-only unless a documented G3/G5 exception is required for BGA escape;
  no AGND / DGND split.
- **G6:** teardrop finishing pass with DRC and geometry review (BGA, USB, NFC, fine-pitch).
- **G8:** BLE / Wi-Fi / both / high traffic / TX power versus ADC, mic floor, rails, RT timing
  and LED artefacts — experiment only; no new hardware from Voice PE.
- After the K1 microphone flex is frozen: K1 acoustic numbers in the microphone contract.
  Do not import Voice PE 71 mm / 72.08 mm / taper.
