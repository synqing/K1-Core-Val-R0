# J1 GT-USB-7005A — independent symbol and footprint

```text
AUTHORITY = G-Switch Rev A0 drawing labels (OCR) + manufacturer STEP pin XY
EASYEDA_CACHE = reference-only, not copied, not imported
LIBRARY_PART = coordinates locked below; EasyEDA objects built at T00
D050_BIND = yes (see CONNECTOR-COMPATIBILITY.md and H0-CLOSE.md)
TOLERANCE = ±0.05 mm on recommended layout
PRIOR_SINGLE_B_ROW = WITHDRAWN
```

Pass 1–3: `PHYSICS-PASS-1-3-J1.md`. Pass 4 coordinates follow. Cached
C5250872 artwork was not used as a source.

A previous pad table put all twelve B lands in one row at Y = −1.15, aligned
with A-row X. That is **wrong**. The recommended layout is two staggered
Ø0.40 rows. This file replaces that table.

## Symbol (electrical)

24 USB-C contacts + four shell tabs + two locating holes (NPTH, no net).
SuperSpeed and SBU exist so they can carry an NC flag. They are not routed.

| Pad | Drawing name | Mate | Net |
| --- | --- | --- | --- |
| A1 | GND | First | `GND` |
| A2 | TX1+ | Second | NC |
| A3 | TX1− | Second | NC |
| A4 | VBUS | First | `5V_USB` |
| A5 | CC1 | Second | `USB_CC1` |
| A6 | D+ | Second | `USB_DP_J1` → ESD → `USB_DP_UP` |
| A7 | D− | Second | `USB_DN_J1` → ESD → `USB_DM_UP` |
| A8 | SBU1 | Second | NC |
| A9 | VBUS | First | `5V_USB` |
| A10 | RX2− | Second | NC |
| A11 | RX2+ | Second | NC |
| A12 | GND | First | `GND` |
| B1 | GND | First | `GND` |
| B2 | TX2+ | Second | NC |
| B3 | TX2− | Second | NC |
| B4 | VBUS | First | `5V_USB` |
| B5 | CC2 | Second | `USB_CC2` |
| B6 | D+ | Second | `USB_DP_J1` |
| B7 | D− | Second | `USB_DN_J1` |
| B8 | SBU2 | Second | NC |
| B9 | VBUS | First | `5V_USB` |
| B10 | RX1− | Second | NC |
| B11 | RX1+ | Second | NC |
| B12 | GND | First | `GND` |
| SHELL.TAB1–4 | shield | — | `GND` |
| LOC.1 / LOC.2 | Ø0.75 NPTH | — | none |

A/B USB2 flip: A6+B6 are the same D+ net; A7+B7 the same D− net. All four
VBUS and all four GND are landed. Every SuperSpeed/SBU pin is present and NC.

On the recommended layout, B12 sits on the A1 side (left) and B1 on the A12
side (right). That is the USB-C mirror, not a numbering error.

## Land classes (from recommended layout + 前插后贴)

The manufacturer page class is **front through-hole, rear SMT, single shell**.
The recommended layout matches that class: A-row rectangular SMT, B-row
**two staggered rows** of plated holes, four side slots, two locators,
edge cutout.

| Class | Count | Geometry | Net |
| --- | --- | --- | --- |
| A-row SMT | 12 | 0.35 × 0.92 mm, 0.50 pitch, span 5.50 | see table |
| B-row TH upper | 6 | Ø0.40 mm plated, Y = −1.80 | see table |
| B-row TH lower | 6 | Ø0.40 mm plated, Y = −2.70 | see table |
| Locators | 2 | Ø0.75 mm NPTH, span 6.90, Y = −1.10 | none |
| Shell slots rear | 2 | 1.50 × 1.00 mm, Y = −1.95, X = ±6.075 | `GND` |
| Shell slots front | 2 | 1.00 × 2.00 mm, Y = −5.80, X = ±6.075 | `GND` |
| Cutout | 1 | 9.50 / 6.24 mm stepped, depth 5.10, R0.30 | board outline |

## Pass 4 — coordinates

Frame: millimetres. Origin: connector centreline X = 0, **A-row pad centres
Y = 0**. Positive Y is into the board (away from the mating face / edge).
The board-edge / cutout lies at **negative Y**. Layout tolerance ±0.05 mm.

Labels were read from the Rev A0 recommended-layout view by Apple Vision
OCR on `datasheets/_extract/hires/layout_a.png` and
`datasheets/_extract/measured/crop_pcb_layout.png` (confidence 1.000 on
every number used below). STEP pin XY corroborates the lower B-row and
fills the one upper-row pair whose 2.60 mm span was not OCR'd.

### A-row SMT (CONFIRMED)

| Pad | X | Y | Shape | Status |
| --- | --- | --- | --- | --- |
| A1 | −2.75 | 0 | 0.35 × 0.92 SMT, long axis Y | CONFIRMED 2.75 / 0.50 / 5.50 / 0.35 / 0.92 |
| A2 | −2.25 | 0 | same | CONFIRMED |
| A3 | −1.75 | 0 | same | CONFIRMED |
| A4 | −1.25 | 0 | same | CONFIRMED |
| A5 | −0.75 | 0 | same | CONFIRMED |
| A6 | −0.25 | 0 | same | CONFIRMED |
| A7 | +0.25 | 0 | same | CONFIRMED |
| A8 | +0.75 | 0 | same | CONFIRMED |
| A9 | +1.25 | 0 | same | CONFIRMED |
| A10 | +1.75 | 0 | same | CONFIRMED |
| A11 | +2.25 | 0 | same | CONFIRMED |
| A12 | +2.75 | 0 | same | CONFIRMED |

