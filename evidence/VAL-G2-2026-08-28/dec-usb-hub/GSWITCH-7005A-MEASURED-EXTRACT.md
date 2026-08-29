# GT-USB-7005A — measured extract (thickness, sink, cutout)

Truth source: `datasheets/D5g-GSwitch-GT-USB-7005A-manufacturer-drawing.pdf`
(Rev A0, 2023-02-01, 1 page, CAD, no extractable text). SHA-256
`abe0fb3ee8c705b2c394e6f642c5268542377784c97e64785af050207d9223a0`.

D-012 stays **1.60 mm**. This file does not change it.

```text
RECOMMENDED_PCB_THICKNESS_ON_DRAWING = SILENT
THICKNESS_VS_D012_160 = PROVEN_BY_GEOMETRIC_SECTION
SINK_CUTOUT_VS_THICKNESS_RELATIONSHIP = STEP_SMT_DATUM (sink 1.880 mm; 0.280 mm bottom keepout)
MANUFACTURER_OR_JLC_DFM_LETTER = ABSENT (request written; not the bind)
BIND = yes
BIND_ROUTE = GEOMETRIC_SECTION + PROCESS_CLASS + STEP_SMT_DATUM
INDEPENDENT_REPRO_2026_08_29 = SMT_Y_0.400000_n120 ; ymin_-1.480 ; sink_1.880 ; protrusion_0.280 ; th_reach_1.100
B_ROW = TWO_STAGGERED_D0.40 (single aligned row withdrawn)
```

“Board Sink 1.9”, “CH 0.4 mm”, and “the drawing exists” are **not** a
thickness window. Same class of error as HYC `沉板1.4`.

## How this was read

The PDF is a plotted CAD sheet (`pdftotext` = empty). Facts below are
copied from the rendered page (72 DPI preview + 144 DPI re-render under
`datasheets/_extract/measured/`). A number that only appeared in one crop
caption, or that conflicted across crops, is **UNCERTAIN**. A number that
is on the title block or is labelled the same way on more than one view
is **CONFIRMED**.

Manufacturer 3D (`D5g-GSwitch-GT-USB-7005A-3D.zip` → `GT-USB-7005A.stp`)
is **secondary**. It has no PCB solid and no recommended-thickness note.

Manufacturer web copy (`D5g-GSwitch-GT-USB-7005X-manufacturer.html`)
says “沉板1.9/2.1mm；CH0.4mm”. That is family recess language, not a
PCB-thickness window, and it is **not** the drawing.

## Dimensions that bear on PCB thickness, sink, or cutout

| ID | What | Value | Class | Bears on 1.60 mm? |
| --- | --- | --- | --- | --- |
| T1 | Title “Sinker1.9” | present | CONFIRMED (title) | **No.** Recess/marketing name. Not a recommended thickness. |
| T2 | Title / labelled CH | **0.40 mm** | CONFIRMED | **No.** Centre-height / offset language. Not a thickness. |
| T3 | Title L | **10.30 mm** | CONFIRMED | Body length only. |
| T4 | Recommended PCB thickness | — | **SILENT** | **This is the bind gate.** Drawing does not write a window. |
| T5 | Compatible PCB thickness min/max | — | **SILENT** | Cannot prove 1.60 mm in or out. |
| T6 | “For 1.60 mm PCB” / “t=1.6” callout | — | **SILENT** | A **1.60 mm** figure appears on the **recommended PCB layout** as a **planar** spacing between two layout features. That is **not** board thickness. Do not bind on it. |
| T7 | Thickness-to-cutout relationship (how deep the body sits in a named board) | — | **SILENT** | Missing. Inference from CH / Sinker / leg length is forbidden as a bind. |
| T8 | Width over shield tabs | **12.15 mm** | CONFIRMED | Envelope / tab span. |
| T9 | SMT pitch | **0.50 mm** | CONFIRMED | Lands, not thickness. |
| T10 | A1–A12 land span | **5.50 mm** | CONFIRMED | 11 × 0.50. |
| T11 | Locating holes | **2 × Ø0.75 mm** | CONFIRMED | Drill, not thickness. |
| T12 | Shield / shell tabs | **four** | CONFIRMED | Count is on the recommended layout. |
| T13 | Layout tolerance | **±0.05 mm** | CONFIRMED | Recommended-layout note. |
| T14 | Board-cutout outline | 9.50 / 6.24 / 5.10, R0.30 | CONFIRMED (OCR on recommended layout) | 8.95 is a separate top-of-layout span (locators / slots), not the cutout width. |
| T15 | Hybrid lands | Front through-slots + rear SMT | CONFIRMED as a class | Process hold (JLC High-difficulty), not a thickness proof. |
| T16 | Front / rear tab slot sizes | 4-1.50, 2-1.00, 2.00; Y = −1.95 and −5.80 from A-row | CONFIRMED (OCR + STEP leg Z) | DFM, not thickness. |
| T17 | Height of the part (orthographic) | **3.64 mm** class | CONFIRMED (matches STEP dy 3.660) | Envelope. Does not name PCB t. |
| T18 | Opening / mouth dimensions | 8.35 (+0.05/−0.03) class and a smaller inner opening | CONFIRMED as a family of numbers; which feature is which is view-dependent | Enclosure, not PCB t. |
| T19 | Mating / unmating force | 5–20 N / 8–20 N | CONFIRMED (spec block) | Insertion load. Not a thickness. |
| T20 | Current / cycles | 5 A VBUS, 1.25 A VCONN, 0.25 A others; 10 000 cycles; 40 mΩ max; 24 V; −40 to +85 °C | CONFIRMED (spec block) | Electrical/mechanical rating. 5 A is not a PD grant. |
| T21 | B-row lands | two staggered Ø0.40 rows; pair spans 1.30 / 1.70 / 3.40 / 5.00 / 6.24; Y −1.80 / −2.70 | CONFIRMED as a class | A single aligned B-row is withdrawn. |

## Secondary STEP envelope (not a bind)

Parsed `GT-USB-7005A.stp` (9 470 `CARTESIAN_POINT` records):

| Axis | Min | Max | Span |
| --- | --- | --- | --- |
| X | −6.195 | 6.195 | 12.390 mm |
| Y | −1.480 | 2.180 | 3.660 mm |
| Z | −5.368 | 5.000 | 10.368 mm |

Span agrees with drawing L = 10.30 mm, height ≈ 3.64 mm, width-over-tabs
≈ 12.15 mm. **The STEP file does not contain a PCB.** Which axis origin
is “top of board” is **not** the bbox origin. Rear SMT tails isolate at
**Y = 0.400 mm** (120 points). That plane is PCB top. Shell min Y =
−1.480 mm → sink 1.880 mm. On 1.60 mm: 0.280 mm bottom keepout. Do **not**
compute “1.60 − 1.48 = 0.12 mm remain” from the undatumed bbox.

## What is explicitly not enough

- Catalogue “Laminated board”
- Unikeyic “Board Sink 1.9 CH 0.4 mm”
- Title **Sinker1.9** + labelled **CH 0.40**
- LCSC in-stock count
- EasyEDA / LCSC C5250872 artwork
- STEP protrusion
- A 1.60 mm **layout** dimension on the recommended land pattern

## Disposition

**Mechanical bind cleared by D050-0c**, not by this drawing’s missing
thickness window. D-050 **BOUND**. Do not change D-012. JLC High-difficulty
process hold remains written.
