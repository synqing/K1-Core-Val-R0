# G2.2 readable reconstruction — fixture, not JLC-SCH-READY

Date: 2026-08-28

```text
JLC_SCH_READY     = OPEN
JLC_LAYOUT_READY  = BLOCKED_BY_JLC_SCH_READY
JLCPCB_LAYOUT     = BLOCKED_BY_SCHEMATIC_PRESENTATION
official_freeze   = False
live_project      = 64325d0e55e0435abd018defb0089a9b (untouched)
```

## What happened

The current G2.1 review sheet failed the presentation checker: 664 short stubs
against 110 routed wires, power rails drawn as labels only, and eight equal
prison boxes.

A signal-weighted soft-region floorplan was built (GND excluded; power and
high-fanout downweighted; buses collapsed; declared reading flow preserved).
A V3 renderer then rewrote presentation only, inside a copy of the
EasyEDA-normalised generation.

Machine compare against the unpublished digest:

```text
ELECTRICAL_EQUIVALENCE = PASS
designators = 252
nets        = 159
nc          = 95
bound_pins  = 105
```

The reconstructed source itself passes the presentation checker (0 stubs, 159
routed wires, unequal soft regions, option notes present). That is an offline
fixture result. It is **not** EasyEDA-stable proof.

The reconstructed page was packed into
`K1-Core-Val-R0-G2.2-READABLE-CANDIDATE.epro` by replacing only
`SHEET/cffcdb562c1b48d1a5214cfc263b6c90/1.esch` in a copy of the
`3db861a3` archive. The PCB member stayed empty. Archive SHA256 prefix
`3db861a3` is a **file hash**, not a project UUID.

`--allow-unfrozen` was required. The renderer still refuses a promotion
candidate without an official freeze.

## What was not done

- No write to live project UUID `64325d0e55e0435abd018defb0089a9b`.
- No `set_document_source`.
- No disposable EasyEDA import of the reconstructed `.epro`.
- No save/reopen, live ERC, or live BOM on a new project UUID.
- `JLC-SCH-READY` was **not** stamped.
- `JLC-LAYOUT-READY` was **not** stamped.

## Remaining ship path

1. Captain: open a new EasyEDA window on review `dcd7e3ca…`; export GUI ERC items.
2. Agent: classify the 9 fatals and 19 warnings; repair any real defect once.
3. Captain: freeze `g2.1-electrical-digest.json` as electrical authority.
4. Captain: accept `FLOORPLAN.html`.
5. Agent: re-emit without `--allow-unfrozen`; import into a **new** disposable
   EasyEDA project (new project UUID).
6. Agent: save/reopen, semantic read-back, settled screenshots, ERC, BOM.
7. Captain: `JLC-SCH-READY` stamp — RFQ/package and schematic handoff only.
8. Agent + Captain, separately: IOMUX, footprints, DXF/mechanics, pad count,
   JLC source package.
9. Captain: `JLC-LAYOUT-READY` stamp.
10. Agent: give JLCPCB the source.

The stamp that means schematic reconstruction shipped is `JLC-SCH-READY` PASS
on a reconstructed project whose digest matches the frozen oracle. Neither
stamp is fabrication readiness.
