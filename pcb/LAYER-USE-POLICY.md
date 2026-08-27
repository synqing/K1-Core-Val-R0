# Layer use policy

| Layer | Role |
| --- | --- |
| L1 / F.Cu | Components, critical local routes, USB and fast digital where appropriate, NFC matching |
| L2 | Solid uninterrupted GND reference |
| L3 | Primary power regions |
| L4 | Slow, control and secondary routing |
| L5 | Solid uninterrupted GND reference |
| L6 / B.Cu | Secondary components and signals referenced to L5 |

## Rules

- No AGND / DGND split. Separation is achieved by placement and routing over continuous ground.
- No fast signal crosses a power-region boundary without its actual reference remaining continuous.
- Fast routes stay adjacent to a solid ground reference.
- NFC matching stays over uninterrupted ground.
- RF antenna keep-outs apply across all six copper layers.
- High-current LED and power copper is implemented as deliberate regions, not router-default traces.
- Every layer change of a sensitive or fast net includes return-current consideration.
- Top and bottom ground pours require deliberate stitching to L2 and L5.
- No via strategy is accepted merely because DRC permits it.

---

## Dielectric spacing — what the assignment actually costs

`JLC06161H-3313` does not space its layers evenly. It forms three tightly-coupled pairs
separated by two wide cores:

| Adjacency | Separation |
| --- | --- |
| L1 ↔ L2 | 0.0994 mm |
| L2 ↔ L3 | 0.55 mm |
| L3 ↔ L4 | 0.1088 mm |
| L4 ↔ L5 | 0.55 mm |
| L5 ↔ L6 | 0.0994 mm |

Two consequences of the current assignment, both deliberate:

- L1 and L6 each sit 0.0994 mm from a solid ground plane. Fast signals on the outer layers have
  a close, continuous reference. This is the strongest property of the stack.
- L4 sits 0.1088 mm from L3 and 0.55 mm from L5 — roughly five times closer to split power than
  to solid ground. **That is why L4 is restricted to slow and control traffic.** The restriction
  is a consequence of the physical stack, not a style preference.

## The six-layer PDN-prioritised alternative

Recorded as an available option, **not a proposed change**.

| | Current baseline | PDN-prioritised alternative |
| --- | --- | --- |
| L1 | signal | signal |
| L2 | GND | GND |
| L3 | power | power |
| L4 | slow / control signal | **GND** |
| L5 | GND | GND |
| L6 | signal | signal |

The alternative converts the 0.1088 mm gap — the tightest plane-capable spacing in the stack —
into a power-ground pair, while both outer signal layers keep their close solid reference.

**The price is one routing layer.** The current baseline deliberately spends L4 as routing
capacity; the alternative spends it on the plane pair. Neither is wrong. The board decides.

### What the plane pair is and is not worth

`0.55 / 0.1088 = 5.06`, so the alternative gives approximately **five times the distributed plane
capacitance per unit overlapping area**, assuming comparable dielectric constant. It does **not**
follow that the PDN is five times better.

Absolute values are modest. At εr ≈ 4.2:

| Overlap | at 0.1088 mm | at 0.55 mm |
| --- | --- | --- |
| 1000 mm² | 0.342 nF | 0.068 nF |
| 4000 mm² | 1.367 nF | 0.270 nF |

Against local MLCC decoupling in the 100 nF to 10 µF range, that is small in bulk terms. Its
real value is **very low inductance at high frequency**, not capacity. And because L3 carries
split rail regions rather than one monolithic supply, the effective overlap is only each rail
island's area over L4 — not the whole board.

### Comparing the two, when the time comes

Capacitance alone does not decide it. Evaluate both electrical and routing consequences:

PDN impedance against frequency; rail transient droop; plane overlap area by rail; required MLCC
population; total routed track length; total via count; number of fast-signal layer transitions;
route-completion margin; escape pressure; ground-return quality; EMI susceptibility.

Moving all slow and control routes off L4 may create a worse routing or EMI problem than the one
the plane pair solves. That must be quantified, not assumed.
