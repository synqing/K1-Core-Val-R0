# K1-CORE-VAL-R0 — S1N-R1: Current-Authority Rebase

```text
STATUS   = STUDY_INPUT
BINDING  = NO — no authoritative EasyEDA or PCB coordinate was changed
CLASS    = Rebase of S1N onto current authority. NOT a new placement thesis.
CANDIDATE= S1N remains the sole candidate architecture; V1N remains the measured negative control
GATE     = VAL-G3 / VAL-G4 input
RENDER   = PLACEMENT-ORIENTATION-RENDER.html — tabs V1·158 / V2 (archives) · V1N · S1N-R1 · Verdict
DATE     = 2026-08-29
RULE     = every moved component has a written physical cause; no movement for aesthetic tidying
```

Seven moves, zero topology changes. Everything in the Captain's PRESERVE list is untouched:
155 × 38 study frame (not a mechanical lock), S3 antenna at the south RF aperture, hub between
S3 and RT, RT θ180 baseline (now explicitly conditional on the authoritative pinmap),
power-entry west, switch-at-load LED protection, J2/J3 north, J9 south, J10 west of the field,
full-height hardware-inclusive NFC reserve, named enclave crossings, south service corridor,
directional K1BR terminations, B-side owner-shadow, conditional DCDC/flash coexistence.
Nothing on the DO-NOT-REOPEN list was reopened.

## R1-a · J1 → D-050 MECHANICAL RESERVE (physical cause: J1 authority moved a generation)

The S1-N normalisation on TE 2129691-1 is stale. Current D-050 state: **GT-USB-7005A /
C5250872 SELECTED, NOT YET BOUND**, TE archived as the previous fallback. Both V1N and S1N-R1
now draw J1 as a **D-050 MECHANICAL RESERVE** envelope (bounding both candidates, ghost shell
inside) labelled `J1 D-050 MECHANICAL RESERVE — SELECTED GT-USB-7005A, BIND PENDING`. The
west-bay geometry is **not authoritative** until bind; the render no longer pretends any
concrete envelope is current.

Constraint set to re-evaluate at bind (recorded on the part, scoped so the central/eastern
architecture is NOT reopened): board cutout · signal-pad and B-row positions · shell/support-tab
geometry · connector centre height · insertion axis · shield/ESD region · CC-protection
footprint · raw-VBUS capacitor/discharge network · cable bend envelope · J1-ESD → USB2422
distance and path · interference with the adjacent mounting envelope.

**J1↔hub US ≈45 mm is demoted to REMEASURE-AT-BIND** — the figure is not preserved by
assumption; the matrix row now carries UNPROVEN-at-bind.

## R1-b · D11 hub/validity island census (physical cause: envelope under-bounded)

F6_VALIDITY_SOURCE is **OPEN** — the source must come from the voltage-envelope proof, not a
default. The previously drawn TPS7A2550-class part in the U22-USB slot is therefore a
**PARAMETRISED PLACEHOLDER** sized for the worst candidate, and the independent host-VBUS
unplug-kill logic is added to the island contents.

Component-envelope census (part + courtyard, mm², CALCULATED):

| Item | mm² |
|---|---:|
| USB2422 QFN-24 | 25 |
| 24 MHz crystal + 2 load caps | 12 |
| RBIAS | 1.5 |
| CRFILT + PLLFILT | 3 |
| 3 × VDD33 decouplers | 4.5 |
| reset + configuration straps (NON_REM ×2, CFG_SEL) | 7.5 |
| VBUS_DET divider + discharge | 4.5 |
| TPS2052B (designator TBD) + caps | 36 |
| validity source, worst candidate envelope | 16 |
| independent unplug-kill logic | 12 |
| S3 VBUS monitor divider/comparator | 3 |
| required test access (4 TP) | 8 |
| **subtotal, island-resident** | **≈133** |
| routing / spacing factor ×1.8 | **≈240** |

S3-local members (USB tuning R, recovery XOR pads) stay beside the S3 pads and are counted
there, not in the island. Result: the drawn Z3 envelope was under-bounded → **reserved
envelope enlarged to ≈20 × 13 mm** (x 63.5–84, y 20.5–33.5), drawn on the render. Its
topological location is unchanged; Z3 is **not closed** until the census parts land.

## R1-c · H3 relocation (physical cause: drawn collision + RF margin)

V1N defect **D-g** (now flagged on the V1N tab): the H3 Ø7 fastener envelope at (121, 31.5)
**overlaps the J3 connector body**, and its edge sits ~1.5 mm from the NFC reserve — a close
metal neighbour for a loop antenna. S1N-R1 moves H3 → **(119.5, 28.5)**: clears the J3 body,
raises the reserve margin to ~3 mm, and adds a **+2 mm RF exclusion margin** beyond the
fastener envelope (drawn). Explicitly **NOT RF-qualified** — conditional until the final
antenna geometry and enclosure hardware are modelled/measured.

## R1-d · Designators and exact identities (physical cause: schematic inventory compile)

