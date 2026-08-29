# CONNECTOR-COMPATIBILITY — D-050

Physics-before-geometry Pass 1–3 for J1: `PHYSICS-PASS-1-3-J1.md`.
Measured extract: `GSWITCH-7005A-MEASURED-EXTRACT.md`.
Footprint evidence: `J1-GT-USB-7005A-FOOTPRINT-REBUILD.md`.
Mechanical close: `H0-CLOSE.md`.
DFM request: `D5g-GSWITCH-JLC-DFM-REQUEST.md` (outstanding; process hold).

No stack mutation. No EasyEDA cache as footprint. MPN bound by geometric
section analysis, not by “Sinker 1.9” / CH 0.4 / “laminated board”.

```text
D050_STATUS = BOUND
SELECTED = GT-USB-7005A / C5250872
BOUND = yes
BIND_ROUTE = GEOMETRIC_SECTION + PROCESS_CLASS + STEP_SMT_DATUM
D012 = 1.60 mm / six layers UNCHANGED
CX70M_ON_160 = NO-GO
TE_2129691 = ARCHIVED_FALLBACK
CX90B2 = 1.60 mm HIROSE CONTROL (not selected)
THICKNESS_ON_DRAWING = SILENT (not used as the bind)
FOOTPRINT_REBUILD = J1-GT-USB-7005A-FOOTPRINT-REBUILD.md (A + staggered B + tabs + cutout)
BOTTOM_PROTRUSION = 0.280 mm keepout
PRIOR_SINGLE_B_ROW = WITHDRAWN
```

Drawing file: `datasheets/D5g-GSwitch-GT-USB-7005A-manufacturer-drawing.pdf`
(1 page, Rev A0, 2023-02-01). SHA-256
`abe0fb3ee8c705b2c394e6f642c5268542377784c97e64785af050207d9223a0`.
`pdftotext` extracted no text (CAD drawing). Labels were OCR'd from the
rendered sheet. STEP SHA-256
`3e8f2300c222477a26adf1221f91e5e01220b0216d33b7826a362ff13ea3b8d5`.

## D050-0 — GT-USB-7005A / C5250872 (bound)

Title on the sheet: **Horizontal Type-c 24P Female Sinker 1.9 CH=0.4 L=10.30mm**.

| Item | From drawing / STEP | vs D-012 1.60 mm |
| --- | --- | --- |
| Body length L | 10.30 mm CONFIRMED | n/a |
| Width over tabs | 12.15 mm CONFIRMED | n/a |
| CH | **0.40 mm** labelled | **not a PCB thickness** |
| Sinker 1.9 | title only | **not a PCB thickness** (same class as HYC `沉板1.4`) |
| Recommended PCB thickness | **SILENT** | Bind is D050-0c, not this cell |
| Thickness / cutout relationship | STEP sink 1.880 mm vs 1.60 mm | **0.280 mm bottom keepout** |
| 1.60 mm figure on recommended layout | planar offset next to `2-Ø0.75` | **not board thickness** |
| SMT pitch | 0.50 mm; A1–A12 span 5.50 mm; land 0.35 × 0.92 | footprint locked |
| B-row | **two staggered** Ø0.40 rows | not a single aligned row |
| Shield tabs | **four** | D050-4; XY in footprint rebuild |
| Hybrid lands | Front slots + rear SMT | JLC High-difficulty process hold |
| SuperSpeed | all 24 contacts exist | stay NC on USB2 hub |
| Ratings on sheet | 5 A VBUS / 1.25 A VCONN / 0.25 A others; 24 V; 40 mΩ max; 10 000 cycles; −40 to +85 °C; mate 5–20 N / unmate 8–20 N | 5 A is headroom, not a PD grant |
| Manufacturer / JLC letter | **ABSENT** | request written; not the bind |

## D050-0c — 1.60 mm geometric section (the bind)

The drawing is still **SILENT** on a recommended PCB-thickness window.
That silence is not a bind. The bind is this section. Independently
reproduced 2026-08-29 (this H0 pass), not inherited from a prior table.

**Process class (manufacturer page, not a thickness adjective).**
GT-USB-7005A is listed as 前插后贴单壳 — front through-hole, rear SMT,
single shell (`D5g-GSwitch-GT-USB-7005X-manufacturer.html`). That class
seats SMT on the **top** and puts the body in an edge cutout. It does
**not** pinch the board between top and bottom flanges. CX70M is the
other class: Hirose writes **0.8 mm max** because the board is pinched.
That contrast is why CX70M stays NO-GO and why a missing G-Switch
thickness sentence is not the same defect.

**STEP SMT datum (9 470 Cartesian points).**
Rear SMT tails isolated as points with Y = **0.400000** exactly
(120 points), Z ≤ −4.20 mm, |X| ≤ 3.05 mm. That plane is PCB top, not
the STEP-origin bbox and not “Y-min of the solid”.

Shell / mouth lowest Y = **−1.480 mm**.
Sink below PCB top = 0.400 − (−1.480) = **1.880 mm**.
On D-012 **1.60 mm**: bottom protrusion = 1.880 − 1.60 = **0.280 mm**.

TH pin tips sit at Y ≈ −0.700 mm → **1.100 mm** below PCB top. On
1.60 mm they stop **0.50 mm short** of the bottom. They do not emerge
and they do not set a thickness.

Legs occupy STEP Y ≈ −0.50 … +0.70. They do not form a bottom clamp
at 1.60 mm or any other named thickness.

