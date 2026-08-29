# Phase C — provisional proceed (not ratification)

What happened. Captain’s implement-the-plan order was recorded as the Phase C
proceed-to-physics stamp. Living documents were flipped from `DRAFT` to
`APPROVED_FOR_PHYSICS / PROVISIONAL`. D-050 stayed open. Nobody wrote EasyEDA.
Nobody wrote `RATIFIED`.

What is true now. Physics may proceed. Official electrical freeze, D-049
`RATIFIED`, and D-050 bind remain blocked until H is actually GREEN.

What is left. Vendor extracts, connector physics, VBUS envelope, pin contract,
then a written H GO/NO-GO.

```text
DATE = 2026-08-29
STAMP_SOURCE = Captain implement-the-plan (Build + execute authorised plan)
D049_STATUS = APPROVED_FOR_PHYSICS / PROVISIONAL
D050_STATUS = OPEN / CONNECTOR-PHYSICS BLOCK
D049_RATIFIED = no
D050_BOUND = no
OFFICIAL_FREEZE = no
EASYEDA_WRITE = no
J1_SELECTED = GT-USB-7005A / C5250872
J1_BOUND = no
```

## C1 — presented

- D-049 architecture text in `authority/01-DECISION-REGISTER.md`
- `architecture/ADR-049-usb2422-embedded-hub.md`
- D-050 OPEN row on G-Switch `GT-USB-7005A` / `C5250872`
- `architecture/ADR-050-j1-usbc-receptacle.md`
- `evidence/VAL-G2-2026-08-28/dec-usb-hub/AUTHORITY-SWEEP.md`

Two stamps requested by the plan:

1. Proceed with hub physics — **yes** (implement-the-plan).
2. D-050 registered OPEN on the named G-Switch part — **yes**. Not a bind.

## C2 — reject path

Not taken. Hub programme is not `REJECTED`.

## C3 — proceed path

| Artefact | After C |
| --- | --- |
| D-049 register | `APPROVED_FOR_PHYSICS / PROVISIONAL` |
| `contracts/usb-interface.md` | `status: PROVISIONAL` |
| `STATUS.md` lane | `ADOPTED_PENDING_PHYSICS_AND_D050` |
| D-050 | still `OPEN / CONNECTOR-PHYSICS BLOCK` |
| RATIFIED | **not written** |

## C4 — harness

Re-run recorded in `PHASE-C-HARNESS.txt` after this stamp.

```text
EXIT_C = D-049 APPROVED_FOR_PHYSICS / PROVISIONAL
D050_OPEN_WITH_SELECTED_MPN = yes
PHYSICS_MAY_PROCEED = yes
EASYEDA_MUTATE_BLOCKED_UNTIL_H_GREEN = yes
```
