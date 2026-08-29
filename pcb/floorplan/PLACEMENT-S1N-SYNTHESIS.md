# K1-CORE-VAL-R0 — S1-N: Normalised Synthesis and Contradiction Closure

```text
STATUS   = STUDY_INPUT
BINDING  = NO — no authoritative EasyEDA or PCB coordinate was changed
CLASS    = CopperPilot-class geometry proposal (convergence, NOT a third thesis)
GATE     = VAL-G3 / VAL-G4 input
PEERS    = PLACEMENT-ORIENTATION-STRATEGY.md (V1) · PLACEMENT-V2-STAR-STUDY.md (V2)
RENDER   = PLACEMENT-ORIENTATION-RENDER.html — tabs V1·158 archive / V2 archive / V1N / S1N / Verdict
DATE     = 2026-08-29
```

S1-N converges V1 and V2 into one comparable, internally consistent floorplan pair:
**V1N** (the normalised V1 baseline, defects retained and measured) and **S1N** (V1
topology + only the explicitly adopted V2 improvements + contradiction closures). No new
architectural thesis was invented.

## 0. Normalisation (identical in V1N and S1N)

- Board exactly **155.0 × 38.0 × 1.60 mm, six-layer** JLC06161H-3313. The V1 archive tab
  stays at its .epro2 snapshot 158.0 outline; V1N compresses the east field, with the NFC
  island unified at x≈122.5 in both variants so island position is not a confound.
- **J1 = TE Connectivity 2129691-1 / C590834** in both. Drawn with SMT signal contacts and
  through-hole shell posts (catalogue-level). **The complete footprint, cutout and mounting
  geometry is labelled UNVERIFIED** on the render and here: until the TE customer
  drawing/CAD is checked, **no mechanical closure is claimed**.
- Identical mounting envelopes: H1 (7, 32) · H2 (7, 6) · H3 (121, 31.5) drawn as **complete
  fastener envelopes** (Ø7 head/washer + Ø8 boss ghost), not hole centres; P4 passive rest
  at (28.5, 35.6). H3's envelope edge reaches x≈124.5 — west of the reserve.
- Identical **hardware-inclusive NFC reserve**: x 126–155, full height. Occupancy counts
  connector bodies, fasteners, washers, standoffs, cable shields and enclosure bosses —
  not only PCB footprints.
- Identical harness assumptions (J1 north ≥10 mm bend; LED cables north; mic flex bend
  volume identical wherever it exits) and identical copper-stack assumptions.
- Chassis/shield/ESD overlay at J1 and all cable entries (⏚ stitch provisions drawn).
  Connector locations remain provisional until enclosure egress is authoritative.

**V1 defects deliberately retained in V1N** so S1N's deltas are measurable:
D-a J9 flex + bend volume in the reserve corner · D-b J10 + cable in the antenna field ·
D-c all K1BR series R at the S3 end · D-d source-side LED switch (~70 mm switched rail) ·
D-e the false "DN1 = 0 vias" claim · D-f the NW gateway asserted by arrows, never studied.

## 1. S1N mandatory changes — how each closed

1. **J9 out of the NFC field.** Mic flex moves to the south edge at x≈120; flex + full bend
   volume drawn and outside the reserve; opposite edge from the LED cables. Exit remains
   enclosure-open.
2. **J10 west of the pure antenna field** at (121.5, 8). The RF path now reads: RFO/EMI →
   matching → **0R XOR selection** → integrated loop feed (east, drawn) **or** external
   U.FL path (west, drawn dashed, DNP by default). Matching consequence stated on the
   render: the external tap adds a stub to the matched node — kept <5 mm and DNP'd, and
   any external-antenna work re-tunes (TUNE_TBD stands regardless).
3. **Enclave rules applied to V1 topology.** Named boundary x 104–126 × y 3.5–18 with a
   crossings register: **G1** SAI group (owner bus, iso-R matrix at the gate), **G2** I²C
   spine (L4, members are its loads), **G3** LED_THERM (L4, RC-filtered <1 kHz, guarded).
   No LED-current path, no switch node, no USB through-route, no unrelated clock. LED data
   is **rerouted north of the enclave** (+2.3 mm clearance + via guard) instead of skirting
   through its NW corner. Unnamed crossings: **0**.
4. **Switch-at-load LED protection in V1 topology** — full worksheet in §3.
5. **NW gateway escape study** at real ball geometry — §4. Headline: two claims died.
6. **Directional terminations** — §2. The R23-family split is a flagged schematic delta.
7. **Combined B-side owner-shadow** — §5, including the NXP-style bottom decoupling and
   the coexistence proof-or-confession.
8. **DCDC ↔ flash reconciliation** — §4/§5. The drawing **falsified** the comfortable
   claim; the corrected containment scheme is drawn and labelled CONDITIONAL.

## 2. Directional termination register (series R at the driving end)

