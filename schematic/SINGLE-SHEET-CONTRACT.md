# Single-sheet contract

K1-CORE-VAL-R0 contains one and only one electrical schematic sheet.

All electrical components reside on that sheet.

All active, DNP, option, validation and TUNE/TBD circuitry resides on that sheet.

All electrical nets are represented on that sheet.

All subsystem boundaries are visible on that sheet.

Hierarchical sheets and separate subsystem pages are forbidden.

Cross-domain connectivity must be understandable without opening another document.

Direct wiring is preferred. Net labels may aid readability but may not conceal architectural
relationships or power flow.

The sheet is organised into visually bounded domains corresponding to the project's domains of
concern. Readability is achieved spatially, not hierarchically.

No PCB component may exist without schematic authority, except items that are purely mechanical
and explicitly listed as such.

## Why

This board exists to reason about domain interactions. Sheet ports and hierarchy conceal exactly
the relationships the board was built to expose.

## Wiring doctrine

A page of hundreds of floating components joined only by global names is not a schematic.

Within a domain, use visible wires. Between adjacent domains, use visible wires wherever they
remain readable. Long global rails and major shared buses may use labelled trunks.

    POWER ENTRY -----5V_PROTECTED-----> SHUNT -----5V_SYS-----> loads

not six disconnected `5V_SYS` labels with no visible power tree.

    RT1062 --BCLK---+
           --FSYNC--+---> AUDIO INTERFACE
           <-SDOUT--+

not isolated pin labels with the connection hidden.

## Component states

Every component appears as one of: `FIT`, `DNP`, `OPTION`, `TUNE_TBD`, `VALIDATION_ONLY`.

Every XOR population is drawn beside its circuit with the rule written next to it:

    PDM_DATA ---+--- R_A 0R FIT ---> ADC6120 PDM
                |
                +--- R_B 0R DNP ---> RT1062 DIRECT
    RULE: R_A XOR R_B

## Qualification

This doctrine is subject to the EasyEDA capability test in
`schematic/single-sheet-qualification/TEST-PLAN.md`. Failing that test does not authorise
hierarchical sheets. It triggers a stop, a report of the measured failure, and optimisation of
the one-sheet implementation.
