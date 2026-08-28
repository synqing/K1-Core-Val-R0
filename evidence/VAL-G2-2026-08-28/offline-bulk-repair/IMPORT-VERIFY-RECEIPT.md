# IMPORT-VERIFY-RECEIPT

State: **IMPORTED_NOT_CANONICAL**

Captain classification, 2026-08-28 (D-048):

```text
IMPORT SEMANTICS:          PASS
ELECTRICAL SPOT CHECKS:    PASS so far
BOM/PCB-STATE CHECKS:      PASS so far
ERC EVIDENCE:              OPEN
VISUAL EVIDENCE:           OPEN
OVERALL RECEIPT:           NOT YET ACCEPTED
STATE:                     IMPORTED_NOT_CANONICAL
ROLE:                      G2.1 ELECTRICAL REFERENCE / EASYEDA NORMALISATION ORACLE
```

The receipt is not rubber-stamped ACCEPTED. Phase 9 requires every ERC item classified;
nine fatals and nineteen warnings with no item text cannot close. Phase 16 treats
unreadable or missing screenshots as missing evidence; the critical zooms were not
captured. Those gaps are procedural. They do not prove the repaired circuit is wrong,
and they do not block starting G2.2 reconstruction.

`dcd7e3ca…` is not product canonical, not JLCPCB handoff, not drawing-geometry
authority, and not a PCB source. Do not promote it because the import survived.

Date: 2026-08-28

The repaired archive was imported once as a new EasyEDA project. It is a disposable review
copy. The live product project was not overwritten. This is not promotion and does not close
VAL-G2.1.

## What happened

The Stage A candidate was imported through EasyEDA’s professional import path as a **New
Project**. The new project opened with one electrical sheet and an empty PCB. It was saved,
closed, and reopened. The sheet did not go blank. Live pin checks show the trunk eFuse still
in place, the shared LED eFuse gone, and the per-branch LED switch present. USB current
limiting is still the trunk device’s job.

EasyEDA later showed a “not responding” sheet over that same review window. The debug port
used for zoomed screenshots died. Readable box-level zooms were therefore not captured. The
electrical claims below rest on the saved source and live pin bindings, not on unreadably
distant pixels.

## What is true now

- Review project name: `K1-Core-Val-R0-G2.1-BULK-CANDIDATE`
- Review project UUID: `dcd7e3cab2a24b9aa6e531d2b62e1b6f` (not live, not the dead qualification project)
- Schematic page UUID: `1435cb46f39e48c8a8aadbb84ca81603` (inherited from the archive)
- PCB UUID: `59bef7e87cff4cd580561703b62d8c19` (inherited; electrically empty)
- Team: `27700277ef7a49e48a0293bece6b2993`
- Discriminator: `parentProjectUuid` / tab suffix `@dcd7e3ca…`. The page UUID alone is not enough.
- Live canonical remains `64325d0e55e0435abd018defb0089a9b`
- Import candidate SHA256: `3db861a351239a8628b151c4610a845da761ed9bcb562755f9ea9374aa262ba7`
- `1dd7d815…` was not imported

**U1-PWR1 remains the inlet/trunk protection device. U17-PWR2 replaces U4-PWR2’s shared LED
protection with independent branch protection. USB current limiting is U1’s job throughout.**

## Phase 6 — identity

- One type-1 schematic page named P1. One board. No `Schematic*_N` sibling.
- PCB document exists and is empty: 0 components, 0 vias, 0 lines, 0 texts, 0 nets.
- Ten domain rectangles present. Box 1 title on the imported sheet is
  `1. POWER ENTRY + PROTECTION` (plan text still says `CURRENT SENSE`). The other nine titles
  match the layout file.
- Not a dummy lattice. Not blank.

## Phase 7 — save, close, reopen

- Saved review schematic only (`saved: true`, parent `dcd7e3ca…`).
- Closed by navigating off the project, then reopened the same review UUID.
- After reopen: same project / page / PCB UUIDs. Still one type-1 sheet.
- Source hash before save: `2352228:ab0dedd2`
- Source hash after reopen: `2352834:a75b5884`
- Counts after reopen: 255 components, 252 designators, 774 wires (archive wires were 773).
  That is host re-serialisation, not a ten-plus topology swing.
- Whole-sheet after reopen: `review-after-reopen-whole.png`

The start-page hop briefly showed the live project URL. No live write was issued. The editor
was pointed back at `dcd7e3ca…` before any further read.

## Phase 8 — live semantic

Pin coordinates from the review sheet bound to named wire stubs (tolerance 8):

| Check | Result |
| --- | --- |
| U1 present; U4 absent; U17 present | PASS |
| U1.3 and R67 on `PWR_ENTRY_PG_RT_IOMUX_TBD` | PASS |
| C11 on `5V_SYS` | PASS |
| U16-VAL.5 SENSE on `3V3` | PASS |
| U3.5 PG on `BUCK_PG`, not NC | PASS |
| U2 A0/A1 strapped, not NC | PASS |
| C10 both pins wired, not NC | PASS |
| U12 RFO2/RFI2 NC; I2C_EN not NC | PASS |
| U12 VDD and VDD_TX on `NFC_5V`; VDD_IO on `3V3` | PASS |
| U13 CS=`3V3`, SA0=`GND`, INT2 NC | PASS |
| U1 OUT=`5V_PROTECTED`; IN=`5V_USB` | PASS |
| U17 IN=`5V_SYS`; OUT1/2 = `5V_LED_L_SW` / `5V_LED_R_SW` | PASS |
| R31-AUD, R32-AUD, R33-AUD all present | PASS |
| RILIM-LED on `TPS2561_ILIM` / `GND` | PASS |
| Stale primitives `e153914`, `e146347` | absent |

