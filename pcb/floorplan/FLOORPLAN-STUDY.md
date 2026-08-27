# Floorplan study

Status: **NOT STARTED — blocked on VAL-G1**

One contraction study. Not three parallel envelope documents: three lanes produce one answer
three times, and the method below already contains the comparison.

## Method

1. Begin with an intentionally generous east-west outline.
2. Place every domain according to physics, mechanics and the interaction requirements.
3. Establish clean routing corridors and return paths.
4. Contract the east-west outline incrementally.
5. Stop at the first material compromise.
6. Record: selected length; last passing length; first rejected length; the exact reason it failed.

Multiple EasyEDA snapshots or screenshots during the contraction are evidence from one method,
not three separately maintained designs.

## Placement priority

1. Enclosure and mechanical constraints
2. Compute and RF architecture
3. Fixed external connectors
4. Power entry
5. Buck and high di/dt block
6. Shunt and INA226 measurement
7. LED power and data
8. NFC RF island
9. Audio interfaces
10. Microphone flex exit
11. Accelerometer
12. Service and test
13. Remaining passives

Compute placement is physics-first: position from RF and mechanical requirements, peripherals
second, GPIO assignment last.

## Prerequisite

`architecture/DOMAIN-INTERACTION-MATRIX.csv` must exist first, and it cannot be instantiated
until VAL-G1 selects Option B or Option C — the meaning of each relationship differs between
them. Conditional entries live in `authority/02-Q0-B-vs-C.md` until then.

---

## Prior-art method: escape-pressure-driven outline synthesis

Source: `SpectraSynq-K1-CORE-Final`, decisions D006 and D007 (2026-08-24). That lane is
**historical design evidence — not a PCB source and not a work target**. Its `.pcb-lane` is
marked dead. Nothing below imports its copper, coordinates or stack.

A prior K1 floorplan study found the primary routing constraint was not total board area but
**local signal-escape density at a constrained board edge**. It responded by altering the PCB
outline around the bottleneck instead of forcing placement into a preselected rectangle. That
was the first proposal in that project to identify the actual constraint and shape the board
around it.

> **PRIOR-ART / NOT APPLICABLE TO K1-CORE-VAL WITHOUT RE-DERIVATION.**
> The stepped-T geometry, all dimensions, coordinates, signal counts and density figures from
> D006/D007 are void here. Processor ownership, signal count, layer count and placement
> constraints have all changed. Only the method transfers.

### The method

1. Derive the actual required escapes from each physically significant package or connector edge.
2. Measure usable routing width after keep-outs, pads, mechanical exclusions and power corridors.
3. Identify the highest-pressure edge or corridor.
4. Change component orientation, component position or PCB outline to relieve that bottleneck.
5. Only then optimise total PCB area.

### Escape pressure, not raw density

Raw density — `required crossings / usable mm` — is a first-order congestion indicator only.
Ten slow GPIO are not equivalent to a USB pair, three synchronous audio clocks, two fast-edge
LED outputs and an RF boundary. Compute both quantities.

Weight each crossing by what it actually demands. Indicative starting weights; the geometry
sets the final values:

| Crossing class | Relative routing pressure |
| --- | --- |
| Slow GPIO / I2C | 1 |
| Interrupt / control | 1 |
| UART | 1 |
| LED fast-edge output | 2 |
| PDM CLK/DATA group | 2 |
| MCLK / BCLK / FSYNC / SDOUT group | 2–3 |
| USB differential pair | one coupled route, high constraint |
| High-current power | separate power-corridor calculation, not an escape |
| RF path | not an ordinary escape at all |

Record alongside the numbers:

- usable routing layers at that corridor;
- unavoidable via count;
- whether a continuous ground reference exists beneath;
- required trace width and spacing;
- connector ground interleaving;
- whether the escape competes with a power corridor;
- whether the escape region sits beside an RF keep-out.

### Every proposal states its cost

No placement or outline proposal is complete with benefit alone. Each move reports both, so a
locally attractive choice cannot hide its second-order damage:

| Proposal | Benefit | Cost |
| --- | --- | --- |
| Rotate RT1062 90 degrees | LED outputs escape directly west | audio clocks lengthen |
| Move buck east | isolates microphone and audio | lengthens 3V3 distribution |
| Widen board | clears NFC and audio corridors | added area |
| Central module connector | short peripheral fanout | two-way routing congestion |
| ESP32_S3 at south edge | antenna exposure | bridge and service USB lengthen |

If nothing got worse, the analysis is not finished.

### Application to VAL-G1

The method applies to Option B and Option C before either exists as copper, provided it runs on
explicitly supplied architecture assumptions and never on a claimed live board.

**Option B** — escape pressure at the SSCM-1 connector. The question is not "do 24 signals fit
on 30 pins". It is whether those functional groups can cross with appropriate grounds,
adjacency, signal integrity and contingency without making the connector the most constrained
object in the product.

**Option C** — which RT1062 package edges carry the most pressure from west-side LED outputs,
audio, the bridge, USB experiments and service connections. That can settle RT1062 orientation
before a single component is placed.
