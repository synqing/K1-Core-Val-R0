# Single-sheet qualification — test plan

Status: **VAL-G2.0A RETIRED_BY_D-042; VAL-G2.0B TERMINATED_BY_D-042**

```text
OPTION_C_SYMBOL_ESTIMATE = RESOLVED
VAL_G2_0_FIXTURE_DEFINITION = RETIRED_BY_D_042
VAL_G2_0_EDA_EXECUTION = TERMINATED_BY_D_042
```

> **HISTORICAL TEST PLAN — LIVE EXECUTION TERMINATED BY D-042.** Captain directly authorised
> canonical capture in `K1-Core-Val-R0` and prohibited further qualification-project mutation.
> The retained plan and measurements are evidence only; nothing below authorises another live
> write to the qualification UUID.

Corrected 2026-08-28 historical inventory: `N_estimated_symbols_option_C = 181`, retained stress
plan `N_test = 218`, named nets `119`. Removal of the non-existent ADC strap reduced the plan below
the old 120-net threshold. The plan is therefore retained evidence, not an accepted qualification
input and not permission to write to the retired project.

Purpose: prove that EasyEDA Pro can carry the complete K1-CORE-VAL board on one schematic sheet
before canonical one-sheet capture creates irreversible implementation reliance.

## Historical live-write control

VAL-G2.0B has no remaining authorised writes. The controls below record the policy that governed
the lane before D-042 terminated it. Canonical VAL-G2.1 writes use the separate canonical mutation
state and ledger named in `project.yaml`.

- If the state requires reconciliation, reconcile the live sheet read-only before a guarded write.
- Execute one circuit block and one visual stage per transaction.
- Placement, designation and wiring are separate transactions; no combined mode is permitted.
- Snapshot before begin, persist semantic read-back after the write, then capture and inspect a
  settled useful-scale screenshot.
- The next write remains blocked until structured visual evidence closes the current transaction.
- Screenshot capture/zoom failure, unreadable scale, unexpected content or semantic disagreement
  rejects the transaction. Only a declared repair/rollback transaction may follow.
- HISTORICAL (this lane is TERMINATED by D-042): the lock state that governed *this retired lane*
  was `evidence/VAL-G2-2026-08-28/EASYEDA-MUTATION-STATE.json` with `EASYEDA-MUTATION-LEDGER.jsonl`
  beside it. That lane now carries a `LANE-RETIRED` marker and must not be written.
  The **current** runtime lock state is the canonical gate named under `canonical_*` in `project.yaml`.
- Run `python3 harness/easyeda_mutation_gate.py validate` before actuation. Static documentation
  describes policy and results; it never overrides the machine state.

EasyEDA Pro documents no schematic area limit, but separately recommends fewer than 100
components per page and warns of editor lag beyond that. Those statements are not contradictory:
no hard limit, and a practical performance warning. K1-CORE-VAL will exceed 100 components, so
the test is mandatory.

## VAL-G2.0A — fixture-definition gate

This gate is required **before project creation or any EasyEDA write**. The numeric floor is not
a substitute for the selected architecture.

1. Resolve `N_estimated_symbols_option_C` from the current Option-C architecture, active
   contracts and primary support requirements.
2. Create `FIXTURE-PLAN.json` with every planned component role, quantity basis, domain, named
   net and component-pin endpoint.
3. Run:

       python3 harness/check_single_sheet_qualification_plan.py

4. Continue to EasyEDA only when it prints:

       SINGLE_SHEET_QUALIFICATION_PLAN=PASS

The checker fails closed when the plan is missing or parses zero components/nets. An unresolved
Option-C estimate is a hard stop; **never substitute the 200-symbol floor for an unknown
estimate**.

The fixture plan must also survive a whole-plan visual review before placement. That review asks
whether the topology resembles a real one-sheet circuit at normal reading scale, not whether a
list of counters reaches its thresholds.

## Fixture

Disposable project, named so it cannot be confused with the real design:

    K1-CORE-VAL-SINGLE-SHEET-QUAL

Exactly one large schematic page. **Size the fixture to Option C**, the worst case, because it
places both RT1062 and ESP32_S3, their support circuitry and the carrier peripherals on one board:

    N_test = max(200, ceil(1.20 x N_estimated_symbols_option_C))

