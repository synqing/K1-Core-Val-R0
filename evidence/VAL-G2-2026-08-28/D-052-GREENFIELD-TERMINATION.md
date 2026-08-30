# D-052 — G2.2/HOLD/canonical repair terminated

```text
DATE   = 2026-08-30
DECISION = D-052
ACT    = programme archive freeze; not a D-040 ownership incident
```

Captain inspected `ProPrj_K1-Core-Val-R0-G2.2-READABLE-HOLD.epro2`. The only
`SCH_PAGE` had 237 component records, 234 with designators, and no
`U20-USB`…`U25-USB`, `Y3-USB`, or `J1-PWR1`. Recovery had treated 287
designators + U20 present as known-good HOLD. That is a control-system
failure: there was no trustworthy answer to “what is the current schematic?”

## What stopped

- USB T1–T6 on HOLD
- HOLD snapshot restore / promotion
- Canonical versus candidate versus current-tab as write identity
- `JLC-SCH-READY` on G2.2

## What remains knowledge

Ratified D-001–D-051, manufacturer research, USB2422 single-Type-C
architecture, D-051 audio, NFC conclusions, power calculations, session
canon keepouts, contracts. Spec:
`architecture/GREENFIELD-BUILD-SPEC.md`.

## Mutation lanes frozen this act

Each live lane was `freeze-incident` then marked `LANE-RETIRED`.

| Directory | Project | Prior gate state |
| --- | --- | --- |
| `evidence/VAL-G2-2026-08-28/g22-hold-lane/` | `55ed9ee9…` | IN_FLIGHT T2 |
| `evidence/VAL-G2-2026-08-28/canonical-core-val-r0/` | `64325d0e…` | READY |
| `evidence/VAL-G2-2026-08-28/canonical-core-val-r0/schematic-lane/` | `64325d0e…` | AWAITING_EVIDENCE |
| `evidence/VAL-G2-2026-08-28/dec-usb-hub/hub-lane/` | `41c8e652…` | READY |

Qualification lane `09e9c541…` was already `LANE-RETIRED` (D-042).

## GREENFIELD EasyEDA UUID

`NOT_ALLOCATED`. The blank project is the first EasyEDA act after OPEN
BEFORE BUILD closes (or a dedicated title-frame-only create that does not
draw electronics). It must not be cloned from this `.epro2`.

## What a later agent must not do

- Run T1.
- `set_document_source` on archived projects.
- Treat any source hash as the identity of the design.
- Ask Captain to GO a terminated repair queue.
