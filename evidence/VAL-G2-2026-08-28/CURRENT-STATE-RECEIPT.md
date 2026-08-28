# Current-state receipt — Voice PE specimen lane

Recorded: 2026-08-28. Read-only. No EasyEDA mutation in this acquisition.

SciPy / LED-eval tooling was not used. This lane has no colour dumps.

## Git

```text
HEAD          = 7f1d9d4313b8617a0663a743daa384d3ec7641b0
origin/master = 7f1d9d4313b8617a0663a743daa384d3ec7641b0   (after git fetch origin master)
branch        = master
HEAD..origin/master unique commits = 0
origin/master..HEAD unique commits = 0
working tree at acquisition        = clean
```

`origin/master` at this fetch **does** contain `schematic/single-sheet-qualification/FIXTURE-PLAN.json`. An earlier Captain check that the file was absent on `origin/master` is stale relative to this receipt.

Label: **not** `LOCAL_UNCOMMITTED_BASELINE`. The fixture plan is in the current `origin/master` tip. It is **retired historical inventory**, not a live G2.0A execution plan.

## FIXTURE-PLAN.json

```text
path     = schematic/single-sheet-qualification/FIXTURE-PLAN.json
exists   = yes
SHA256   = 3b610541b5be79379d212e5b9534031843e48fdc82e0b90c7c4e1751d5352d85
git blob = be6659c4a0edb87425843e6db4dedf87f2dd2761
```

Counts from the JSON (not from STATUS prose):

```text
plan_state                    = RETIRED_BY_D_042
option_c_estimated_symbols    = 181
planned_symbols               = 218
components                    = 218
nets                          = 119
blocks                        = 20
stress_rail_load              = 37
testpoint class               = 6  (TP1..TP6)
```

## Fixture checker (measured)

`python3 harness/check_single_sheet_qualification_plan.py` → **FAIL** (exit 1)

```text
FIXTURE_PLAN_COMPONENTS=218
FIXTURE_PLAN_BASELINE_COMPONENTS=181
FIXTURE_PLAN_FIXTURE_ONLY_COMPONENTS=37
FIXTURE_PLAN_NETS=119
FIXTURE_PLAN_ENDPOINTS=573
FIXTURE_PLAN_HIGH_FANOUT_NETS=11
FIXTURE_PLAN_EXPLICIT_WIRE_NETS=115
FIXTURE_PLAN_DOMAINS=11/11
FIXTURE_PLAN_MAJOR_ROLES=6/6
FIXTURE_PLAN_STATE=RETIRED_BY_D_042
HISTORICAL_THRESHOLD_DEFICITS=1
FAIL: passive device_uuid 6c37aeb54bf9f62bbe56e26c90f7ebd6 is assigned multiple values: 100nF,10uF
FAIL: passive device_uuid e6d727dcc615a5b2234ff9515369b026 is assigned multiple values: 1.33k,10k,3.48k
FAIL: fixture requires at least 120 named nets, found 119
SINGLE_SHEET_QUALIFICATION_PLAN=FAIL
```

This FAIL is a property of the **retired** G2.0A artefact. It is not a licence to invent nets or parts to chase the old 120-net floor.

## EasyEDA — live identity (read-only)

`get_current_context` at acquisition:

```text
friendlyName     = K1-Core-Val-R0
project UUID     = 64325d0e55e0435abd018defb0089a9b
schematic UUID   = cffcdb562c1b48d1a5214cfc263b6c90
page UUID        = 1435cb46f39e48c8a8aadbb84ca81603
pages            = 1 (P1)
documentType     = 1 (schematic page)
```

Qualification project `09e9c541fd3d404082d4b92e55ae5336` / page `1991698f35bf4c09b8de4bcf78bd2b7b` is **not** the live document. D-042 forbids further mutation of that UUID.

## EasyEDA — live inventory (read-only)

`list_schematic_primitive_ids {family: component}` count = **222**

`get_document_source`:

```text
sourceHash     = 472059:f2bbfe81
characters     = 472059
designators    = 221
unique NET attrs = 141
```

Designator suffixes on the live page (block-like tags, not fixture-plan block IDs):

```text
PWR1=20  PWR2=27  RTC=47  RTDBG=16  ESP=28
AUD=32   NFC=15   MOT=10  LED=12   VAL=14
```

Live test-point designators: `TP1-ESP`, `TP2-ESP`, `TP3-AUD`, `TP4-AUD`, `TP5-AUD`, `TP6-VAL`, `TP7-AUD`, `TP8-AUD`.

Compact census: `evidence/VAL-G2-2026-08-28/voice-pe-live-census.json`.

## Mutation gates

Qualification gate `evidence/VAL-G2-2026-08-28/EASYEDA-MUTATION-STATE.json`:

```text
state        = READY
project      = 09e9c541fd3d404082d4b92e55ae5336
document     = 1991698f35bf4c09b8de4bcf78bd2b7b
source_hash  = 44408:332ad2fb
validate     = READY (exit 0)
```

D-042 still forbids writes to that project even if the machine state says READY.

Canonical gate `evidence/VAL-G2-2026-08-28/canonical-core-val-r0/MUTATION-STATE.json`:

```text
state                      = READY
project                    = 64325d0e55e0435abd018defb0089a9b
document                   = 1435cb46f39e48c8a8aadbb84ca81603
recorded source_hash       = 472037:1225536d
live sourceHash            = 472059:f2bbfe81
last_closed_transaction_id = canonical-audio-capture-electrical-repair-2026-08-28
updated_at                 = 2026-08-28T03:39:02.996655+00:00
```

Live source hash has drifted from the last closed canonical record. That is an observation, not a write permit. This Voice PE exercise does not start a canonical mutation.

## What this receipt falsifies

The previous draft’s claims (`VAL-G2.0A = PLAN_PASS` at 182/219; `VAL-G2.0B` live on the qualification sheet) are **false against current territory**.

```text
VAL-G2.0A = RETIRED_BY_D_042  (181 baseline / 218 planned / checker FAIL)
VAL-G2.0B = TERMINATED_BY_D_042
VAL-G2.1  = IN PROGRESS on 64325d0e55e0435abd018defb0089a9b
```

## Lane file inventory

This lane is **16 files**, not eight artefacts.

```text
modified authority / status = 5
  STATUS.md
  architecture/VALIDATION-ARCHITECTURE.md
  authority/01-DECISION-REGISTER.md
  authority/05-SUPERSESSIONS.md
  sources/SOURCE-REGISTER.md

new markdown notes = 8
  docs/agent/VOICE-PE-SPECIMEN-VAL-R0.md
  CURRENT-STATE-RECEIPT.md
  VOICE-PE-CATEGORY-AUDIT.md
  VOICE-PE-ENGINEERING-REVIEW.md
  VOICE-PE-TEST-ACCESS-CENSUS.md
  VOICE-PE-FIXTURE-PLAN-DELTA.md
  VOICE-PE-SEMANTIC-REVIEW.md
  VOICE-PE-EASYEDA-SKIP.md

new live-census dumps = 3
  voice-pe-live-census.json
  voice-pe-live-context.json
  voice-pe-live-component-ids.json

new artefacts = 11
commit set     = 16
```

`box5-audit*` and other `canonical-core-val-r0/` job files are not this lane.
