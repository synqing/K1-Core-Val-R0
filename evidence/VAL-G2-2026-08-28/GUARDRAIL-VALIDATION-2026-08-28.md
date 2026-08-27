# EasyEDA guardrail validation — 2026-08-28

## Scope

This record validates the documentation and mutation-control machinery only. No EasyEDA API/MCP
write was issued while installing or validating these controls.

## Historical failing baselines

- The preserved first generator targeted literal 200-symbol/120-net floors and manufactured
  one-ended passive stubs.
- The second rebuild again used role-count placement and uniform grids; the first useful screenshot
  arrived after 81 components.
- The visual log records later continuation after an unusable-scale screenshot and explicit stop.
- The initial router structural contract had five failing cases before its amendment.
- The first mutation-gate test run failed because the gate module did not yet exist.

## Live contradiction found by the new validator

The ledger originally contained this unexplained transition:

```text
STATE_RECONCILED source_hash = 222135:c6b343ed
MUTATION_BEGAN pre_source_hash = 222137:a9bf996e
```

The full replay validator rejected that chain. The state was quarantined without an EasyEDA write.
An external agent then automatically reconciled the quarantine and resumed mutations. I incorrectly
classified that operator as unowned and invoked the incident freeze. Captain confirmed it was the
authorised productive operator, so I released the freeze immediately. The durable correction is that
operator authority must be established before containment; this evidence file does not claim the
current runtime phase.

## Final deterministic checks

| Check | Result |
| --- | --- |
| `python3 harness/test_easyeda_mutation_gate.py` | 21 behavioural cases succeeded |
| `python3 harness/easyeda_mutation_gate.py validate` | state/ledger replay exercised, including hash-chain rejection and incident containment |
| `python3 harness/test_single_sheet_qualification_plan.py` | 30 behavioural cases succeeded |
| `python3 harness/check_single_sheet_qualification_plan.py` | 219 components, 120 nets, 576 endpoints parsed |
| `python3 harness/check_authority_consistency.py` | 7 authority files, 21 ownership rows, 9 contracts; zero contradictions |
| `python3 harness/test_negative_suite.py` | 21 deliberate authority corruptions rejected |
| `python3 harness/check_terminology.py` | 31 files and 1,897 lines scanned; zero violations |
| Python AST parse of gate, gate tests and fixture executor | succeeded |
| `git diff --check` | no whitespace errors |
| global `easyeda-router/test_contract.py` | 6 structural contract cases succeeded |

## Behavioural controls exercised

The mutation tests cover missing state, blocked state, missing snapshot, stale/wrong identity,
simultaneous begin attempts, unchanged source, missing visual closure, non-PNG evidence, too few
inspection checks, accepted evidence containing a defect, rejection/repair behaviour, source/ledger
tampering, quarantine recovery, non-releasable incident freeze and repository wiring.

## Visual evidence boundary

The existing reconciliation screenshot
`screenshots/reconcile-live-sheet.png` was inspected during this control session. It shows the named
qualification project and one populated schematic page at whole-sheet scale. It does not resolve the
subsequent source-hash discontinuity and therefore cannot reopen actuation.

No new screenshot was created because no EasyEDA mutation was performed by this control work.