Use representative symbol and wiring complexity. Not 200 identical resistors.

Minimum content:

- 200 representative electrical symbols
- 120 named nets
- 10 or more high-fanout power and control nets
- one visibly wired power tree
- at least one representative domain group of 20 or more symbols

Mock but electrically coherent domains for: RT1062 and support; ESP32_S3 and support; the bridge
interface; power entry and protection; buck and rails; LED power and data; audio, TDM and PDM;
USB; NFC; accelerometer; connectors; option links.

### Falsifiable semantic requirements

- Every baseline symbol represents a source-derived Option-C role. Any fixture-only stress symbol
  is identified explicitly, records its stress basis and may not duplicate a processor, major IC,
  support IC, power IC or clock merely to increase the count.
- Every named net has at least two distinct component-pin endpoints. A one-pin label or wire stub
  is a dangling name, not a net.
- Every high-fanout net has at least four endpoints, including an active/source IC and a real
  load, protection, connector or passive endpoint. Passive-only fanout does not qualify.
- The RT1062, ESP32_S3, audio front end, NFC front end and accelerometer each have planned
  power/ground and functional-interface endpoints.
- At least 20 nets use explicit visible wiring, every required domain contains explicit wiring,
  and the power-tree nets are explicitly wired. Net labels remain valid for long-distance
  cross-domain connections but may not be the only wiring technique.
- Names containing `QUAL`, `DUMMY`, `PLACEHOLDER`, `PADDING` or `REPLICA` may not be used to
  manufacture connectivity or component roles.
- The `create-schematic` plan-complete gate remains mandatory for disposable fixtures. “Mock”
  permits non-canonical values; it does not permit floating major devices or invented topology.

## Rejected attempt — 2026-08-28

Project UUID `09e9c541fd3d404082d4b92e55ae5336` contained the rejected fixture. Its electrical
content was deleted on 2026-08-28. EasyEDA refused a second project with the exact contract name
while that shell existed, so the same electrically empty container now holds one blank replacement
schematic/page. A second role-count placement attempt was stopped and removed after its first
screenshot showed repeated library-symbol grids and bad page composition. Current screenshot and
source read-back show 0 components, 0 texts, 0 rectangles, 0 wires and 0 nets. The project is not a
qualification result and no further content may be written until VAL-G2.0A passes.

See `evidence/VAL-G2-2026-08-28/INVALID-FIXTURE-RCA.md`.

## Objective responsiveness gate

Measure with screen recording or monotonic timestamps. Not prose impressions. Run each operation
five times. A failure is recorded with its measured duration and operation. Do not average away
a repeatable stall.

| Operation | Pass condition |
| --- | --- |
| Move a domain of 20+ symbols with attached wires | Editor accepts the next selection or edit within 2.0 s of mouse release, on every run |
| Add, move or delete a connected wire segment | Editor accepts the next selection or edit within 2.0 s, on every run |
| Pan and zoom continuously for 30 s | No individual UI freeze longer than 1.0 s |
| Annotate the full sheet | Completes within 60 s, no missing or duplicate designators |
| Run ERC | Completes within 60 s, no editor lock-up |
| Save, close, reopen | Reopens with exact symbol and net inventory |
| Update or import to a disposable PCB | Completes with exact schematic component and net counts |

## Integrity gate

- The machine-checked fixture plan matches the EasyEDA component and endpoint-level net inventory.
- After every mutation or visually atomic batch, capture and granularly inspect a settled screenshot
  before the next mutation. Preserve every screenshot and its intended-delta verdict.
- No components or nets disappear.
- Save and reopen is stable and repeatable.
- ERC completes.
- PCB import inventory matches the schematic exactly.
- No repeatable corruption.

## On failure

Failing this test does **not** authorise hierarchical sheets. Stop, report the measured failure,
and optimise the one-sheet implementation: symbol density, decorative content, wiring layout,
net-trunk use, tables and canvas organisation.

## Boundary

This test creates a disposable qualification project only. It does not create the final K1
EasyEDA project, schematic, PCB or any manufacturing artefact.