| Signal | Source | Destination | Series-R owner | Test access |
|---|---|---|---|---|
| K1BR_SCK | RT1062 (LPSPI1 master) | ESP32-S3 | **RT end** (B-side, beside its escape vias) | TP at S3 end |
| K1BR_MOSI | RT1062 | ESP32-S3 | **RT end** | TP at S3 end |
| K1BR_CS | RT1062 | ESP32-S3 | **RT end** | TP at S3 end |
| K1BR_MISO | ESP32-S3 | RT1062 | **S3 end** | TP at RT end |
| K1BR_IRQ | ESP32-S3 | RT1062 | **S3 end** | TP at RT end |
| LED_D0 / LED_D1 | RT1062 (FlexIO2) | U14 / U15 | **RT end** | 0R pad mid-run |
| PDM_CLK | active capture master (RT or ADC — XOR) | IM69D130 | **active master end** (both pads exist in the XOR matrix) | TP4 |
| AUDIO_MCLK/BCLK/FSYNC | RT default · J8 external override | ADC6120 | **RT end**; the iso-R doubles as the contract-required isolation | TP3 + J8 |
| AUDIO_DOUT | ADC6120 | RT1062 | **ADC end** | TP |

Flagged schematic delta: the captured netlist groups the R23-family at the S3 end.
SCK/MOSI/CS series R move to the RT gateway in one closed mutation transaction before G4.

## 3. LED power / fault / thermal worksheet (S1N, per channel unless stated)

| Item | Value | Evidence |
|---|---|---|
| 5V_SYS trunk RSH1→x≈100 | ~66 mm: L3 region 12 mm × 15.2 µm + L1 reinforcement 8 mm × 35 µm | MEASURED (drawn) |
| Trunk R / drop @ 3 A (both ch) | ≈2.5–3 mΩ → ≈8 mV; ΔT < 5 °C | CALCULATED_FROM_STACKUP / ESTIMATED |
| Switched branch U4→FB→J2/J3 | ~8 mm × 6 mm × 35 µm ≈ 0.7 mΩ copper | CALCULATED_FROM_STACKUP |
| TPS2561 R_ON · FB DCR | ≈26 mΩ · ≈15 mΩ typ — the ferrite, not copper, dominates | ESTIMATED (datasheet-typical) |
| Total drop @ 1.5 A limit | ≈66–70 mV | ESTIMATED |
| ΔT @ limit | switch <15 °C @ ~59 mW/ch; copper negligible | ESTIMATED · UNPROVEN until a thermal pass |
| Neck-downs | none permitted <6 mm on branches; trunk taps 6 × Ø0.45 via arrays | rule, drawn |
| Connector-side bulk | 2 × 22 µF per channel at J2/J3 + source bulk | drawn |
| Return | L2 unbroken under trunk and branches; ≥4 GND vias per connector | MEASURED (drawn) |
| Source-side faults | eFuse (global trunk) + RSH1/INA226 + INA_ALERT | netlist |
| Load-side faults | per-channel current limit (RILIM ≈1.5 A), per-channel thermal shutdown, PG → RT | datasheet / netlist |
| Independence | channel L fault does not drop channel R (separate halves, shared protected IN) | topology |
| Switch off / faulted | connector +5 V dead (bulk discharges into load); 5V_SYS trunk stays powered; LED_OE_L/R tristates the shifter so data never drives an unpowered strip | netlist (OE nets exist) |

## 4. Local G4 escape study (real ball map — the render's second viewport)

RT1062 west half at θ180, all positions from the project's own symbol/footprint
(MEASURED_FROM_GEOMETRY). Findings:

- **K1BR:** J1/K1 are outer-ring — true L1 escapes. **J3/J4 are inner — via→L4→via, 2
  transitions each.** The "zero-via corridor" claim is corrected: corridor 0-via, escape
  ≈4 vias.
- **USB DN1:** L8/M8 sit **7 rings deep**. Escape is dogbone → L6 (L5 reference) → hub.
  **2 transitions minimum. The "0 via / 0 transition USB" claim is withdrawn** — for V1N,
  S1N, and it invalidates the same cell in the earlier V1/V2 matrix.
- **FlexSPI:** 6 B-side vias to the flash under SD_B1; 2 mm rework ring kept clear.
- **DCDC ↔ flash (item 8):** the drawing **falsified** "≥3 mm from the node projection" —
  the DCDC_LP ball columns (1–2) **interleave** the SD_B1 field (3–5); the achievable
  lateral gap is ~1.5–2.5 mm. Corrected containment, drawn: switch-node copper confined to
  L1 north of the package with a fenced via group; B-side under the LP ball projections
  sees only plane-shielded balls (L2–L5 between); flash shifted SW to (87.6, 21.4).
  Status: **CONDITIONAL** on a noise check — the "quiet FlexSPI corner" is no longer
  asserted, it is drawn and conditioned.
- **Service face:** SWD/LPUART1/straps/SAI1 fixed balls are outer-ring on the S face — L1.
- Routing itself remains G4 work; this study fixes the geometry and the claim hygiene.

