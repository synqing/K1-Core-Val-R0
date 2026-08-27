# SSCM-1 status

| Item | State |
| --- | --- |
| SSCM-1 v1.0 pin map (2026-08-14) | **UNRECOVERED — treat as UNFROZEN** |
| Recovery pass | NOT RUN — one bounded attempt authorised |
| SSCM-1 v2 requirements | DRAFT — see `REQUIREMENTS.md` |
| Scoring of Option B | BLOCKED until v2 requirements exist |

## Why v1.0 is not frozen

The 14-Aug note recorded a pin budget: M.2 B-key 2280, 22 GND, 4x +5V, 2x +3V3, 2x AUX,
7 reserved (3 differential pairs plus 1 GPIO), 30 signal, 75 positions, notch 12-19, 67 active.

The interface specification behind that budget could not be located in `K1.hardware` or in
`SpectraSynq-Instrument-Spine`; every search hit was footprint-library noise. The DualMCU
firmware repository contains no SSCM-1, M.2 or carrier reference at all, so the 24-Aug processor
ruling was written without reference to the module architecture.

A frozen contract that cannot be located is functionally unfrozen. Recovery gets one bounded
pass. If it does not surface, v2 is authored from present requirements rather than reconstructed
from scraps.

## Method

Start from an ownership-boundary requirements sheet — what must cross carrier to module, and
under what electrical conditions. Do not start from a pin map. A pin map written before the
requirement set is how a module standard fails at its second product.
