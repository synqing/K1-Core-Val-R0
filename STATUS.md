# STATUS

Updated: 2026-08-27

| Lane | State |
| --- | --- |
| VAL-G0 bootstrap | COMPLETE |
| VAL-G1 Option B vs C | **CLOSED 2026-08-27 — Option C selected, Option B deferred** |
| VAL-G2 single-sheet schematic | **UNBLOCKED — next design work** |
| VAL-G3 envelope and floorplan | NOT STARTED |
| VAL-G4 placement and locks | NOT STARTED |
| VAL-G5 stack, rules, planes | NOT STARTED |
| VAL-G6 route and DRC | NOT STARTED |
| VAL-G7 fabrication-output proof | NOT STARTED |
| VAL-G8 bring-up | NOT STARTED |
| Single-sheet qualification | PLANNED, NOT RUN |
| SSCM-1 recovery pass | NOT RUN |
| Audio L0 software SRC | NOT STARTED |
| Audio L1 ADC6120EVM | NOT STARTED |
| Audio L2 RT1062 raw SAI | NOT STARTED |
| Current-S3 baseline | NOT STARTED |

## Nothing is blocked

RT1062 package is FROZEN: `MIMXRT1062DVJ6B`, 196-ball, 12 x 12 mm, 0.8 mm pitch (D-028).
Next design work is VAL-G2: the complete single-sheet native schematic built around it.

## Now unblocked by VAL-G1 closure

The domain-interaction matrix can be instantiated for Option C.
Board outline and floorplan follow once the package is frozen.

## Carried forward as OPEN

Option C BGA escape, six-layer routability, and any HDI/VIPPO requirement. Not proven.
VAL-G3 gate item, and only once the real schematic exists. **No BGA escape analysis and no
CopperPilot run before VAL-G2 completes** — there is no circuit for it to route.

## Not blocked

All three audio validation levels and the current-S3 baseline. None touch the Core.