Pad length **0.92 mm** is the recommended-layout land (OCR). Do not
substitute the 0.20 mm lead width from the part view.

### B-row TH — two staggered rows (CONFIRMED as a class)

Lower (mouth) X matches drawing pair spans **1.70 / 3.40 / 5.00** and
STEP front-pin X ±0.850 / ±1.700 / ±2.500. Upper X uses drawing **1.30 /
6.24**; the middle pair ±1.30 is the STEP rear-pin centre (2.60 mm span
not OCR'd). Y uses labelled **2.70** to the lower row and **0.90** stagger.

| Pad | X | Y | Shape | Status |
| --- | --- | --- | --- | --- |
| B12 | −3.12 | −1.80 | Ø0.40 TH | CONFIRMED 6.24 |
| B9 | −1.30 | −1.80 | Ø0.40 TH | STEP rear pin X |
| B7 | −0.65 | −1.80 | Ø0.40 TH | CONFIRMED 1.30 |
| B6 | +0.65 | −1.80 | Ø0.40 TH | CONFIRMED 1.30 |
| B4 | +1.30 | −1.80 | Ø0.40 TH | STEP rear pin X |
| B1 | +3.12 | −1.80 | Ø0.40 TH | CONFIRMED 6.24 |
| B11 | −2.50 | −2.70 | Ø0.40 TH | CONFIRMED 5.00 |
| B10 | −1.70 | −2.70 | Ø0.40 TH | CONFIRMED 3.40 |
| B8 | −0.85 | −2.70 | Ø0.40 TH | CONFIRMED 1.70 |
| B5 | +0.85 | −2.70 | Ø0.40 TH | CONFIRMED 1.70 |
| B3 | +1.70 | −2.70 | Ø0.40 TH | CONFIRMED 3.40 |
| B2 | +2.50 | −2.70 | Ø0.40 TH | CONFIRMED 5.00 |

`2-0.40` sits next to the B-row. Treat B12/B1 as plated Ø0.40 unless a
later G-Switch letter says those two are 0.40 slots.

### Locators, shell tabs, cutout

| Feature | X | Y | Shape | Status |
| --- | --- | --- | --- | --- |
| LOC.1 | −3.45 | −1.10 | Ø0.75 NPTH | CONFIRMED 6.90 / 2-Ø0.75 / 1.10 |
| LOC.2 | +3.45 | −1.10 | Ø0.75 NPTH | same |
| SHELL.TAB1 | −6.075 | −1.95 | slot 1.50 × 1.00 | CONFIRMED 12.15 / 1.95 / 4-1.50 / 2-1.00 |
| SHELL.TAB2 | +6.075 | −1.95 | same | rear pair (toward A-row) |
| SHELL.TAB3 | −6.075 | −5.80 | slot 1.00 × 2.00 | CONFIRMED 5.80 / 2.00 |
| SHELL.TAB4 | +6.075 | −5.80 | same | front pair (toward edge) |
| CUTOUT | ±4.75 front / ±3.12 inner | 0 to −5.10 | R0.30 | CONFIRMED 9.50 / 6.24 / 5.10 / R0.30 |

`1.95` and `5.80` are **both from the A-row datum**, not a 5.80 mm span
between tab centres. STEP leg Z, re-datumed to A-row, lands at
Y ≈ −1.93 and Y ≈ −5.78. That is the same pair.

Slot mill vs plated: **plated** for the four shell tabs (they are GND).
Locators stay NPTH unless a later G-Switch letter says plated.

The **1.60 mm** figure next to `2-Ø0.75` is a **planar** offset on the
recommended layout. It is **not** board thickness.

## Board-edge datum, sink, insertion axis

| Quantity | Value | Source |
| --- | --- | --- |
| PCB top in STEP | Y = 0.400 mm (120 Cartesian points, exact) | `GT-USB-7005A.stp` |
| Shell lowest Y | −1.480 mm | same STEP |
| Sink below PCB top | **1.880 mm** | 0.400 − (−1.480) |
| On D-012 1.60 mm | **0.280 mm** below the bottom face | 1.880 − 1.60 |
| TH pin reach below top | **1.100 mm** | STEP tip Y ≈ −0.700 |
| TH emergence on 1.60 mm | none (0.50 mm short of the bottom) | same |
| Insertion axis | horizontal, CH **0.40 mm** below PCB top | drawing CH 0.40 + STEP |
| Board-edge / cutout front | Y = −5.10 mm in this frame | labelled 5.10 |

The body occupies a **through cutout**, not a pocket. Bottom copper, parts
and enclosure must clear **0.30 mm** under the shell in the cutout.

## Verification checklist (T00 must prove)

- [ ] 24 signal pads present, numbers A1–A12 / B1–B12
- [ ] B-row is **two staggered rows**, not one aligned row
- [ ] A6+B6 common D+; A7+B7 common D−
- [ ] four VBUS on `5V_USB`; four GND on `GND`
- [ ] CC1=A5, CC2=B5
- [ ] eight SuperSpeed + two SBU = NC
- [ ] four shell tabs on `GND`
- [ ] two Ø0.75 locators, no net
- [ ] cutout on board outline, not a copper pour hole
- [ ] EasyEDA/LCSC C5250872 cache not imported as the part

Machine table: `J1-GT-USB-7005A-pads.json` and `.csv`.
To-scale land pattern: `J1-GT-USB-7005A-FOOTPRINT.html`.

## Cache comparison (reference only)

EasyEDA C5250872 may be opened **read-only** after T00 to count pads. It is
not the source of any coordinate in this file.
