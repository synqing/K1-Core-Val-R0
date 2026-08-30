# STATUS

Updated: 2026-08-30 (G2.2 HOLD PWR1 ILM repaired; canonical untouched; `JLC-SCH-READY` still OPEN)

| Lane | State |
| --- | --- |
| VAL-G0 bootstrap | COMPLETE |
| VAL-G1 Option B vs C | **CLOSED 2026-08-27 — Option C selected, Option B deferred** |
| VAL-G2 | **READY** |
| VAL-G2.0A fixture definition | **RETIRED_BY_D-042 — corrected historical inventory 181, planned 218; old 120-net threshold not met** |
| VAL-G2.0B EasyEDA qualification execution | **TERMINATED_BY_D-042 — qualification project frozen** |
| VAL-G2.1 canonical single-sheet schematic capture | **IN PROGRESS — live `64325d0e55e0435abd018defb0089a9b` remains product canonical and untouched. `dcd7e3ca…` is the G2.1 electrical reference / EasyEDA normalisation oracle (D-048), not drawing authority. Import receipt NOT YET ACCEPTED. Hub disposable + G2.2 reconstruction are the authorised EasyEDA path. `G2_1_OFFICIAL_FREEZE` waits on hub ERC (Phase K) **and** on AUX being present on the electrical graph (D-051). The live sheet is still PDM-only; the **contract** is dual-input. `JLC-SCH-READY` remains OPEN. D-049 is `RATIFIED`. D-050 is `RATIFIED / BOUND` on GT-USB-7005A / C5250872. D-051 is `RATIFIED`.** |
| VAL-G3 envelope and floorplan | NOT STARTED — non-binding direction recorded in `architecture/G3-FLOORPLAN-DOCTRINE.md` (`RECORDED_NOT_EXECUTED`) |
| VAL-G4 placement and locks | NOT STARTED |
| VAL-G5 stack, rules, planes | NOT STARTED |
| VAL-G6 route and DRC | NOT STARTED |
| VAL-G7 fabrication-output proof | NOT STARTED |
| VAL-G8 bring-up | NOT STARTED |
| SSCM-1 recovery pass | **COMPLETE_NOT_FOUND** |
| Audio L0 software SRC | NOT STARTED |
| Audio L1 ADC6120EVM | NOT STARTED |
| Audio L2 RT1062 raw SAI | NOT STARTED |
| Current-S3 baseline | NOT STARTED |
| DEC-USB-HUB | **ADOPTED** — D-049 `RATIFIED`. D-050 `RATIFIED / BOUND` on `GT-USB-7005A` / `C5250872`. H **GREEN**. `F6_VALIDITY_SOURCE` = `5V0_USB_VALID` (TPS7A2550DRVR / C2876265). EasyEDA I–L in scope on disposable projects only. |

## SSCM-1 recovery state

```text
SSCM1_RECOVERY_STATE = COMPLETE_NOT_FOUND
SSCM1_V1_AUTHORITY = UNRECOVERED_UNFROZEN
SSCM1_V2 = REQUIREMENTS_DRIVEN_REPLACEMENT
```

## VAL-G2.0 fixture state

```text
OPTION_C_SYMBOL_ESTIMATE = RESOLVED
VAL_G2_0_FIXTURE_DEFINITION = RETIRED_BY_D_042
VAL_G2_0_EDA_EXECUTION = TERMINATED_BY_D_042
```

`N_estimated_symbols_option_C = 181`. That is the corrected baseline inventory after removal of the
non-existent ADC strap; the retained historical stress plan contains 218 symbols and 119 named
nets. It does not meet the old 120-net qualification threshold and is not an accepted execution
plan. D-042 retired the lane before another qualification write.

The first generated fixture was rejected because it optimised primitive counts. D-042 terminated
further mutation of qualification project `09e9c541fd3d404082d4b92e55ae5336`. The active canonical
project is `64325d0e55e0435abd018defb0089a9b`; its runtime mutation authority lives in
`evidence/VAL-G2-2026-08-28/canonical-core-val-r0/MUTATION-STATE.json` and the paired append-only
ledger. Static status prose must not be used to infer that another write is allowed.

