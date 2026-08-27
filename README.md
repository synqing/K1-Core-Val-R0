# K1-CORE-VAL-R0

SpectraSynq K1 **hardware validation platform**. Not the production cost-optimised mainboard.

Experimental capability, observability, electrical correctness and future flexibility outrank
PCB area and prototype BOM cost. The board may grow east-west whenever additional area materially
improves RF, SI, PI, EMI, thermal behaviour, routing, measurement access or experimental flexibility.

## State

- Gate: **VAL-G0 — bootstrap complete**
- Open gate: **VAL-G1 — Option B versus Option C** (compute location)
- No EDA project, schematic, PCB, Gerber, BOM, CPL or manufacturing artefact exists.

## Reading order

1. `AGENTS.md` — operating doctrine for anyone working here
2. `authority/00-AUTHORITY-PRECEDENCE.md` — which document wins
3. `authority/02-Q0-B-vs-C.md` — the open architecture gate
4. `schematic/SINGLE-SHEET-CONTRACT.md` — the schematic rule

## Harnesses

    python3 harness/check_authority_consistency.py
    python3 harness/check_terminology.py

Both fail closed on missing or empty input. A check that cannot report non-zero input counts
does not print PASS.
