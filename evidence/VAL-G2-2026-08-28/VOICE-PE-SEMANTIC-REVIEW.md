# Semantic review — Voice PE specimen transfer

Date: 2026-08-28. Machine PASS of authority/terminology is required. Machine PASS of the
retired fixture checker is **not** required and was not chased.

## What this lane added

- Specimen note, category audit, engineering review, test-access census, fixture-delta note.
- `SOURCE-REGISTER.md` Nabu Casa / CERN-OHL-P v2 row (patterns-only).
- Decision **D-043** and matching supersession.
- Test-access doctrine in `architecture/VALIDATION-ARCHITECTURE.md`.
- STATUS pointer only. No MISSION, USB, LED, mic, debug-fabric, or layer-policy edits.

## Provenance check

| Question | Finding |
| --- | --- |
| Any Voice PE MPN added to FIXTURE-PLAN or EasyEDA? | **No.** JSON SHA unchanged. No EasyEDA write. |
| USB shield 1 MΩ ∥ 1 nF present as a frozen K1 part? | **No.** CANDIDATE in specimen only. |
| LED eFuse 0402 0R bypass symbol? | **No.** Capability OPEN. |
| Cargo-cult 0R on USB pairs or NFC RF? | **No.** Explicitly forbidden. |
| Option-C estimate driven by ~439 Voice PE footprints? | **No.** Still 181 / 218. |
| Test-access rows name the mechanism? | **Yes.** Header / series pad / existing TP / no casual stub. |
| Architecture reopened (Option C, XU316, M.2, single-S3)? | **No.** D-043 says closed. |

## Checkers (this close)

```text
check_authority_consistency.py           = PASS
check_terminology.py                     = PASS
test_single_sheet_qualification_plan.py  = 30 tests OK
check_single_sheet_qualification_plan.py = FAIL (retired artefact; unchanged)
FIXTURE-PLAN.json SHA256                 = 3b610541b5be79379d212e5b9534031843e48fdc82e0b90c7c4e1751d5352d85
```

The live-plan FAIL is duplicate `device_uuid` values and 119 nets versus the historical
120-net floor. That FAIL is recorded in `CURRENT-STATE-RECEIPT.md`. Inventing nets or parts
to print PASS is forbidden.

## EasyEDA

Qualification project: D-042 stop. Canonical project: this lane started no mutation
transaction. Gate files were observed, not written.

## SciPy

Unused.