Manufacture `getNetlistFile` / BOM file export returned no file. Net membership above is from
live pin geometry plus named stubs, plus schematic ATTR for BOM.

## Phase 9 — ERC

`sch_Drc.check(strict, no UI, verbose)` returned type-counts only: **9 fatal**, **19 warn**.
Rules were not edited. Individual messages were not returned by the bridge. **This does not
close Phase 9.** An unmapped transformer/import-semantic error would stop the run; without
item text those 28 residuals cannot be classified. The counts are parked evidence, not a
pass. The GUI panel remains the certifying gate and was not exported because the editor
hung before a panel shot.

When EasyEDA is healthy again: extract every ERC item, classify each one, and only then
revisit this section. If any item is a real electrical defect, fix it once in the G2.1
source graph so G2.2 inherits the correction. Do not Force Quit the hung window to obtain
the panel tonight.

Parked: `erc/bridge-erc.json`.

## Phase 10 — BOM (schematic ATTR)

RQ-048 seven refs: blank MPN, blank supplier, blank `supplierId`, BOM=no, PCB=no.

U6-RTC: two units, **one** Add-into-BOM=yes line.

R8-PWR2 absent.

`DVBUS-PWR1` and `U17-PWR2`: Convert to PCB = no.

`RILIM-LED`: 59 kΩ, BOM=no, PCB=yes, supplier blank.

Eight test points: BOM=no, PCB=yes, no Keystone 5001 identity.

Parked: `bom/review-bom-from-source.json`.

## Phase 11 — CPL

Empty. Pass. No place and no convert-to-PCB.

## Phases 12–13 — census

Required present designators: all found. Required absent (`F1`, `L3-NFC`, `R43-NFC`,
`R50-MOT`, `U4-PWR2`, `C68-PWR2`, `R8-PWR2`): all absent.

Required nets present, including `PWR_ENTRY_PG_RT_IOMUX_TBD`. Retired orphans
`5V_LED_COMMON`, `LED_EFUSE_DVDT`, `LED_EFUSE_ILIM`, `USB_EFUSE_PG` are absent as exact NET
names (`USB_EFUSE_PGTH` remains on U1 pin 4 and is not the orphan).

## Phases 14–15 — DEC / RQ (live)

Holds stay holds. No RQ-056.

- DEC-05 target is **U16-VAL.5**, on `3V3`.
- DEC-13 / RQ-035: R31 and R32 and R33 all fitted.
- RQ-025: U1.3 and R67 share one observability net.
- RQ-047: `SUPERSEDED_BY_U4_REMOVAL` (R8 gone).
- RQ-044: U17 drawn, U4 gone, footprint held.
- RQ-048 / RQ-050 / RQ-052 as above.
- DEC-04: RFO2/RFI2 remain NC. Do not un-NC them.

Full machine record: `LIVE-VERIFY.json`.

## Phase 16 — visual

| File | SHA256 | Claim | Obvious? |
| --- | --- | --- | --- |
| `review-identity-before-save.png` | `35ed8f5ab3a7a100adf33cf715de6ccccac9cfaeb1782ab2547bff16b2ceac0e` | Review project, ESP notes, unsaved tab | Yes at this zoom |
| `review-whole-before-save.png` | `b2ec8ce8253c4d69a88b17b8239e4627215e50c6780ad00227da80821860c220` | Ten boxes, one sheet | Titles yes; designators no |
| `review-after-reopen-whole.png` | `3459c2158451a3539f1c6c55a0752dc8fdfc2a1a38270c94432f81dfca93dce5` | Same sheet after reopen, not blank | Titles yes; designators no |
| `review-after-reopen-cua-whole.png` | `a073b76e0c0baccd0cd5433e96f03a6b4fe6ecdfe5a3d62e6e3ceb8d6f37ed00` | Review window still showing the sheet; OS “not responding” overlay | Hang dialog obvious |

Readable critical zooms (U1+R67, no U4, U17 default-off, NFC NC, U16.5, R31–R33) were **not**
captured. EasyEDA’s CDP port closed and the window later showed a hang sheet. Distant
whole-sheet pixels are not those zooms. Treat Phase 16 designator-scale shots as **missing
evidence**, not as a pass.

Do not Force Quit the hung window to “help”. Wait or leave it. The review project is already
saved in the cloud under `dcd7e3ca…`.

## Holds that remain open

1. VAL-G3 IOMUX for CC, I2C owner, power-good, LED enable/fault.
2. RF matching and SI `TUNE_TBD`.
3. Custom footprints for `U17-PWR2` and `DVBUS-PWR1`.
4. Re-derive TPS2561 RILIM; 59 kΩ is nominal only.
5. This import proof is not promotion.
6. RQ-014, RQ-015, RQ-025, RQ-038, RQ-045 remain `PARTIAL_G3`.
7. RQ-047 `SUPERSEDED_BY_U4_REMOVAL`.
8. ERC GUI panel not exported (bridge counts only).
9. Phase 16 readable zooms after the editor is healthy again.
10. DEC-16 pads stay unplaced while VAL-G2 is open.

## What this does not do

- Does not make `dcd7e3ca…` product canonical or JLCPCB handoff.
- Does not close VAL-G2.1 or accept this receipt.
- Does not mutate live `64325d0e…`.
- Does not commit or push.
- Does not replay the 89-transaction MCP campaign.
- Does not authorise interactive beautification of `dcd7e3ca…`.

D-048 assigns `dcd7e3ca…` the role **G2.1 electrical reference / EasyEDA normalisation
oracle** and routes readable reconstruction to G2.2. That is the opposite of promotion.

**IMPORTED_NOT_CANONICAL — RECEIPT NOT YET ACCEPTED**
