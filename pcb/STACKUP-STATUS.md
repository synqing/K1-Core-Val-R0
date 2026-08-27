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