## 5. B-side owner-shadow (combined, with coexistence register)

U8 flash (under SD_B1, shifted SW) · NXP-style core decap ring inside the fan-out via
field · boot straps under the S face · **K1BR RT-end series R** beside their escape vias
under the N face · DCDC field: **no B-side parts under the node projection** (keepout
drawn) · fan-out via field drawn · ≥2 mm rework ring around the flash, ≥0.3 mm via-to-pad
assembly clearance. Unjustified B-side parts: **0**.

## 6. West-edge S3 fallback (Captain: "RF-C FALLBACK") — corrections applied to the record

Naming note: G3 §3 already uses "RF-C" for the enclosed-cavity arrangement; this fallback
is the **west-short-edge** arrangement — flagged for the terminology harness so the two
never merge. Not qualified until all of the following are closed:

- Antenna genuinely outside the baseboard **or** the manufacturer-recommended board-material
  cutout — the "keepout under the antenna section" arrangement drawn in V2 is *not* claimed
  qualified.
- ≥15 mm three-dimensional clearance in **all** directions, enforced as a sphere, not a
  west-projection only.
- **SW2/SW3 and user finger volume violate it today**: nearest button ≈8.4 mm from the
  antenna section (MEASURED) — they move east of x≈22, and J6's cable bend volume is added
  to the check.
- **False clearance claims corrected:** nearest USB copper is ≈18 mm (DN2's L6 leg under
  the module body), not 35 mm; J1 body ≈32.7 mm, not 35 mm (MEASURED).
- Ground copper + ground-via fence treatment at the antenna feed boundary added per the
  Espressif guideline before any qualification run.

## 7. Escalation package (90° RT / LPSPI3 / SAI2) — preserved, not promoted

Promotion requires a **global pinmux proof**, one row per moved signal: exact MPN/package
(MIMXRT1062DVJ6B, 196 MAPBGA), pad, mux ALT mode, input daisy register, IO rail (NVCC
bank), DMA request, clock root, boot interaction, conflicts, firmware changes. Fillable
today from verified data: ball positions, NVCC banks. **UNPROVEN until IMXRT1060RM
lookup:** every ALT mode, daisy and DMA mapping. Lives with PLACEMENT-V2-STAR-STUDY.md.

## 8. Mechanical

U13 "neutral axis" language is withdrawn. Replacement: a **mount-dependent stiffness /
modal-placement hypothesis** — U13 sits inside the drawn fastener-envelope triangle, away
from insertion loads, cable tugs and switch actuation, and **re-derives when the enclosure
fixes the mounts**. Fastener envelopes (not centres) are drawn at H1/H2/H3; chassis/shield
provision and ⏚ESD marks at J1, J2/J3, J9, J10.

## 9. Corrected comparison matrix

Rendered on the Verdict tab with per-cell evidence labels
(MEASURED_FROM_GEOMETRY / CALCULATED_FROM_STACKUP / ESTIMATED / UNPROVEN). Manhattan
numbers are labelled ESTIMATED and are never presented as routed evidence. Key corrected
cells: DN1 = 2 transitions in **both** variants; K1BR = ~4 escape vias in both; DCDC/flash
coexistence = CONDITIONAL (finding, not assertion); NFC field hardware = the V1N defect
row vs S1N's clean field (nearest fastener envelope edge 124.5 < 126).

## 10. Disposition

| Class | Items |
|---|---|
| **ADOPTED** | 155.0 normalisation · TE 2129691-1 envelope (geometry UNVERIFIED) · J9 out of the NFC field · J10 + selection XOR west of the field · enclave rule-set with named gates G1–G3 · switch-at-load LED protection · directional terminations · B-side owner-shadow set · DCDC node-exclusion scheme · hardware-inclusive reserve · fastener envelopes · chassis/ESD provisions |
| **CONDITIONAL** | DN1 L6 escape dressing (full G4 escape) · LED-data guarded reroute (noise) · DCDC↔flash containment (noise check) · U13 position (mount-dependent) · connector positions (enclosure egress) |
| **FALLBACK** | West-short-edge S3, only after §6 corrections; not qualified today |
| **REJECTED** | 45° RT · 90° RT/LPSPI3/SAI2 as baseline · all series R at one end · J9/J10 in the NFC field · any "zero-via"/"0-transition" claim not shown geometrically · Manhattan estimates presented as routed evidence |
| **UNPROVEN** | TE 2129691-1 drawing/CAD (blocks mechanical closure) · LPSPI3 pad-set legality · full BGA escape (D-026/D-031 gate) · thermal (cluster and LED) · LED-seam noise · enclosure egress · DN2 under-body copper sign-off (fallback only) |

S1N is the recommended G4 entry floorplan. V1N exists to make that recommendation
measurable. Promotion of anything above requires the normal evidence path and a Captain
ruling; the authoritative PCB was not touched.
