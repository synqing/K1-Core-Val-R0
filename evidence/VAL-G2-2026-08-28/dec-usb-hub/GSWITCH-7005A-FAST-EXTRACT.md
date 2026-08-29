# GT-USB-7005A — fast numeric extract (page 1)

Source: `datasheets/D5g-GSwitch-GT-USB-7005A-manufacturer-drawing.pdf`  
SHA-256 `abe0fb3ee8c705b2c394e6f642c5268542377784c97e64785af050207d9223a0`  
Rev A0, 2023-02-01, G-Switch, model **GT-USB-7005A**, title *Horizontal Type-c 24P Female Sinker1.9 CH=0.4 L=10.30mm*.

**Thickness proof: SILENT.** The sheet never writes recommended PCB thickness, a min/max window, `t=`, or “for 1.60 mm PCB”. **Do not infer 1.60 mm from Sinker 1.9** (title) or from the drawn sink **1.95 mm**. The only **1.60** on the sheet is a *planar* spacing on the recommended PCB layout (neighbours 1.10 / 0.90 / 1.15). That is not board thickness.

CX90B2 already carries a written 1.6±0.05 mm PCB-thickness letter in the D5d Hirose design guide (`datasheets/D5d-Hirose-CX90B2-24P-design-guide.pdf` §4.3); that is a different part.

## How this was read

Local files only. No GUI. No EasyEDA.

| Probe | Result |
| --- | --- |
| `pdfinfo` | 1 page, 3006.75 × 2126.25 pt, PDF 1.7, 964 364 bytes |
| `pdftotext -layout` | empty (`\f` only) |
| pdfminer | 1 `LTPage`, 1 `LTFigure`, 1 `LTImage`; no text containers |
| `pdfimages -list` | **one raster**: 4009 × 2835 RGB, 8 bpc, **96 ppi**, object 8 |
| Content stream | CAD dimensions are **pixels in that image**, not path/text objects |

**Not vector.** There are no millimetre coordinates to dump. Page box only: media/crop `(0, 0, 3006.75, 2126.25)` pt. Embedded image object 8 at 96 ppi. Numbers below are Vision OCR of that raster plus inspection of high-zoom crops (title, side/CH, recommended layout right-hand stack).

UNIT on the sheet: **mm**. Recommended-layout note: **TOLERANCE: ±0.05**. SCALE 1:1. SIZE A4.

## Table — every labelled numeric dimension

Column *proves 1.60 mm* is **YES** only if the label is a PCB-thickness window that includes 1.60 mm. Everything else is **SILENT**.