The bounded recovery pass is complete. Historical module fragments exist, but the frozen SSCM-1
v1 specification was not recovered and is not authority. Option B remains deferred and its
interface feasibility is unproven.

## Current execution — canonical capture authorised by D-042

RT1062 package is FROZEN: `MIMXRT1062DVJ6B`, 196-ball, 12 x 12 mm, 0.8 mm pitch (D-028).
VAL-G2.0A retains a corrected but retired historical plan. VAL-G2.0B is terminated. VAL-G2.1
canonical capture proceeds only through one closed mutation transaction at a time on the single
canonical page; the qualification project receives no further mutation.

Voice PE specimen re-derivation is D-043 (`docs/agent/VOICE-PE-SPECIMEN-VAL-R0.md`).
Receipt: `evidence/VAL-G2-2026-08-28/CURRENT-STATE-RECEIPT.md`. That lane does not write EasyEDA.

A disposable G2.1 bulk-repair candidate is **IMPORTED_NOT_CANONICAL** as review project
`dcd7e3cab2a24b9aa6e531d2b62e1b6f`. D-048 assigns that project the role **G2.1 electrical
reference / EasyEDA normalisation oracle**. It is not product canonical, not JLCPCB handoff,
and not schematic-geometry authority. The import receipt is **NOT YET ACCEPTED** (ERC item
text and critical zooms remain OPEN). Live `64325d0e55e0435abd018defb0089a9b` remains the
product project and stays untouched. Readable reconstruction is G2.2
(`K1-Core-Val-R0-G2.2-READABLE-CANDIDATE`); `JLC-SCH-READY` attaches there.
Programme: `architecture/G2.2-READABLE-SCHEMATIC.md`.
Receipt: `evidence/VAL-G2-2026-08-28/offline-bulk-repair/IMPORT-VERIFY-RECEIPT.md`.

## JLC handoff gates

```text
JLCPCB_LAYOUT = BLOCKED_BY_SCHEMATIC_PRESENTATION
JLC_SCH_READY = OPEN
JLC_LAYOUT_READY = BLOCKED_BY_JLC_SCH_READY
G2_1_OFFICIAL_FREEZE = BLOCKED_BY_HUB_ERC_PHASE_K
G2_2_OFFLINE_FIXTURE = ELECTRICAL_IDENTITY_PASS_UNFROZEN
```

Official freeze was already refused for unclassified ERC. D-049/D-050 no longer
block it. The living freeze stamp waits on hub EasyEDA ERC (Phase K). D-051
additionally forbids freezing a PDM-only audio graph: the contract now requires
the switched stereo 3.5 mm AUX lane, which is **not** yet on the live sheet.
The earlier ERC refusal is still true. AUX schematic restore waits until USB-C
3D seating is off the canvas and Captain issues an EasyEDA GO.

Offline reconstruction artefacts live under
`evidence/VAL-G2-2026-08-28/schematic-presentation/`. The current review sheet
fails the presentation checker (86 % stubs, label-only power, prison boxes).
The reconstructed V3 page matches the unpublished digest
(`0651019a5a345389…`) and is not imported, not canonical, and not a JLC stamp.

`JLC-SCH-READY` means the G2.2 reconstructed sheet is electrically frozen, professionally
readable, and EasyEDA-stable. It unblocks RFQ/package completion and schematic handoff
preparation. It does **not** unblock paid JLCPCB placement or routing.

`JLC-LAYOUT-READY` means `JLC-SCH-READY` plus final layout-relevant IOMUX, verified
footprints for every fitted part, final DXF/mechanics, exact pad count, and the required
JLC source package. Only that stamp unblocks paid JLCPCB placement/routing.

The current EasyEDA sheet is a graphical netlist. Paid layout stays blocked until both
gates close in order.

### G2.2 PWR1 ILM — 2026-08-30

This is a **candidate-scoped** electrical repair, not a product-project change.

| Project | Identity | ILM state |
| --- | --- | --- |
| **Canonical** `64325d0e55e0435abd018defb0089a9b` | CLEAN — U1-PWR1.9 already on `USB_EFUSE_ILIM`. **Not mutated.** |
| **G2.2 HOLD** `55ed9ee948734a0e903f37744b51f3b8` | HAD U1-PWR1.9 on `USB_DP_UP`. **Repaired** in `g22-pwr1-ilm-repair-2026-08-30`. |

