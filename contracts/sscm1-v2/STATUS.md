# SSCM-1 status

```text
SSCM1_RECOVERY_STATE = COMPLETE_NOT_FOUND
SSCM1_V1_AUTHORITY = UNRECOVERED_UNFROZEN
SSCM1_V2 = REQUIREMENTS_DRIVEN_REPLACEMENT
```

| Item | State |
| --- | --- |
| SSCM-1 v1.0 pin map (2026-08-14) | **UNRECOVERED — treat as UNFROZEN** |
| Recovery pass | **COMPLETE_NOT_FOUND** |
| SSCM-1 v2 requirements | REQUIREMENTS-DRIVEN REPLACEMENT; DRAFT while Option B is deferred |
| Scoring of Option B | DEFERRED — interface feasibility UNPROVEN |

## Why v1.0 is not frozen

The 14-Aug note recorded a pin budget: M.2 B-key 2280, 22 GND, 4x +5V, 2x +3V3, 2x AUX,
7 reserved (3 differential pairs plus 1 GPIO), 30 signal, 75 positions, notch 12-19, 67 active.

The frozen interface specification behind that budget was not recovered. `K1.hardware` contains
historical K1-M2B/module architecture fragments and a placeholder mapping, but none is the missing
SSCM-1 v1 contract. The prior `SpectraSynq-Instrument-Spine` search could not be reproduced in the
current review because that checkout was unavailable. The recorded DualMCU ingest contains no
SSCM-1 interface authority.

A frozen contract that cannot be located is functionally unfrozen. The bounded recovery pass is
complete and did not recover it. V2 is authored from present requirements rather than
reconstructed from scraps.

## Method

Start from an ownership-boundary requirements sheet — what must cross carrier to module, and
under what electrical conditions. Do not start from a pin map. A pin map written before the
requirement set is how a module standard fails at its second product.
