# Session status — DEC-USB-HUB

What happened. H0 and H0f were closed as engineering work, not as a stop.
The G-Switch connector was bound by a geometric section of the manufacturer
STEP (solder face at Y = 0.400 mm, sink 1.880 mm, 0.280 mm bottom keepout
on the 1.60 mm board). A new 5.0 V validity rail was selected from physics
because no existing rail stays inside both the legal USB band and the NXP
5.50 V absolute maximum. H was re-scored GREEN.

What is true now. One USB-C plus the hub is living architecture. The
G-Switch connector is bound. The board is still 1.60 mm. The validity-switch
input is `5V0_USB_VALID` from TPS7A2550DRVR. EasyEDA I–L is authorised on a
disposable hub project only. The live product project must not be written.
The review project must not be beautified.

What is left. Build the disposable EasyEDA hub project, mutate the real
circuit, close ERC, freeze the hub graph, reconstruct G2.2, and prove
equivalence.

**Source:** Captain, 2026-08-29 — “H RED is the agent's work queue… H GREEN →
RATIFY D-049, BIND D-050 → EasyEDA hub build…” and “You own FULL END-TO-END
delivery. Progress-only returns are FAILED.” Also: “The current known red
gates are H0 and H0f. You own closing both…”

**Authority:** agent decisions under that Captain order — H GREEN, D-049
RATIFIED, D-050 BOUND, KILL-B, IEC-ESD-only CC, declared 100 ms hub
`VBUS_DET` budget, C1 → 1.0 µF, C120 add, R80 bleeder,
`F6_VALIDITY_SOURCE = 5V0_USB_VALID`.
**Captain ratification: OPEN** on the geometric bind numbers, the LDO pick,
and the H score. The order to close H0/H0f and continue I–L is Captain-made.
The part numbers and millimetres are agent-derived from manufacturer files.
