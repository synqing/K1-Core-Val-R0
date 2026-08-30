# ADR-052: Terminate G2.2/HOLD schematic repair; greenfield is the only implementation

**Status:** Accepted  
**Date:** 2026-08-30  
**Deciders:** Captain

## Context

The G2.2 / HOLD / canonical schematic-repair programme no longer has a single
answer to “what is the current schematic?”. Saved `.epro2`, live editor,
semantic dumps, recovery hashes and designator censuses disagree. Continuing
T1–T6 would spend more work inside an untrusted state machine.

## Decision

Keep the engineering knowledge. Discard every existing EasyEDA schematic,
placement, net geometry and PCB copper as **implementation authority**.

Existing K1-CORE-VAL-R0 EasyEDA projects are **ARCHIVE / EVIDENCE / DO NOT
MUTATE / DO NOT FABRICATE**. They may answer “what value did we previously
use?” They must not answer “how should the new schematic be wired?”

The next implementation is a new EasyEDA Pro project
`K1-Core-VAL-R0-GREENFIELD` with a **new UUID and no ancestry**: not a clone,
not Save As, not imported from any `.epro2`, not JSON-edited from an old
page. Component #1 waits on `architecture/GREENFIELD-BUILD-SPEC.md`.

Hashes fingerprint a known semantic state. They are not the identity of the
design.

PCB, when the greenfield schematic is frozen, is a **blank board**. No
imported K1 copper. Mechanical constraints that remain ratified still apply.

## Options considered

### Option A: Keep repairing HOLD / G2.2
**Rejected.** The control system failed. The attached HOLD `.epro2` did not
match the 287-designator recovered-state story.

### Option B: Promote one snapshot as canonical
**Rejected.** Snapshot worship is the failure mode.

### Option C: Greenfield (chosen)
Complexity of *implementation* drops. Architecture work continues off-canvas.

## Consequences

- G2.2, HOLD, G2.1 oracle and product-canonical EasyEDA writes stop.
- `JLC-SCH-READY` no longer attaches to G2.2. It attaches to GREENFIELD after
  the spec is drawn and verified.
- USB wiring *lessons* (session canon, checkers) remain knowledge for the
  greenfield USB block. They are not a licence to mutate HOLD.

## Action items

1. Freeze every existing mutation lane (`FROZEN_INCIDENT` programme archive +
   `LANE-RETIRED`). **Done 2026-08-30.** Receipt:
   `evidence/VAL-G2-2026-08-28/D-052-GREENFIELD-TERMINATION.md`.
2. Author the greenfield build spec; close OPEN items before component #1.
   Spec written; OPEN items remain OPEN.
3. Implementation home is `/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R1`
   (D-053). EasyEDA name `K1-Core-VAL-R1`, blank project, title frame only,
   after identity can be proven on a **new** UUID. UUID `NOT_ALLOCATED`
   until that create. Do not clone HOLD. Do not draw in the R0 repo.