- TPS2561 branch device = **U17-PWR2** (repaired-schematic designator; the floorplan alias
  "U4" is retired everywhere in V1N/S1N-R1).
- "F6-2052B" was a decision-fork label, not a designator: now **TPS2052B, DESIGNATOR TBD,
  PLACEHOLDER** (hub island not yet captured). USB2422 likewise DESIGNATOR TBD.
- Rule adopted: exact current schematic designators; exact MPNs; explicit placeholder status
  where no device is selected; **no floorplan-only alias that could be mistaken for schematic
  authority**. (V1/V2 archive tabs are left as historical record.)

## R1-e · LED termination split (physical cause: two distinct electrical segments)

The register previously conflated two drivers. Corrected:

1. **Segment 1 — RT1062 (FlexIO2) → U14/U15 input** (3.3 V): optional source treatment at the
   RT end (0R/33R, DNP default), test 0R mid-run.
2. **Segment 2 — U14/U15 output → R51/R52 → J2/J3 DATA** (5 V, the actual cable driver):
   source termination is **R51/R52, existing schematic designators, placed at the shifter
   outputs** — they never move to the RT end; the cable driver is never left unterminated.

Worksheet honesty marks: connector bulk "2 × 22 µF/ch" = **PROPOSED SCHEMATIC Δ** (current
capture holds a single bulk per rail); RILIM ≈1.5 A = **worksheet assumption, value TBD by
contract**; R_ON/DCR = datasheet-typical ESTIMATED. The study does not freeze schematic
values because they make a convenient worksheet.

## R1-f · Ball-map provenance discipline (physical cause: symbol repair history)

The project U6 symbol has a **documented repair history** (bad DCDC naming, wrong ball
landings). "Real ball map" is therefore split into three provenance classes:

- **Ball geometry** — measured from the BGA footprint grid: MEASURED.
- **Ball function** — symbol-derived: requires **NXP ball-map cross-check** before promotion.
- **Peripheral assignment** — requires the **frozen K1 pinmux contract**, which does not exist.

Provenance register (render carries the full table):

| Net | Ball | Native pad | ALT/daisy | NVCC | Authority |
|---|---|---|---|---|---|
| LPUART1 TX/RX | K14/L14 | GPIO_AD_B0_12/13 | RM lookup | NVCC_GPIO | **D-020 · RATIFIED FACT** |
| BOOT_MODE0/1 | F11/G14 | GPIO_AD_B0_04/05 | — | NVCC_GPIO | **D-020 · RATIFIED FACT** |
| SWD | E14/F12 | GPIO_AD_B0_06/07 | RM lookup | NVCC_GPIO | symbol + EVKB — cross-check |
| USB_OTG1 DP/DN | L8/M8 | fixed silicon | n/a | — | NXP DS — cross-check pending |
| K1BR ×5 | J1/J3/J4/K1(+IRQ) | SD_B0 field | RM-REQUIRED | NVCC_SD0 | **PROPOSED — NOT PINMUX-FROZEN** |
| SAI1 + PDM | G12/H11/H12/J14 · J13/L13 | AD_B1 field | RM-REQUIRED | NVCC_GPIO | **PROPOSED — NOT PINMUX-FROZEN** |
| LED_D0/D1 | D7/E7 | GPIO_B0_00/01 | RM-REQUIRED | NVCC_GPIO | **PROPOSED — NOT PINMUX-FROZEN** |
| MOTION_INT · THERM | L11 · K12/L12 | AD field (ADC) | RM-REQUIRED | NVCC_GPIO | **PROPOSED — NOT PINMUX-FROZEN** |

Where an assignment is open, the study reserves the escape corridor and says so.
"Measured from geometry" never implies "electrically ratified". The RT θ180 baseline itself
is conditional on the NXP cross-check.

## R1-g · USB DN1 return-path treatment (physical cause: 2T is not a transition design)

Added to the escape viewport: the D+/D− via pair with **two flanking GND return vias**
(L2↔L5 reference transfer at the transition), through-vias with no stub on this 1.6 mm
6-layer stack, pair skew matched by symmetric via placement, anti-pads per stack. Route
width/gap comes from the JLC impedance calculator against the selected stack —
**UNPROVEN** until that run exists; hub-side and RT-side breakout geometry is G4 work.

## Reran matrix & disposition

The Verdict tab reruns the same normalised matrix with the new rows (J1 mechanical basis,
D11 occupancy, provenance status) and the corrected evidence labels. The disposition row
formerly named ADOPTED is renamed **SELECTED INTO S1N STUDY**; **RATIFIED / PROMOTED are
reserved for actual authority changes and appear nowhere in this study**.

UNPROVEN now leads with: D-050 J1 bind (blocks all west-bay mechanical closure) ·
F6_VALIDITY_SOURCE + unplug-kill implementation · NXP ball-map cross-check · frozen pinmux
contract · full BGA escape · USB impedance geometry · thermal · LED-seam noise · enclosure
egress.

S1N-R1 is the recommended G4 entry floorplan and the sole candidate architecture.
Promotion of anything here requires the normal evidence path and a Captain ruling.
