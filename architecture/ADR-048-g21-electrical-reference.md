# ADR-048: G2.1 is the electrical reference, not the drawing authority

**Status:** Accepted
**Date:** 2026-08-28
**Deciders:** Captain
**Register:** D-048

## Context

The repaired archive (`3db861a3…`) survived a real EasyEDA import, save and reopen in
disposable project `dcd7e3cab2a24b9aa6e531d2b62e1b6f`. The sheet did not collapse, split,
lose the repaired topology, or mutate BOM state. That is the prerequisite for any
wholesale schematic reconstruction.

The same sheet is not a professional drawing. Ten domain boxes still organise the page as
sealed islands. Power flow is often a pair of distant labels. The RT1062 reads as one
monolithic pin directory. Promoting that geometry would canonise a presentation failure
and force an immediate rewrite of whatever we had just called finished.

The import receipt is also incomplete on its own terms: Phase 9 ERC item text is missing,
and Phase 16 critical zooms are missing. Those gaps are procedural. They do not authorise
promotion, and they do not have to stop layout-engine work.

## Decision

`dcd7e3ca…` (`K1-Core-Val-R0-G2.1-BULK-CANDIDATE`) is the **G2.1 electrical reference /
EasyEDA normalisation oracle**. It proves what EasyEDA thinks the repaired project is.

It is not:

- the product canonical project;
- the JLCPCB handoff schematic;
- final schematic-geometry authority;
- a PCB layout source.

The live project `64325d0e55e0435abd018defb0089a9b` stays untouched.

Readable reconstruction is a new derivative, **`K1-Core-Val-R0-G2.2-READABLE-CANDIDATE`**.
Its only job is to rebuild the drawing while proving **zero intentional electrical change**
from the G2.1 graph.

`JLC-SCH-READY` attaches to G2.2:

> electrically equivalent + professionally readable + EasyEDA-stable.

This decision is not “VAL-G2.1 complete” and does not accept the import receipt.

## Options Considered

### Option A: Promote `dcd7e3ca…` now

| Dimension | Assessment |
|-----------|------------|
| Complexity | Low today, high tomorrow |
| Cost | Immediate false close, then a forced rewrite |
| Scalability | Locks the ugly geometry into every later gate |
| Team familiarity | Attractive because the import just worked |

**Pros:** One project identity; import proof already exists.
**Cons:** Canonises the presentation failure; JLCPCB engineers still cannot read the sheet;
G2.2 becomes an apology rather than a programme.

### Option B: Beautify `dcd7e3ca…` interactively in EasyEDA

| Dimension | Assessment |
|-----------|------------|
| Complexity | High |
| Cost | Another MCP clicking campaign |
| Scalability | Manual wire edits do not survive the next electrical correction |
| Team familiarity | Repeats the failure mode that produced the mess |

**Pros:** No second project.
**Cons:** Forbidden electrical drift is easy to introduce and hard to prove absent; the
editor is currently hung; the ten-box grammar stays in charge.

### Option C: Keep `dcd7e3ca…` as electrical reference; reconstruct G2.2 offline (selected)

| Dimension | Assessment |
|-----------|------------|
| Complexity | Medium — graph extract plus geometry-only transformer |
| Cost | Up-front invariant work; cheaper than a second electrical regression |
| Scalability | One electrical fix in G2.1 is inherited by every later relayout |
| Team familiarity | Reuses the V3 parser and pin-binding work already paid for |

**Pros:** Exact electrical-graph invariant; no interactive beautify; JLCPCB gate attaches
to a readable sheet.
**Cons:** Official G2.1 freeze still waits for a healthy EasyEDA export; ERC item text is
still OPEN.

## Trade-off Analysis

The valuable property of `dcd7e3ca…` is **host-normalised electrical semantics**, not
its geometry. Option A spends that property on the wrong artefact. Option B spends it
inside an editor that cannot currently be driven and that has already shown it will
accept ugly, disconnected labels as a finished page. Option C keeps the electrical
graph and throws the drawing away on purpose.

The ERC 9/19 result is distinguished, not ignored:

- G2.1 graph = current reference graph (we have this);
- G2.1 graph = proven manufacturing-clean graph (we do not).

Layout-engine work may proceed against the first. `JLC-SCH-READY` still requires the
second.

## Consequences

- Promoting `dcd7e3ca…` is a failed act even if every later checker is green.
- Interactive beautification of `dcd7e3ca…` is a failed act.
- G2.2 may change only geometry, labels, notes, groups, sheet size and title-block
  annotation.
- One pin changing electrical membership fails G2.2.
- When EasyEDA recovers: classify ERC items, optionally close Phase 16 zooms, export
  the saved review project, hash that export as the official G2.1 reference source.
- Tonight’s post-reopen source dump may seed graph extraction. It is not the official
  freeze.

## Action Items

1. [x] Record D-048 and the receipt classification.
2. [x] Write the G2.2 programme contract.
3. [x] Extract a pre-export electrical-graph seed from the post-reopen source.
4. [ ] When EasyEDA is healthy: ERC item text, optional zooms, export, official freeze.
5. [ ] Implement geometry-only relayout against the frozen graph.
6. [ ] Import G2.2 as a new disposable project and prove equivalence before any
   promotion question.
