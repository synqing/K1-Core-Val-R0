# K1-CORE-VAL-R0

SpectraSynq K1 **hardware validation platform**. Not the production cost-optimised mainboard.

Experimental capability, observability, electrical correctness and future flexibility outrank
PCB area and prototype BOM cost. The board may grow east-west whenever additional area materially
improves RF, SI, PI, EMI, thermal behaviour, routing, measurement access or experimental flexibility.

## State

- VAL-G1: **CLOSED — Option C selected, Option B deferred**
- VAL-G2: **READY**
- VAL-G2.0: **single-sheet qualification required first**
- VAL-G2.1: **canonical capture waits on VAL-G2.0 PASS**
- No EDA project, schematic, PCB, Gerber, BOM, CPL or manufacturing artefact exists.

## Reading order

1. `AGENTS.md` — operating doctrine for anyone working here
2. `authority/00-AUTHORITY-PRECEDENCE.md` — which document wins
3. `authority/02-Q0-B-vs-C.md` — the closed architecture ruling
4. `schematic/SINGLE-SHEET-CONTRACT.md` — the schematic rule
5. `schematic/single-sheet-qualification/TEST-PLAN.md` — required first operation in VAL-G2

## Harnesses

    python3 harness/check_authority_consistency.py
    python3 harness/check_terminology.py

Both fail closed on missing or empty input. A check that cannot report non-zero input counts
does not print PASS.

The two harnesses have a disposable negative suite, including the three SSCM-1 recovery-state
mismatches. This is a test of the existing checkers, not a third checker:

    python3 harness/test_negative_suite.py
