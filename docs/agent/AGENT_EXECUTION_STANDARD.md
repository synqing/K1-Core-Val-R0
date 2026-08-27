# Agent execution standard

This document is the durable canon referenced by the repository `AGENTS.md`. Repository-specific
authority and Captain's current instructions override a general rule when they are more specific.

## Prime law

The brief is the floor, not the ceiling. Faithfully reproducing weak, fabricated or mechanically
compliant work is failure.

Every deliverable must satisfy all three bars:

1. **Fidelity:** obey authority, provenance, repository boundaries, ownership and safety.
2. **Craft:** produce a coherent artefact whose composition and operation survive direct inspection.
3. **Value:** create shipped value, decision value or reusable machinery.

## Evidence hierarchy

Use the strongest evidence available. From strongest to weakest:

1. persisted artefact inspected through the product's authoritative surface;
2. independent semantic extraction from that persisted artefact;
3. deterministic validation against a separately authored contract;
4. tool return payload or generated manifest;
5. agent prose.

Lower layers cannot override disagreement at a higher layer. API success, source hashes and object
counts prove only the narrow fact they measure.

## Mandatory operating sequence

1. Read repository authority and current status.
2. Verify live identity: checkout, branch, remote, target project/document/device and current state.
3. State the intended bounded delta and its acceptance evidence.
4. Snapshot before mutation.
5. Make one reversible, reviewable delta.
6. Read the persisted semantic result from outside the mutation return path.
7. Inspect the user-visible result with the appropriate instrument.
8. Compare both observations with the intended delta.
9. Record the result before another mutation.
10. Stop and repair or roll back on any disagreement.

## Non-negotiable rules

- Never turn a minimum threshold into the design target.
- Never substitute counts, hashes or generated paperwork for the property being qualified.
- Never invent source truth to unblock actuation.
- Never continue the same failed mechanism with different quantities or formatting.
- Never hide multiple visually meaningful stages inside one batch.
- Never report a state that was not verified live when live verification was cheap and safe.
- Never change a checker or rubric and use the changed version to certify the artefact without
  proving the checker still rejects known-bad cases.
- Never make Captain perform routine repair, file work or instrumented inspection that an agent can
  perform.
- Never create sibling worktrees or project folders unless Captain authorises the exact path.
- Never mutate EasyEDA without following `EASYEDA-EXECUTION-CANON.md`.

## Map and territory

A plan, contract, fixture manifest or model is a map. The saved artefact and its visible behaviour
are the territory. The map defines what should exist; independent read-back and inspection establish
what does exist.

Neither is sufficient alone:

- map without territory permits paper designs and vacuous gates;
- territory without map permits attractive but wrong artefacts;
- a claim is admissible only when map-to-territory comparison can fail and has been run.

## Failure response

When evidence contradicts intent:

1. stop further mutations;
2. preserve the pre-write snapshot, failed result and diagnostic evidence;
3. classify whether the fault is plan, tool, actuation, evidence or judgement;
4. repair or roll back the smallest failed delta;
5. strengthen the controlling source only when the failure exposes a reusable gap;
6. prove the strengthened control rejects the historical bad case; and
7. resume from a newly observed state, never from the previous claim.

## Harness rules

- A checker that parses zero relevant records must reject.
- A checker is not proven until a known-good control is accepted and known-bad mutations are
  rejected for the intended reason.
- Inputs used to generate an artefact cannot independently certify that artefact.
- Evaluation rules are locked during an execution. Changes require rerunning historical controls.
- Durable state belongs in repository artefacts, not chat history.
- Rejected attempts remain available as evidence so future agents do not repeat them.

## Completion report

Every stop report states, in plain English:

- what happened;
- what is true now;
- what remains;
- files changed;
- commands or calls executed;
- validation results;
- screenshots, renders and logs;
- blockers; and
- the numbered path to the actual close condition.

## Task-specific canon

- EasyEDA mutation and schematic execution:
  `docs/agent/EASYEDA-EXECUTION-CANON.md`
- EasyEDA guardrail design:
  `docs/agent/2026-08-28-easyeda-execution-guardrail-design.md`
- Complete incident record:
  `evidence/VAL-G2-2026-08-28/SESSION-DEBRIEF-2026-08-28.md`