| quantity | value | unit | page | proves 1.60 mm |
| --- | --- | --- | --- | --- |
| Recommended PCB thickness | ABSENT | — | 1 | SILENT |
| PCB thickness min / max | ABSENT | — | 1 | SILENT |
| Callout “t=1.6” / “for 1.60 mm PCB” | ABSENT | — | 1 | SILENT |
| Title Sinker (adjective, not a section) | 1.9 | mm | 1 | SILENT |
| Title CH | 0.4 | mm | 1 | SILENT |
| Title L | 10.30 | mm | 1 | SILENT |
| CH, side view (drawn) | 0.40 | mm | 1 | SILENT |
| Sink below top / into-board body, side view | 1.95 | mm | 1 | SILENT |
| Recommended-layout **planar** vertical spacing (right-hand stack; neighbours 1.10, 0.90, 1.15) | 1.60 | mm | 1 | SILENT |
| Body length (top view; matches title L) | 10.30 | mm | 1 | SILENT |
| Overall height (front/side) | 3.64 | mm | 1 | SILENT |
| Front-shell height | 2.96 | mm | 1 | SILENT |
| Feature height above a side datum | 1.88 | mm | 1 | SILENT |
| Rear/back view upper tab / housing height | 1.20 | mm | 1 | SILENT |
| Rear/back view lower tab / housing height | 1.00 | mm | 1 | SILENT |
| Shell lip / step (side) | 0.50 | mm | 1 | SILENT |
| Width over shield tabs (body rear + recommended layout) | 12.15 | mm | 1 | SILENT |
| Shell / bottom-view width | 9.15 | mm | 1 | SILENT |
| Body width (front) | 8.75 | mm | 1 | SILENT |
| Receptacle opening width | 8.35 | mm | 1 | SILENT |
| Opening-width tolerance | +0.05 / −0.03 | mm | 1 | SILENT |
| Receptacle opening height | 2.56 | mm | 1 | SILENT |
| Opening-height tolerance | ±0.04 | mm | 1 | SILENT |
| Inner-shell opening width | 6.69 | mm | 1 | SILENT |
| Inner-opening-width tolerance | +0.045 / −0.055 | mm | 1 | SILENT |
| Contact-row gap in mouth | 0.70 | mm | 1 | SILENT |
| Contact-row-gap tolerance | ±0.05 | mm | 1 | SILENT |
| Side-lead / tab vertical span (front) | 1.98 | mm | 1 | SILENT |
| Rear pin-field span (top view) | 5.50 | mm | 1 | SILENT |
| Half of rear pin-field (centreline) | 2.75 | mm | 1 | SILENT |
| SMT lead width, 12× (top view) | 0.20 | mm | 1 | SILENT |
| Pin / land pitch (top view and A-row layout) | 0.50 | mm | 1 | SILENT |
| Shell tab width on body, 4× | 1.00 | mm | 1 | SILENT |
| Side-view depth / tab-related span | 5.80 | mm | 1 | SILENT |
| Side-view inner span | 2.90 | mm | 1 | SILENT |
| Mounting-post / pin width, 2× (side) | 0.60 | mm | 1 | SILENT |
| Rear-view contact gap | 0.20 | mm | 1 | SILENT |
| Rear-view inner housing width | 6.90 | mm | 1 | SILENT |
| Bottom-view feature 4.45 (top/right of sheet) | 4.45 | mm | 1 | SILENT |
| Bottom-view / iso inner span | 3.50 | mm | 1 | SILENT |
| Tab / shell feature length, 2× | 3.20 | mm | 1 | SILENT |
| Bottom-view / iso depth | 5.00 | mm | 1 | SILENT |
| Contact width, 24× | 0.25 | mm | 1 | SILENT |
| Contact-width tolerance | ±0.04 | mm | 1 | SILENT |
| Body underside pin width | 0.80 | mm | 1 | SILENT |
| Body underside inner pin span | 1.70 | mm | 1 | SILENT |
| Body underside pin span | 2.60 | mm | 1 | SILENT |
| Body underside pin span | 3.40 | mm | 1 | SILENT |
| Body underside pin span | 5.00 | mm | 1 | SILENT |
| Body rear-tab vertical | 1.15 | mm | 1 | SILENT |
| Body rear-tab vertical | 0.90 | mm | 1 | SILENT |
| Layout A-row land width | 0.35 | mm | 1 | SILENT |
| Layout A-row land / pitch, 6× callout | 0.50 | mm | 1 | SILENT |
| Layout A-row span | 5.50 | mm | 1 | SILENT |
| Layout A-row half-span from centreline | 2.75 | mm | 1 | SILENT |
| Layout locator span | 6.90 | mm | 1 | SILENT |
| Layout outer pad/hole group | 8.95 | mm | 1 | SILENT |
| Layout locating holes, 2× | Ø0.75 | mm | 1 | SILENT |
| Layout B-row plated holes | Ø0.40 | mm | 1 | SILENT |
| Layout A-row pad height | 0.40 | mm | 1 | SILENT |
| Layout vertical offset | 0.55 | mm | 1 | SILENT |
| Layout vertical offset | 0.92 | mm | 1 | SILENT |
| Layout right-hand offset (above 1.60) | 1.10 | mm | 1 | SILENT |
| Layout B-row offset from A-row | 1.15 | mm | 1 | SILENT |
| Layout locator offset from A-row | 0.90 | mm | 1 | SILENT |
| Layout front shell-tab slot height | 1.95 | mm | 1 | SILENT |
| Layout shell-tab slot width, 2× | 1.00 | mm | 1 | SILENT |
| Layout shell-tab slot length, 4× | 1.50 | mm | 1 | SILENT |
| Layout rear-slot / tab spacing | 2.00 | mm | 1 | SILENT |
| Layout Y to rear tabs | 5.80 | mm | 1 | SILENT |
| Layout inner B-row / cutout width | 1.30 | mm | 1 | SILENT |
| Layout B-row / cutout width | 1.70 | mm | 1 | SILENT |
| Layout B-row / cutout width | 3.40 | mm | 1 | SILENT |
| Layout B-row / cutout width | 5.00 | mm | 1 | SILENT |
| Cutout inner width | 6.24 | mm | 1 | SILENT |
| Cutout / inner tab span | 9.50 | mm | 1 | SILENT |
| Cutout depth (pad datum → board-edge of cutout) | 5.10 | mm | 1 | SILENT |
| Cutout corner radius | R0.30 | mm | 1 | SILENT |
| Cutout inner feature, 2× | 0.40 | mm | 1 | SILENT |
| Layout oval / slot vertical | 2.70 | mm | 1 | SILENT |
| Recommended-layout tolerance (labelled) | ±0.05 | mm | 1 | SILENT |
| General tolerance, X. | ±0.20 | mm | 1 | SILENT |
| General tolerance, X.X | ±0.15 | mm | 1 | SILENT |
| General tolerance, X.XX | ±0.10 | mm | 1 | SILENT |
| General tolerance, X.XXX | ±0.05 | mm | 1 | SILENT |
| General tolerance, angles | ±3 | ° | 1 | SILENT |
| Current, VBUS | 5 | A | 1 | SILENT |
| Current, VCONN | 1.25 | A | 1 | SILENT |
| Current, other contacts | 0.25 | A | 1 | SILENT |
| Voltage rating | 24 | V AC | 1 | SILENT |
| Withstanding voltage | 100 | V AC / min | 1 | SILENT |
| Contact resistance, max | 40 | mΩ | 1 | SILENT |
| Insulation resistance, min | 100 | MΩ | 1 | SILENT |
| Operating temperature, min | −40 | °C | 1 | SILENT |
| Operating temperature, max | +85 | °C | 1 | SILENT |
| Mating force | 5–20 | N | 1 | SILENT |
| Unmating force | 8–20 | N | 1 | SILENT |
| Durability | 10 000 | cycles | 1 | SILENT |
| Data rate, max | 10 | Gbit/s | 1 | SILENT |

**Extracted labelled dimensions: 96** (plus 3 explicit ABSENT thickness rows). Table rows: **99**.  
**Rows with *proves 1.60 mm* = YES: 0.**

Vision OCR of the title-block tolerance column sometimes reads `±0.20` as `10.20`; the `X.` / `X.X` / `X.XX` / `X.XXX` stubs and a `‡0.05` hit on X.XXX match the usual CAD block, and the layout itself separately labels **±0.05**. Contact resistance OCR as `40ml`/`40mg` is **40 mΩ**. Insulation OCR as `100M2`/`100MQ` is **100 MΩ**.

## What this does not prove

- Title **Sinker1.9** is not a PCB-thickness window.
- Drawn **CH 0.40** is centre height, not thickness.
- Drawn **sink 1.95** is recess into the board, not a 1.60 mm stack letter.
- Layout **1.60** is plan-view spacing, not `t`.
- Electrical 5 A / 10 000 cycles are ratings, not thickness.

## Vector coordinate dump

None. Geometry is a single 4009 × 2835 raster, not stroked CAD. The only dumpable boxes are the page media box `(0, 0, 3006.75, 2126.25)` pt and image object 8.
