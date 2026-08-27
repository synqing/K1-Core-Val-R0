# EasyEDA execution guardrail design — 2026-08-28

Status: authorised implementation design

## Objective

Prevent an agent from making a second EasyEDA write until the preceding write has all of the
following bound to the same project, document and transaction:

1. a pre-write source snapshot;
2. a declared, bounded visual delta;
3. a post-write semantic read-back;
4. a settled screenshot at a useful scale;
5. a granular visual inspection record; and
6. an accepted or rejected disposition.

The guard must also prevent primitive-count targets, generic symbol substitution, decorative
scaffolds and multi-stage bulk execution from masquerading as an electrical schematic.

## Baseline failures this design must stop

- A 200-symbol fixture derived from a numeric floor instead of architecture.
- 120 one-ended named stubs counted as nets.
- Passive-only fanout counted as representative topology.
- Functional IC quantities duplicated without source basis.
- Generic device fallbacks and uniform grids used for placement.
- A whole sheet written before the first meaningful visual inspection.
- A second role-count build attempted after the first failure had already identified that model as
  invalid.
- Placement, designation and wiring grouped into one execution path without an evidence stop between
  visual stages.
- A semantic read-back used as a substitute when the screenshot was empty, hung, too distant or
  otherwise unable to show the requested delta.
- Work continuing after the evidence log itself recorded a process violation.

## Options considered

### A. Add more prose only

Low implementation cost, but already disproven. The session contained relevant prose rules before
the failure, and agents still optimised counts and delayed visual inspection.

### B. Canon + executable write lock + executor integration + router amendment

Selected. It places the control at the narrowest current mutation surface while keeping source
truth, visual judgement and recovery explicit. It also remains auditable without changing the
EasyEDA host or stealing desktop focus.

### C. Modify the global EasyEDA bridge to refuse all writes until screenshot acknowledgement

Potentially stronger across projects, but the bridge cannot itself prove that an external screenshot
shows the intended delta, and a global lock could disrupt unrelated repositories. This remains a
future bridge feature after the repository state machine has proven the contract.

## Selected architecture

### Durable surfaces

| Surface | Artefact | Rule |
| --- | --- | --- |
| Locked canon | `docs/agent/EASYEDA-EXECUTION-CANON.md` | Agents read; changes require evidence and tests |
| Write-lock state | active evidence directory `EASYEDA-MUTATION-STATE.json` | One current state; never hand-edited during a transaction |
| Append-only events | active evidence directory `EASYEDA-MUTATION-LEDGER.jsonl` | Begin, mutation, inspection and recovery events append only |
| Electrical plan | `FIXTURE-PLAN.json` | Must clear the semantic plan checker before actuation |
| Actuator | `execute_fixture_block.py` | One block and one visual stage per invocation |
| Visual evidence | PNG plus structured inspection JSON | Screenshot and semantic read-back are both mandatory |
| Router | global `easyeda-router` skill | Routes every EasyEDA task into this contract |

### State machine

```text
FROZEN_INCIDENT  (no automatic release path)

BLOCKED_RECONCILIATION
        |
        | read-only live census + useful screenshot + inspection
        v
      READY
        |
        | begin(normal), after snapshot and declared delta
        v
    IN_FLIGHT
        |
        | post-write semantic read-back
        v
AWAITING_EVIDENCE
        |                         |
        | accepted                | rejected
        v                         v
      READY                    REJECTED
                                  |
                                  | begin(repair) only
                                  v
                              IN_FLIGHT
```

No normal write is possible from `FROZEN_INCIDENT`, `IN_FLIGHT`, `AWAITING_EVIDENCE`, `REJECTED`
or `BLOCKED_RECONCILIATION`. Unlike ordinary reconciliation, an incident freeze cannot be released
by an execution agent. It is appropriate only after operator ownership is genuinely unresolved;
concurrent Captain-authorised work must not be frozen.

### Transaction boundary

A transaction is one visual stage for one complete circuit block:

- place the complete block;
- designate the already placed block;
- wire the already designated block; or
- repair/roll back one rejected delta.

Placement, designation and wiring are separate transactions because each changes what the canvas
must show. A convenience `all` mode is forbidden.

### Evidence contract

The structured visual record contains:

- transaction, project and document identities;
- screenshot path and dimensions;
- settled-state declaration;
- inspection scale;
- intended and observed deltas;
- unexpected changes;
- at least four named inspection checks; and
- accepted/rejected disposition.

An accepted record requires every check to be affirmative and `unexpected_changes` to be empty.
A rejected record closes normal actuation and permits only a declared repair transaction.

### Runtime-state ownership

The state was initially installed as `BLOCKED_RECONCILIATION` because the uncommitted visual log
recorded partial-scale evidence, a process violation and subsequent live mutations. That value is
not permanent authority. The machine-owned state file and ledger are the only source for the
current transaction phase; static status documents record only that this gate is mandatory.

## Test strategy

The historical generators and mutation log are the observed failing baseline. Deterministic tests
must additionally prove:

- missing state cannot silently authorise a write;
- missing snapshot blocks begin;
- a second begin is refused;
- simultaneous begins from independent processes are serialised;
- unchanged source after a claimed mutation is refused;
- missing/empty/non-PNG screenshots are refused;
- wrong project/document/transaction identity is refused;
- weak inspection records are refused;
- rejection blocks normal work;
- repair is the only write allowed after rejection;
- an accepted repair returns the lock to `READY`;
- the executor has no `all` mutation mode; and
- every mutating executor stage calls the guard.
- state, evidence digests and the terminal ledger event remain mutually consistent.

## Scope boundary

This work does not mutate EasyEDA, repair the current live sheet, approve the current fixture plan,
or complete qualification. It installs the control system that must govern the next live action.
