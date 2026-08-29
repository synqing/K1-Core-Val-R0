# ADR-051: VAL-R0 audio is dual-input (AUX + PDM)

**Status:** RATIFIED
**Date:** 2026-08-30
**Deciders:** Captain ruling 2026-08-30
**Register:** D-051 = `RATIFIED`

This ADR restores architecture that K1-AUDIO-EVAL-R0 already specified and that
failed to migrate into the K1-CORE-VAL-R0 audio contract. It does **not** claim
that the live EasyEDA sheet already carries the jack. The sheet is still the
PDM portion only.

## Context

The live VAL-R0 sheet and the previous audio contract described two mutually
exclusive IM69D130 routes into RT1062:

- FIT: IM69D130 → TLV320ADC6120 PDM → hardware decimation → TDM → RT1062
- DNP: IM69D130 → RT1062 SAI → software decimation

An audit read that pair as “dual audio” and treated unused ADC analogue pins as
a deliberate rejection of a 3.5 mm input. Captain overruled that reading.

K1-AUDIO-EVAL-R0 (`docs/01-PRD.md`, `docs/03-HARDWARE-ARCHITECTURE.md`,
`docs/04-ELECTRICAL-DESIGN.md`, BOM and schematic-connection tables in the
33-file package) already required:

- switched stereo 3.5 mm TRS line/headphone-level capture;
- true differential laboratory input as an XOR population against the consumer
  pad;
- one IM69D130 through the same TLV320ADC6120;
- aligned line-L, line-R and room-microphone capture;
- 48 kHz, four-slot, 32-bit TDM;
- ADC-PDM / direct-PDM XOR.

When `U11-AUD` / TLV320ADC6120 appeared on the K1-CORE-VAL-R0 mainboard, only
the PDM-route comparison was copied. The analogue jack and front end were not.
That omission is a requirements-migration failure, not a ratification that AUX
is unused.

The EVAL host delta sent the experimental direct-PDM branch to ESP32. Current
K1 ownership (D-001) keeps capture, ADC/TDM ingress, Audio Processing, VP and
render on RT1062. The VAL-R0 direct-PDM branch therefore terminates on RT1062,
not ESP32-S3. D-028 (RT1062 package) is unchanged.

## Decision

VAL-R0 audio is **dual-input** on one TLV320ADC6120:

1. Switched stereo 3.5 mm AUX/line into analogue CH1 and CH2.
2. One IM69D130 PDM room-microphone lane into the same ADC (FIT default).
3. Simultaneous ADC capture of AUX-L, AUX-R and IM69D130 in the normal
   line-plus-room profile.
4. 48 kHz, four-slot, 32-bit TDM to RT1062:
   - slot 0: AUX-L
   - slot 1: AUX-R
   - slot 2: IM69D130 / room microphone
   - slot 3: reserved / diagnostic
5. The ADC-PDM / direct-RT PDM XOR remains, and applies **only** to the
   microphone-capture routes. It does not replace, disable or redefine AUX.

Do not freeze the post-D049/D050 electrical graph while AUX is absent from
that graph.

Do not assign GPIO in this decision. Do not bind the jack MPN. Do not place
EasyEDA parts under this ADR. Schematic restore waits until USB-C 3D seating
is off the live canvas and Captain issues an EasyEDA GO.

## Options considered

### Option A: keep the PDM-only contract (overruled)

| Dimension | Assessment |
|-----------|------------|
| Complexity | Lowest on paper |
| Cost | Leaves U11 analogue channels unused |
| Validation | Cannot run the line-plus-room experiment the EVAL PRD required |
| Team familiarity | Matches the incomplete migrated contract |

**Pros:** Matches the present sheet.
**Cons:** Treats a migration omission as a product decision; cannot capture
AUX-L / AUX-R / room-mic together; contradicts K1-AUDIO-EVAL-R0.

Captain rejected the reading that unused analogue pins meant AUX was never
ratified.

### Option B: keep AUX on a daughterboard only

| Dimension | Assessment |
|-----------|------------|
| Complexity | Second PCB, host FPC, card enable |
| Cost | Repeats the EVAL 95 × 50 mm card after U11 is already on Core |
| Validation | Splits the quiet enclave off the mule |

**Pros:** Preserves the original EVAL form.
**Cons:** `U11-AUD` is already on the mainboard. The missing work is the
analogue lane into that part, not another card. EVAL’s 30-pin FPC, PCA9306
and card-enable map are not copied.

### Option C: restore EVAL analogue + PDM onto the mainboard ADC (selected)