Do not write “K1-CORE has ILM connected to USB D+” without naming the candidate. That
sentence is now false for both the live product project and the repaired HOLD.

R1-PWR1 electrical identity is **1.24 kΩ** / `RNCF0402BTC1K24` / LCSC `C2491273`.
Stale `partId` text `RC0402FR-0710KL.1` still implies 10 kΩ and must not be used as
the ohmic value. `harness/check_g22_pwr1_ilm.py` reports `METADATA_MISMATCH` and
refuses to promote an ILM→D+ binding. That check is now on the G2.2 oracle path.

This ILM blocker is cleared on HOLD. **`JLC-SCH-READY` remains OPEN** — hub wiring,
J1 0/28, AUX, ERC Phase K and the other existing gates are independent.

### Authority catch-up, 2026-08-28

The authority layer had fallen behind the live schematic. Four closed transaction families had no
authority record, and three real design rulings existed only as Python string literals. Both gaps
are closed:

| Transaction family | Now recorded as |
| --- | --- |
| `canonical-power-buck-ss-cap-wire`, `canonical-power-buck-pg-pullup-*` | D-045; `architecture/POWER-ARCHITECTURE.md` |
| `canonical-nfc-i2c-en-pullup-*` | D-046; `contracts/nfc-interface.md` |
| `canonical-nfc-regulator-decouple-*` | D-047; `contracts/nfc-interface.md` |

D-044 was the two-port ruling: `J1-PWR1` power plus direct RT1062 USB, `J7-ESP` S3 service USB.
That text stays in the register as history. D-049 now states **one** USB-C plus USB2422, with
both processors as non-removable downstream devices. D-049 is **`APPROVED_FOR_PHYSICS / PROVISIONAL`**
from Captain implement-the-plan 2026-08-29, and is **`RATIFIED`** after H GREEN
2026-08-29. D-050 is `RATIFIED / BOUND` on `GT-USB-7005A` / `C5250872`. Two
receptacles are no longer current living truth. D-014 remains `AMENDED_BY_D-044`; D-044 is
`AMENDED_BY_D-049`.

`evidence/VAL-G2-2026-08-28/canonical-core-val-r0/TAKEOVER-RECEIPT.md` is **historical**. Its
"Remaining DRC (not done this pass)" list — the NFC regulator caps and the PG decision — is closed
by D-045 and D-047 and by the transactions above. The receipt is left unedited as the record of
what was true at takeover.

`architecture/G3-FLOORPLAN-DOCTRINE.md` records the mechanical and RF direction for VAL-G3 as
`RECORDED_NOT_EXECUTED`. Nothing in it is ratified, and it contains no coordinates. Three bad
artefacts are tombstoned in `authority/05-SUPERSESSIONS.md`: the `15 x 7 mm` antenna keepout, the
four-screw mounting default and the short-edge USB-C assumption.

### Authority catch-up, 2026-08-30

D-051 restores the analogue architecture that K1-AUDIO-EVAL-R0 already specified and that
failed to migrate into `contracts/audio-interface.md`. VAL-R0 audio is dual-input: switched
stereo 3.5 mm AUX plus IM69D130 PDM through one TLV320ADC6120, with simultaneous AUX-L /
AUX-R / room-mic capture. The PDM XOR remains the microphone-lane alternate only. Ownership
is unchanged (RT1062 still owns capture). The live sheet still has no jack; this catch-up
does not rewrite that history.

## Now unblocked by VAL-G1 closure

The domain-interaction matrix can be instantiated for Option C.
Board outline and floorplan follow only after VAL-G2 closes.

## Carried forward as OPEN

Option C BGA escape, six-layer routability, and any HDI/VIPPO requirement. Not proven.
VAL-G3 gate item, and only once the real schematic exists. **No BGA escape analysis and no
CopperPilot run before VAL-G2 completes** — there is no circuit for it to route.

## Not blocked

All three audio validation levels and the current-S3 baseline. None touch the Core.
