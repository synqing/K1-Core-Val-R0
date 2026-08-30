# ADR-053: Greenfield implementation home is K1-CORE-VAL-R1

**Status:** Accepted  
**Date:** 2026-08-30  
**Deciders:** Captain  
**Register:** D-053

## Context

D-052 discarded R0 EasyEDA as implementation authority.

**Source:** Captain, 2026-08-30 — “The new green field project folder is
`/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R1`”

## Decision

The only implementation home is:

`/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R1`

That path is Captain-named. It is not a git worktree of R0, not a clone,
and not an import of HOLD/canonical/G2.2.

Hardware intent remains the K1-CORE validation platform (VAL-R0
architecture). The folder is R1 so the fractured R0 implementation is
not the working tree.

EasyEDA project name: **`K1-Core-VAL-R1`**. New UUID. No ancestry.

K1-CORE-VAL-R0 remains **knowledge and archive**.

## Consequences

- Agents drawing the board work in R1.
- R0 mutation lanes stay `LANE-RETIRED`.
- Component #1 still waits on OPEN BEFORE BUILD.
