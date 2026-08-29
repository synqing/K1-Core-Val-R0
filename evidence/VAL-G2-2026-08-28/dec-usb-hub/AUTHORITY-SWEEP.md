# Authority sweep — two-USB-C / J7 living text

What happened. Phase B grepped `harness/`, `schematic/`, `architecture/` and
`contracts/` for `J7-ESP`, `receptacle_count: 2`, `two USB-C` and close cousins,
then dispositioned every hit. Named historical evidence under
`evidence/VAL-G2-2026-08-28/canonical-core-val-r0/` was left unedited.

What is true now. Every living document in the B9.4 list either matches D-049
`DRAFT` or is recorded here as wait-for-stamp. Zero hits lack a disposition.

What is left. Captain Phase C. Do not treat this sweep as ratification.

```text
SWEEP_DATE = 2026-08-29
UN_DISPOSITIONED_HITS = 0
D049_STATUS = DRAFT
D050_STATUS = OPEN / CONNECTOR-PHYSICS BLOCK
STACKUP_STATUS_MD = UNEDITED
D012 = UNEDITED
```

## B9.4 living docs

| Path | Hits | Disposition |
| --- | --- | --- |
| `contracts/usb-interface.md` | `receptacle_count: 2`, `J7-ESP` section | **Rewrite now** — done. Front matter `status: DRAFT`, one receptacle + USB2422. J7 section replaced with “J7 does not exist”. |
| `authority/01-DECISION-REGISTER.md` | D-044 two-USB-C text | **Rewrite now (status only)** — D-044 text kept as history; status `AMENDED_BY_D-049`. D-049 `DRAFT` and D-050 `OPEN / CONNECTOR-PHYSICS BLOCK` added. D-012 row unedited. |
| `authority/05-SUPERSESSIONS.md` | D-044 two-USB-C row; short-edge row mentioning two Type-C | **Rewrite now (add rows)** — new 2026-08-29 rows for D-049 and for “D-050 does not supersede D-012”. Earlier D-044 tombstone of “single USB owned by S3” **kept**. Short-edge historical reason text **left unedited**. |
| `architecture/POWER-ARCHITECTURE.md` | D-044 / `J7-ESP` sentence | **Rewrite now** — done. TPS62913 D-045 table unedited. |
| `architecture/G3-FLOORPLAN-DOCTRINE.md` | §2 two Type-C from D-044; `J7-ESP` near-S3 | **Rewrite now** — done. `BINDING = NO` kept. One Type-C + hub-island hypothesis. |
| `architecture/VALIDATION-ARCHITECTURE.md` | none | **No rewrite** — does not name two USB-C. |
| `architecture/G2.2-READABLE-SCHEMATIC.md` | USB flow “connector → MCU”; service USB | **Rewrite now** — living USB sentences point at D-049 one Type-C + hub. Reconstruction against the hub digest waits for Phase L. |
| `STATUS.md` | D-044 two-receptacle paragraph | **Rewrite now** — done. Lane `DEC-USB-HUB = IN_PROGRESS_DRAFT`. `G2_1_OFFICIAL_FREEZE = BLOCKED_BY_DEC_USB_HUB_AND_D050`. `JLC_SCH_READY = OPEN`. |
| `contracts/debug-fabric.md` | native USB implying a dedicated receptacle | **Rewrite now** — done. `J6-ESP` mandatory; DN2 only when hub and host are up. |
| `docs/agent/JLC-LAYOUT-READY.md` | no two-receptacle assumption | **Light rewrite now** — one-Type-C / D-050 forward pointer added so two receptacles cannot remain implied living truth. Not a stamp. |

Also rewritten now (living machine-readable authority, leftover two-port keys):

| Path | Hits | Disposition |
| --- | --- | --- |
| `project.yaml` `usb:` block | `authority: D-044`, `receptacle_count: 2`, `J7-ESP` | **Rewrite now** — aligned to D-049 `DRAFT` / D-050 selected-not-bound. |

## `architecture/` other hits

| Path | Hits | Disposition |
| --- | --- | --- |
| `architecture/ADR-049-usb2422-embedded-hub.md` | names D-044 / `J7-ESP` as history | **Rewrite now** — new file. Historical mention only. |
| `architecture/ADR-050-j1-usbc-receptacle.md` | none of the two-port living claims | **New file** — OPEN, selected-not-bound. |

## `contracts/` other hits

None remaining as current two-port truth. `usb-interface.md` residual `J7-ESP` strings are “does not exist”.

## `harness/`

