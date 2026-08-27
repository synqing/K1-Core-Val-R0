# Stack-up status

Status: **PREFERRED CANDIDATE — NOT ORDER-FROZEN**

Baseline: 1.60 mm, six copper layers. The former 1.00 mm-only assumption is retired. No agent may
infer that a K1 mainboard carrying a MEMS microphone must therefore be 1.00 mm.

Candidate: `JLC06161H-3313`, 1 oz outer / 0.5 oz inner.

Construction as listed by JLCPCB for this stack:

| Sequence | Material | Thickness |
| --- | --- | --- |
| F.Cu | copper | 35 um |
| prepreg | 3313 x1 | 0.09940 mm |
| L2 | copper | 15.2 um |
| core | FR-4 | 0.55 mm |
| L3 | copper | 15.2 um |
| centre prepreg | 2116 x1 | 0.1088 mm |
| L4 | copper | 15.2 um |
| core | FR-4 | 0.55 mm |
| L5 | copper | 15.2 um |
| prepreg | 3313 x1 | 0.09940 mm |
| B.Cu | copper | 35 um |

## Not yet frozen

Controlled-impedance dimensions are not frozen until the actual layer count, copper weights and
impedance configuration are selected in JLCPCB's live calculator and order workflow. USB
geometry is recalculated against the selected stack, not carried over.

---

## Layer-count ruling

| | |
| --- | --- |
| **6 layers** | **Baseline.** Current policy in `LAYER-USE-POLICY.md`. |
| **8 layers** | **Conditional escalation.** Available, not selected. Requires evidence from the post-VAL-G1 floorplan. |
| **10 layers** | **No.** Not in the current design space. Not investigated unless 8 is first shown insufficient. |

Six layers is not a compromise here: it gives two solid ground references, a dedicated power
layer and three routing surfaces, for a design with no external DDR bus, no PCIe and no
multi-gigabit SERDES.

### What is not a reason to add layers

Professional appearance. Component count. Having two processors. Audio being sensitive — that is
won by placement, continuous return paths, local filtering and controlled current loops. NFC
being RF — the matching network wants compact symmetric geometry over uninterrupted ground, and
buried layers do not rescue a poor front-end layout. "It is a validation board so give ourselves
everything" — unnecessary complexity makes experiments harder to interpret, not easier.

### Escalation triggers

Move 6 → 8 only if the actual post-VAL-G1 floorplan demonstrates one or more:

- RT1062 escape cannot be completed without routing important fast nets over split power.
- Audio clocks, the bridge, USB and LED fast edges compete for the same clean reference corridor.
- L3 becomes excessively fragmented by the rail set.
- Six-layer routing forces an unreasonable number of fast-signal layer changes.
- Option C placement proves routing-density constrained despite board lengthening.
- SI or EMI analysis identifies a return-path or coupling problem an extra plane pair genuinely fixes.
- A dedicated additional shield or reference layer around a sensitive subsystem is deliberately required.
- **PDN:** simulated or measured rail impedance, transient response or noise cannot meet the
  defined rail target across the required frequency and load range.

### PDN remedy order

PDN demand is governed by transient-current spectrum, digital rise and fall times, processor and
radio load steps, decoupling ESL/ESR and anti-resonances, plane geometry and rail target
impedance. **Interface clock rates alone cannot establish it.** No present evidence shows the
design requires a tighter embedded power-ground pair; that must be determined from target-impedance
and transient evidence, not from bus speeds.

When it is investigated, work in this order:

1. Component placement, current-loop geometry and local decoupling.
2. Capacitor value and package mix; remove harmful anti-resonances.
3. Six-layer power-region geometry and via distribution.
4. Evaluate the `L3 = power / L4 = GND` six-layer reassignment, quantifying **both** the PDN
   improvement and the lost-routing cost.
5. Only if the six-layer remedies fail materially, evaluate an 8-layer stack.

### What 8 layers actually costs

A new stack, higher fabrication complexity and bare-board cost, more lamination and registration
constraints, more elaborate SI/PI analysis, and more opportunity to misuse layers.

**Via count is not on that list.** Via count is an outcome of routing architecture: additional
routing channels may reduce congestion-driven layer hops as easily as they add transitions.

### Area before layers

Where the choice is a longer board on six layers with clean zoning against a shorter board on
eight with compressed placement, take the longer board. XY area is electrically inexpensive.
Z-axis routing cannot fix poor component adjacency, RF proximity, buck-to-audio spacing, awkward
connector orientation, thermal crowding or inaccessible probe points.

## Assembly service — not a layer-count question

JLCPCB Economic PCBA supports 2, 4 and 6 layers, **single-sided placement only**, 2–50 pieces.
Standard PCBA supports 1–32 layers and single **and double-sided** placement.

K1-CORE-VAL is authorised for double-sided component placement, which commits it to Standard
PCBA **regardless of whether it is 6, 8 or 10 layers**. Any earlier argument that six layers
preserves Economic eligibility is withdrawn: the placement decision already settled the service
class, and layer count does not change it.
