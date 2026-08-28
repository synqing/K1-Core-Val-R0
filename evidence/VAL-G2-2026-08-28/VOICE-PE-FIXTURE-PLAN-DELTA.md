# Fixture-plan delta — Voice PE specimen lane

Date: 2026-08-28.

`schematic/single-sheet-qualification/FIXTURE-PLAN.json` was **not amended**.

## Why zero JSON mutation

- Receipt SHA256 remains `3b610541b5be79379d212e5b9534031843e48fdc82e0b90c7c4e1751d5352d85`.
- Plan state is `RETIRED_BY_D_042`. D-042 forbids further qualification-project mutation.
- Phase 3 / 4 adopted **doctrine** (test-access census) and left USB shield and LED bypass as
  **CANDIDATE**. No new source-derived K1 part, ratified option symbol, or named stress part
  was added.
- Voice PE footprint count (~439) is forbidden as an estimate driver.

## Estimate invariant (unchanged)

```text
option_c_estimated_symbols = 181
planned_symbols            = 218
stress_rail_load           = 37
N_test                     = max(200, ceil(1.20 × 181)) = 218
```

K1BR series footprints stay `TUNE` / representative. No ohms freeze. No USB `1 MΩ ∥ 1 nF`.
No LED 0402 0R bypass symbol.

Test-access work is a census of **existing** mechanisms:
`VOICE-PE-TEST-ACCESS-CENSUS.md`. It does not add TP rows to the retired JSON.

Do not invent a 120th net to chase the historical floor.