| Path | Hits | Disposition |
| --- | --- | --- |
| `harness/check_authority_consistency.py` | none of the two-port strings | **Rewrite now** — added D-049 assertions. Passes on `DRAFT` / `PROVISIONAL`. Does **not** require `RATIFIED`. |
| `harness/schematic_domains.py` | no `J7-ESP` / two-USB-C string | **Rewrite after stamp** — Phase L, once a hub digest exists. |
| `harness/epro_schematic_renderer.py` | no D01/D05 two-port captions found by this sweep | **Rewrite after stamp** — Phase L. |
| `harness/schematic_floorplan.py` | no two-port string | **Rewrite after stamp** — Phase L. |

## `schematic/` — still describe the G2.1 dual-USB graph

| Path | Hits | Disposition |
| --- | --- | --- |
| `schematic/repair_esp_service.py` | `J7-ESP` pin map and wiring | **Rewrite after stamp** — repair script for the graph that still exists. |
| `schematic/repair_nc_flags.py` | `J7-ESP` A8/B8 NC | **Rewrite after stamp**. |
| `schematic/dump_floating_pins.py` | `J7-ESP` A8/B8 | **Rewrite after stamp**. |

Do not pretend those scripts already implement the hub. They must keep matching the
current dual-USB G2.1 source until H GREEN and Phase J delete J7.

## Historical evidence — leave unedited (B9.3)

These record what the sheet was. They are not living authority.

| Path | Disposition |
| --- | --- |
| `evidence/VAL-G2-2026-08-28/canonical-core-val-r0/USB-TOPOLOGY-AUDIT.md` | Historical — leave unedited |
| `evidence/VAL-G2-2026-08-28/canonical-core-val-r0/PIN-AUDIT-S3.md` | Historical — leave unedited |
| `evidence/VAL-G2-2026-08-28/canonical-core-val-r0/PIN-AUDIT-PWR1.md` | Historical — leave unedited |
| `evidence/VAL-G2-2026-08-28/canonical-core-val-r0/DRC-WAIVERS.json` (J7 SBU) | Historical — leave unedited; T24 may copy-then-edit on a hub candidate later |
| `evidence/VAL-G2-2026-08-28/canonical-core-val-r0/TAKEOVER-RECEIPT.md` | Historical — leave unedited |
| `evidence/VAL-G2-2026-08-28/canonical-core-val-r0/BOM-SEMANTIC-AUDIT.md` | Historical — leave unedited |
| `evidence/VAL-G2-2026-08-28/canonical-core-val-r0/ORACLE-BUILD-RECEIPT.md` | Historical — leave unedited |
| Other `canonical-core-val-r0/jobs/*` and pin harvest JSON naming `J7-ESP` | Historical — leave unedited |
| `evidence/VAL-G2-2026-08-28/schematic-presentation/*` dual-USB G2.2 fixture | Historical fixture of the current graph — leave unedited; Phase L replaces it |

## Explicitly not rewritten

| Path | Why |
| --- | --- |
| `pcb/STACKUP-STATUS.md` | B9.6 — D-050 names the collision; thickness stays 1.60 mm |
| D-012 register row | Unchanged. `RATIFIED` 1.60 mm / six layers |
| Working plan file | Do not edit |
| Live EasyEDA `64325d0e…` | Untouched |
| `dcd7e3ca…` | Not beautified |

## B9.5 harness results (2026-08-29)

`python3 harness/check_authority_consistency.py`

```text
AUTHORITY_FILES_PARSED=7
OWNERSHIP_ROWS_PARSED=21
REQUIRED_FUNCTIONS_PRESENT=21/21
CONTRACTS_PARSED=9
DOCUMENTS_SCANNED=33
SSCM1_RECOVERY_RECORDS_PARSED=3/3
VAL_G2_0_STATE_RECORDS_PARSED=3/3
CONTRADICTIONS=0
AUTHORITY_CONSISTENCY=PASS
```

Passed on USB contract `status: DRAFT`. The checker does not require `RATIFIED`.

`python3 harness/check_terminology.py`

```text
TERMINOLOGY_FILES_SCANNED=36
TERMINOLOGY_LINES_SCANNED=3029
QUOTED_EXEMPTIONS_HONOURED=4
VIOLATIONS=0
TERMINOLOGY=PASS
```

No leftover living-doc failure of the “two USB-C still current” class.

## Exit B (sweep)

```text
LIVING_B94_MATCHES_D049_OR_WAIT_FOR_STAMP = yes
UN_DISPOSITIONED_HITS = 0
EASYEDA_WRITES = 0
AUTHORITY_CONSISTENCY=PASS
TERMINOLOGY=PASS
PHASE_C_STAMP = given_2026-08-29_implement_the_plan
D049_AFTER_C = APPROVED_FOR_PHYSICS / PROVISIONAL
D050_AFTER_C = OPEN / CONNECTOR-PHYSICS BLOCK
AUTHORITY_CONSISTENCY_AFTER_C = PASS
```

Phase C follow-up: Captain implement-the-plan recorded as proceed-to-physics.
This sweep remains the Phase B receipt. See `PHASE-C-STAMP.md`.