| Dimension | Assessment |
|-----------|------------|
| Complexity | Jack, ESD, consumer/lab XOR, AC coupling, pin-use re-derivation |
| Cost | Area in the audio enclave; later D06 rebase |
| Validation | Restores LINE_PLUS_ROOM on the mule |

**Pros:** One converter, both input families, simultaneous three-channel
capture; XOR stays a mic-lane experiment; D-001 ownership unchanged.
**Cons:** Live sheet is still PDM-only; IN2-as-PDM-data and pin-19-as-MCLK
on that sheet collide with EVAL analogue pin use and must be re-derived
when the jack is drawn.

## Migrated electrical facts (from K1-AUDIO-EVAL-R0)

These are design inputs for the later schematic restore. They are **not** a
licence to copy values without recalculation, and they are **not** a jack
circuit drawn in this ADR.

| Topic | EVAL source | VAL-R0 reading |
| --- | --- | --- |
| Converter | TLV320ADC6120IRTER / C2874822, sole fitted ADC | Already `U11-AUD`; part family unchanged |
| Analogue CH1 | IN1P / IN1M = line L | AUX_L |
| Analogue CH2 | IN2P / IN2M = line R | AUX_R |
| PDM clock | GPIO1 = PDMCLK, FIT default | Unchanged role; XOR to RT1062 remains the DNP alternate |
| PDM data | MICBIAS_GPI2 = PDMDIN | EVAL pin use. The live sheet’s `IN2P` as PDM data is the PDM-only interim and cannot survive once CH2 is analogue |
| MCLK | EVAL treated MCLK as an optional host experiment pin | D-013 override remains REQUIRED. Pin 19 cannot be both PDMDIN and MCLK. Re-derive at schematic restore; no GPIO assigned here |
| Jack | Switched stereo 3.5 mm TRS; candidate `PJ-3537S-SMT` / `C2689709`, status `PINOUT-VERIFY` | Candidate / reference only. Mainboard MPN is **not bound**. Designator is **not** `J1` (`J1-PWR1` is USB-C) |
| Front end | Low-C ESD first; consumer pseudo-differential matched series/return (EVAL start 10 kΩ 0.1 %, EVT-tunable); four DNP 0 Ω lab links; four 1 µF AC-coupling capacitors | Recalculate attenuation, impedance and corners from TI authority. Meet 2.0 Vrms consumer source without clipping. Do not tie the sleeve to negative ADC pins without proving the topology |
| Populations | Consumer FIT XOR laboratory DNP; ADC-PDM FIT XOR direct-PDM DNP | Same XOR rules. Never fit both members of either pair |
| Direct PDM | EVAL: ESP32 | VAL-R0: RT1062 (D-001) |
| Host FPC / card LDO / PCA9306 | Daughterboard-only | Not copied |
| DualMCU AIC3204 jacks | Other programme | Not the VAL-R0 circuit |

Required operating profiles (EVAL PRD + Captain addendum):

- `LINE_REF_FIXED`, `LINE_DRE`
- `LINE_PLUS_ROOM`, `LINE_PLUS_ROOM_DRE`
- `MIC_ADC`, `MIC_DIRECT`
- `LINE_HPF_PROBE` remains an EVAL-retained optional probe, not a substitute
  for `LINE_PLUS_ROOM`

`MIC_ADC` versus `MIC_DIRECT` is **not** the meaning of dual audio.

## Trade-off analysis

Keeping the PDM-only contract would freeze a graph that cannot do the
line-plus-room experiment the validation mule exists to run. Restoring a
daughterboard would ignore that the ADC is already on Core. Restoring the
analogue lane onto `U11-AUD` re-opens pin use (PDM data and MCLK) and needs
a later EasyEDA pass. That later pass is cheaper than ratifying the wrong
input architecture.

## Consequences

- `contracts/audio-interface.md` is dual-input. PDM XOR language stays as
  the microphone alternate.
- The live sheet remains PDM-only until a later Captain-authorised EasyEDA
  restore. Historical pin audits that call IN1/IN2 unused are descriptions of
  that sheet, not living architecture.
- Official electrical-graph freeze cannot close on a PDM-only netlist.
- No GPIO map, no jack MPN bind, no second schematic sheet, no EasyEDA write
  under this ADR.

## Action items

1. [x] Record D-051 and restore the audio contract.
2. [ ] After USB-C 3D seating is off the live canvas, Captain EasyEDA GO for
   jack + ESD + conditioning + coupling + pin-use repair on the single sheet.
3. [ ] Prove manufacturer jack pinout, switch contacts and insertion axis
   before binding an MPN.
4. [ ] Recalculate the consumer/lab networks from TI analogue-input authority.
5. [ ] Keep D06 on one sheet; enlarge the audio envelope only after the
   electrical graph includes AUX.