To-scale section: `J1-SECTION-160.html` (40 px = 1 mm).

This is **not** “1.60 − 1.48 from an undatumed bbox”. It is not “Board
Sink 1.9”. It is not CH 0.4 mm used as thickness. CH 0.40 mm on the
drawing is the plug axis below the top and agrees with the same datum
(STEP axis 0.40 mm below Y = 0.400).

**Legs / TH** pass into slots / holes from the top (pin-in-paste /
front-insert). JLC **Assembly Difficulty High** remains a process hold,
not a thickness reject and not a silent 0.8 mm edit.

**Keepout.** Bottom copper, parts and enclosure must clear **0.30 mm**
under the shell in the cutout. Write that on the G3 floorplan when
layout starts. Do not change D-012.

Independently rebuilt symbol/footprint: **locked** in
`J1-GT-USB-7005A-FOOTPRINT-REBUILD.md` (A-row SMT, **staggered** B-row
Ø0.40 TH, four tabs, two locators, cutout). EasyEDA cache was not copied.

JLC 2026-08-29 snapshot: Extended, SMT Assembly, **Assembly Difficulty
High**. Process hold, not a cutout waiver.

LCSC stock on the dated snapshot is procurement evidence only.

## D050-0b — TE 2129691-1 / C590834

Archive pack on disk (`D5h-*`). Customer drawing OCR (sheets 2–3) names
**PCB SURFACE** and hybrid lands. It does **not** write a recommended
PCB-thickness window in the extractable labels. Bind only if D050-0
fails **and** Captain re-selects it. Not selected now.

## D050-1 — CX70M vs D-012

Hirose product snapshots + CX series catalog PDF on disk (`D5c-*`).
Handoff and Hirose page: recommended PCB thickness **0.8 mm max**, 5.0 A,
NRND, TID **5,200,000,077**.

**CX70M on current 1.60 mm K1 = NO-GO.**

- CX-PATH-A (whole board 0.8 mm): read-only study only. `pcb/STACKUP-STATUS.md`
  and D-012 **not mutated**.
- CX-PATH-B stepped tongue: **NO-GO** without written JLC DFM for this stack.
- CX-PATH-C USB daughterboard: poor VAL default (second high-current interconnect).

## D050-2 — HYCW78

`沉板1.4` = recess geometry, not “designed for 1.4 mm PCB”. Manufacturer
drawing / thickness window / 5 A qualification / TID: **request outstanding**.
`USB_IF_TID = UNPROVEN / REQUEST_MANUFACTURER_EVIDENCE`. Fallback only.
Same bar as G-Switch: no bind from catalogue adjectives.

## D050-3 — CX90B2 control

Product / spec / design-guide on disk (`D5d-*`). Hirose CX90B2 design guide
§4.3 (quoted from the PDF): **recommended PCB thickness is 1.6±0.05 mm**
considering 1.2±0.1 mm PIP leg length. That is the strongest *written*
1.60 mm letter in the pack. Role: on-board Hirose control if sink-mount
assembly is later rejected. **Not selected** — G-Switch section cleared
1.60 mm without changing D-012 and without giving up the recessed face.

## D050-4 — 24-pin plus shell (winner contract; same nets if fallback)

```text
A4/A9/B4/B9     → 5V_USB
A1/A12/B1/B12   → GND
SHELL / four shield tabs → signal GND + stitching (VAL default)
                         chassis option remains named, not implemented
A6+B6           → low-C ESD → USB_DP_UP → USB2422
A7+B7           → low-C ESD → USB_DM_UP → USB2422
A5 CC1          → Rd + sense + CC-PROTECTION
B5 CC2          → Rd + sense + CC-PROTECTION
SBU1/SBU2       → NC
all SSTX/SSRX   → NC
```

Today’s G2.1 symbol is USB4105-GF-A (20 pins; SuperSpeed absent). G-Switch
drawing shows all 24 contacts plus four tab slots. Missing shell-tab nets
fail the contract. Never drop the EasyEDA C5250872 cache on the sheet.

## D050-6 — power-domain pointer

See `VBUS-CONTRACT.md` F9. Owned by the H0f sibling. Not edited here.
A 5 A connector does not change Default / 1.5 A / 3 A advertisement math.

## Fallback score (same bar)

| Candidate | 1.60 mm evidence | Why it did not win |
| --- | --- | --- |
| **GT-USB-7005A** | Geometric section (sink 1.880 mm, 0.280 mm keepout) + 前插后贴 class + STEP SMT datum Y=0.400 | **Bound.** Captain-selected. Recessed face kept. Drawing thickness window still SILENT. |
| TE 2129691-1 | Hybrid; OCR shows PCB SURFACE, no thickness window | Captain superseded it. Same missing-window class as G-Switch, weaker 3D pack in this repo. |
| HYCW78 | Thickness window still outstanding | Same 沉板 trap. No manufacturer drawing bind. |
| CX90B2 | Hirose §4.3 **1.6±0.05 mm** | Strongest written letter. On-board control only — gives up the recessed face. |
| CX70M | Hirose **0.8 mm max** | NO-GO on 1.60 mm. |

Winner is G-Switch because the allowed geometric-section route cleared
1.60 mm on the Captain-selected recessed part. CX90B2 would win only if
that section had failed and the programme accepted an on-board Hirose.

## Exit D050

**Usable bind path: proven.** D-050 **BOUND** on GT-USB-7005A / C5250872.
CC letter remains in `CC-PROTECTION.md` (not re-opened here). No
board-thickness edit. D-012 unchanged.
