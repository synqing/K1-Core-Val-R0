# G3 floorplan doctrine — mechanical and RF direction

```text
STATUS = RECORDED_NOT_EXECUTED
BINDING = NO
CLASS = STUDY_INPUT
GATE = VAL-G3
RATIFIED = NOTHING_IN_THIS_FILE
```

Captain ruled this material **non-binding study** on 2026-08-28. It is recorded so the direction
is not lost between VAL-G2 and VAL-G3, and for no other purpose.

## How to read this file

Nothing here is a decision, a coordinate, a dimension, a keepout or a placement. Every item is a
question VAL-G3 must answer against real geometry, real escape pressure and the completed
schematic.

- A **hypothesis** is a starting position to be tested and possibly discarded.
- An **option** is one of several candidates, none selected.
- A **default** is what applies when nothing displaces it, and it is displaceable.

If a later document cites this file as authority for a position, that citation is wrong. Promoting
anything below requires a Captain ruling and a decision-register entry, per
`authority/00-AUTHORITY-PRECEDENCE.md`.

This file does not reopen D-022 (six layers baseline), D-028 (RT1062 package frozen) or the
ownership matrix.

## 1. USB-C edge placement — hypothesis

**Hypothesis:** both USB-C receptacles sit on a long edge, taken as the north edge, rather than on
a short edge.

The short-edge assumption it replaces was inherited, never tested, and is tombstoned in
`authority/05-SUPERSESSIONS.md`. This hypothesis is not its ratified successor; it is the position
VAL-G3 starts from and must justify or drop.

What VAL-G3 must test:

- escape pressure at the chosen edge, by the method in `pcb/floorplan/FLOORPLAN-STUDY.md`;
- distance from the 2.4 GHz zone for both pairs;
- whether the inlet power corridor and the J1 differential pair can coexist on one edge;
- the insertion-load path into the mounting scheme (section 5).

## 2. Two Type-C locations — from D-044

D-044 puts two USB-C receptacles on the board and no third. Each belongs near the part that owns
it, which turns connector placement into a placement constraint on both compute devices rather
than a free choice:

| Receptacle | Owner | Placement pressure |
| --- | --- | --- |
| `J1-PWR1` | RT1062 | Near the RT1062 USB OTG1 pins; also the board's 5 V inlet, so it carries the full trunk current |
| `J7-ESP` | ESP32_S3 | Near the ESP32_S3 native USB pins |

Both are on the long edge under the section 1 hypothesis. Both are kept away from the antenna
region. Both insertion loads are carried by the mounting scheme, not by the connector solder
joints.

Open tension VAL-G3 must resolve rather than assume away: `J7-ESP` wants to be near ESP32_S3,
ESP32_S3 wants to be at the RF edge, and USB wants to be away from the antenna. Those three pulls
are not automatically compatible.

## 3. ESP32-S3 RF placement options

Three arrangements from the Espressif PCB layout design guidelines. None is selected.

| Option | Arrangement | Standing |
| --- | --- | --- |
| **RF-A** | Antenna overhangs the board perimeter; module body on the board, radiator beyond the outline | Espressif's reference arrangement. The comparison baseline |
| **RF-B** | Edge-connected notch: the antenna sits in a cut-away that remains connected to the board edge | **The K1 candidate.** Keeps the radiator inside the mechanical envelope while retaining an edge relationship |
| **RF-C** | Fully internal cavity, board material on all four sides of the antenna | **Explicitly not a baseline.** Recorded only so it is not rediscovered as an idea. Enclosed on four sides is the worst of the three for detuning and clearance |

RF-B is a candidate because it is the arrangement that plausibly fits a K1 enclosure, not because
it has been shown to work. VAL-G3 evaluates it against RF-A with real clearance, real enclosure
material and the real antenna, and RF-A remains available if RF-B does not survive.

### Antenna clearance is not a PCB keepout rectangle

Espressif's 15 mm figure is an **end-product clearance recommendation** between the antenna and
surrounding enclosure or metal. It is not a keepout rectangle to be drawn on the PCB. The
`15 x 7 mm` keepout that circulated earlier was an invention and is tombstoned in
`authority/05-SUPERSESSIONS.md`; do not recreate it, and do not replace it with a different
invented rectangle.

The real requirement at VAL-G3 is a clearance volume derived from the selected module, the
selected arrangement and the actual enclosure — which is a mechanical study, not a number to
copy.

### USB away from the antenna

Espressif's guidance keeps USB and other high-speed traces physically away from the antenna
region. This applies to both receptacles from D-044, not only to `J7-ESP`. It is one of the
constraints that makes section 2's tension real.

## 4. Recessed side-button service bay

Direction: service and recovery controls live in a **recessed side bay** rather than as exposed
top-surface buttons.

Rationale to be tested at VAL-G3: recessing prevents accidental actuation of recovery and reset
in a validation platform that will be handled repeatedly, while keeping the controls reachable
without opening the enclosure. Depth, actuator style, count and position are all open.

This interacts with `contracts/debug-fabric.md` (D-018, requirements only) — the bay is where the
fabric's human-facing controls would surface if they surface physically at all.

## 5. Mounting — three-point triangle default, fourth support passive

**Default:** three mounting points arranged as a triangle.

**Plus:** a fourth location providing *passive support* — a pad, boss or rest that reacts load
without constraining the plate. **The fourth location is not a screw.**

Why this displaces the four-screw habit: three points are kinematically determinate, so the board
is located without being over-constrained and without a fourth screw fighting board flatness and
enclosure tolerance. The fourth location's actual job is reacting connector insertion load, and a
passive support does that without adding a constraint. Four screws were a habit, not a derived
load case; that default is tombstoned in `authority/05-SUPERSESSIONS.md`.

What VAL-G3 must derive rather than assume: the triangle's orientation relative to the two Type-C
insertion axes, whether the passive support belongs under the connector edge, and whether the
board's stiffness under insertion load actually needs it.

## 6. Non-rectangular board outline is permitted doctrine

The outline is an output of the placement and escape study, not an input to it.

`pcb/floorplan/FLOORPLAN-STUDY.md` already carries the method: identify the highest-pressure edge
or corridor, then change orientation, position or **outline** to relieve it, and only then
optimise total area. A non-rectangular outline — notch, step, cut-away — is a legitimate result of
that method, including the RF-B notch in section 3.

Two constraints on that freedom, both to be settled at VAL-G3: fabrication and routing cost of the
chosen profile, and the enclosure's own geometry. A shape that relieves escape pressure and
cannot be moulded around has relieved nothing.

## 7. What VAL-G3 owes this file

VAL-G3 closes by either promoting each item above into a decision with evidence, or recording why
it was dropped. An item that is neither promoted nor dropped has not been studied.

## Sources

- Espressif, ESP32-S3 PCB layout design guidelines —
  https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html
  (registered in `sources/SOURCE-REGISTER.md`)
- `authority/01-DECISION-REGISTER.md` D-044 (two USB-C receptacles), D-008 (RF zone mandatory)
- `authority/05-SUPERSESSIONS.md` — 2026-08-28 tombstones for the `15 x 7 mm` keepout, the
  four-screw default and the short-edge USB-C assumption
- `pcb/floorplan/FLOORPLAN-STUDY.md` — escape-pressure method
