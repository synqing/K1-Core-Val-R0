# D5e — HYCW78-USBC24-140B / C3034184 request record

Status: **REQUEST OUTSTANDING**. This is a D050 hold, not a Phase D failure.

Date: 2026-08-29.

## What is on disk

| Artefact | What it is |
|---|---|
| `datasheets/D5e-LCSC-C3034184.html` | LCSC catalogue page snapshot |
| `datasheets/D5e-JLC-C3034184.html` | JLC part page (JS shell; not a readable catalogue table) |
| `datasheets/D5e-jlcsearch-C3034184.json` | jlcsearch 2026-08-29: MPN `HYCW78-USBC24-140B`, SMD, stock 62, `is_basic: false`, “Laminated board”, 5 A, 10 000 cycles |
| `datasheets/LCSC-wmsc-C3034184.json` | LCSC wmsc 2026-08-29: stock 57, HOAUC, recessed-mount 24-pos |
| `datasheets/LCSC-C3034184-catalog-or-vendor.pdf` | LCSC-hosted PDF (image-only; not a manufacturer thickness proof) |
| `datasheets/D5e-HOAUC-HYC78-USBC24-140-manufacturer.html` | HOAUC / 华宇创 page for **HYC78-USBC24-140** (not the W-suffix LCSC MPN) |

## Manufacturer identity tension

The LCSC/JLC MPN is `HYCW78-USBC24-140B`. The manufacturer page retrieved from https://www.szhoauc.com/product/usb/waterproof%20USB/359.html names **HYC78-USBC24-140** and “防水 USB TYPE C 3.1 沉板1.4 DIP+SMT”. That is not yet proven to be the same drawing as C3034184.

`沉板1.4` remains recess-geometry language, not a PCB-thickness window.

## Questions that remain unanswered (request to HOAUC)

Send to the manufacturer (page contact: twhoau@163.com / 0755-27575531) and keep the reply in this folder:

1. Recommended **PCB-thickness window** versus a 1.60 mm six-layer board (do not accept “沉板1.4” as that answer).
2. Basis for the catalogue **5 A** figure (per-contact vs collective; test method).
3. Per-contact current rating, if any.
4. Contact resistance (max).
5. USB-IF TID, or a written statement that none is claimed. Legal value: `USB_IF_TID = UNPROVEN / REQUEST_MANUFACTURER_EVIDENCE`. “No TID exists” is not an allowed close.

Until those answers and a manufacturer drawing for the exact `HYCW78-USBC24-140B` MPN are in the pack, this part is a recessed 1.60 mm **fallback candidate only**. It is not bound.
