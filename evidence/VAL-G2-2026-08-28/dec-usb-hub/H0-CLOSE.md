# H0-CLOSE — D-050 mechanical / footprint bind

```text
H0_MECHANICAL_BIND = YES
WINNER_MPN = GT-USB-7005A
WINNER_LCSC = C5250872
THICKNESS_160_PROVEN = YES
PROOF_ROUTE = GEOMETRIC_SECTION + PROCESS_CLASS + STEP_SMT_DATUM
THICKNESS_ON_DRAWING = SILENT
FOOTPRINT_COMPLETE = YES
PRIOR_SINGLE_B_ROW = WITHDRAWN
D012 = 1.60 mm UNCHANGED
EASYEDA = not written
LIVE_64325d0e = untouched
VBUS_CONTRACT = not edited
PLAN_FILE = not edited
```

## What happened

The manufacturer drawing was read again from the file, not from the
previous pad table. The PDF has no text layer. Every used millimetre
was either an OCR'd label on the recommended-layout view or a Cartesian
point in the manufacturer STEP.

The earlier lock that put twelve B-row holes in one line at Y = −1.15,
aligned with A-row X, is **withdrawn**. The drawing is two staggered
Ø0.40 rows. The new table is in `J1-GT-USB-7005A-FOOTPRINT-REBUILD.md`,
`J1-GT-USB-7005A-pads.json` and `.csv`.

## 1.60 mm

**YES — proven.** Not from “Sinker 1.9”, not from CH 0.4, not from
“laminated board”, and not from the **1.60 mm planar** offset next to
`2-Ø0.75` on the land pattern.

Independently reproduced from `GT-USB-7005A.stp` (9 470 points):

| Quantity | Value |
| --- | --- |
| SMT solder-face Y | **0.400000 mm** (120 points, exact) |
| Shell lowest Y | **−1.480 mm** |
| Sink below PCB top | **1.880 mm** |
| On D-012 1.60 mm | **0.280 mm** below the bottom face |
| TH tip reach below top | **1.100 mm** (does not emerge) |

Process class on the G-Switch page is 前插后贴单壳: SMT on the top, body
in a cutout, no pinch. That is why a missing thickness sentence is not
the CX70M defect. JLC “Assembly Difficulty High” stays a process hold.

## Footprint

**Complete** for an authoritative rebuild: A-row SMT, staggered B-row
TH, four shield tabs, two locators, stepped cutout, board-edge datum,
sink, insertion axis. One upper-row pair (B9/B4 at X = ±1.30) is the
STEP rear-pin centre; the 2.60 mm span was not OCR'd. `2-0.40` may
mean B12/B1 are 0.40 slots; they are carried as plated Ø0.40 until a
later letter says otherwise.

## Why this winner

Captain selected GT-USB-7005A. The same bar was applied to the recorded
fallbacks. CX90B2 has the strongest *written* 1.60 mm letter (Hirose
§4.3 1.6±0.05 mm) but is on-board and was not selected. TE 2129691-1
has no thickness window in the OCR'd drawing. HYCW78 still has no
manufacturer thickness letter. CX70M remains NO-GO (0.8 mm max).

G-Switch won because the allowed geometric-section route cleared 1.60 mm
on the selected recessed part without editing D-012.

## Remaining H0 holes (not a mechanical NO)

These do **not** reopen the mechanical bind:

1. Drawing still **SILENT** on a recommended PCB-thickness window. The
   outstanding G-Switch / JLC request stays a process hold, not a bind
   gate.
2. B9/B4 X = ±1.30 is STEP-corroborated; 2.60 mm was not OCR'd.
3. B12/B1 may be 0.40 slots (`2-0.40`).
4. EasyEDA library objects are **not** built here (T00, after H GREEN).
5. **H0c** CC-PROTECTION letter is already written; not re-opened.
6. **H0d–H0g** (budget, KILL, `F6_VALIDITY_SOURCE`, F8 clocks) are the
   H0f sibling’s VBUS pack. Not edited.

## Mechanical bind

**YES.**
