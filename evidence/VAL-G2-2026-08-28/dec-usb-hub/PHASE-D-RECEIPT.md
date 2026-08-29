# Phase D Receipt — DEC-USB-HUB

Generated: 2026-08-29  
Evidence root: `evidence/VAL-G2-2026-08-28/dec-usb-hub/`

---

## D1 — USB2422 Main Datasheet

| Field | Value |
|-------|-------|
| Path | `datasheets/D1-USB2422-DS00001726B.pdf` |
| SHA256 | `4a9ad71cd6535368f9535d08924dbff9c21c0554d5fbf01cf06ae0d92a44fc0d` |
| Bytes | 449 402 |
| Status | **OK** — real PDF, 45 pages |

---

## D2 — USB2422 Hardware Design Checklist

| Field | Value |
|-------|-------|
| Path | `datasheets/D2-USB2422-Hardware-Checklist-DS00004196.pdf` |
| SHA256 | `beebb52d49bed3e86643beda8df5625f8479c7f307435410c441f2fe5042dbaf` |
| Bytes | 429 763 |
| Status | **OK** — real PDF |

---

## D3 — USB2422 Errata DS00001576A

| Field | Value |
|-------|-------|
| Path | `datasheets/D3-USB2422-Errata-DS00001576A.pdf` |
| SHA256 | `b7b32442a7d3ed8f53d767548e321d0c7552bc35cfc8b2099ccb0f283261128e` |
| Bytes | 162 817 |
| Status | **OK** — 8 anomalies extracted; Anomaly 3 is a hold. See `ERRATA-HOLD.md`. |

---

## D4 — NXP IMXRT1060 Electrical Specs

| Item | Path | SHA256 (first 16) | Bytes | Status |
|------|------|-------------------|-------|--------|
| IEC (industrial) | `datasheets/D4-NXP-IMXRT1060IEC.pdf` | `a4ef1fd31841678b` | 2 908 425 | **OK** — obtained from archive.org snapshot 20240926105745 |
| CEC (commercial) | `datasheets/D4-NXP-IMXRT1060CEC.pdf` | `d65fcf01020ccde2` | 2 742 929 | **OK** — obtained from archive.org snapshot 20240926105745 |

Both direct NXP URLs (`/docs/en/data-sheet/` and `/docs/en/nxp/data-sheets/`) return HTTP 404. Archive.org `if_` raw format used. PDFs verified as `%PDF-` real documents.

USB_OTG1_VBUS extract → `NXP-USB-OTG1-VBUS-EXTRACT.md` (25 mA per interface, 50 mA max, 4.40–5.5 V).

---

## D5 — ESP32-S3 USB Device Driver Reference

| Field | Value |
|-------|-------|
| Path | `datasheets/D5-ESP32-S3-usb_device.html` |
| SHA256 | `16659db160a78af4838f142c8bfb969b51c1e0cfd8d888f89a9c45e4fd9662e5` |
| Bytes | 292 049 |
| Status | **OK** — HTML snapshot of Espressif ESP-USB docs |

VBUS thresholds, 3 ms response time, and 0.75×Vdd design point extracted → `ESP-USB-SELF-POWERED-EXTRACT.md`.

---

## D5a — TPS2052B Power Switch

| Item | Path | SHA256 (first 16) | Bytes | Status |
|------|------|-------------------|-------|--------|
| TPS2052B datasheet | `datasheets/D5a-TI-TPS2052B.pdf` | `b8e3d6d124f7aa62` | 3 679 769 | **OK** |
| LCSC C130049 (SOIC-8) | `datasheets/D5a-LCSC-C130049.html` | `1bb2277b79773659` | 452 628 | **OK** |
| LCSC C2680445 (WSON-8) | `datasheets/D5a-LCSC-C2680445.html` | `d0725564f316b68f` | 389 605 | **OK** |

EN polarity active-high, OC active-low, Vin 2.7–5.5 V, 500 mA continuous, IL 0.75–1.25 A → `PROCUREMENT.md`.

---

## D5b — USB-IF UFP Powered Hub White Paper

| Field | Value |
|-------|-------|
| Path | `datasheets/D5b-USB-IF-UFP-Powered-Hub-WP-0.9.pdf` |
| SHA256 | `314090a3f075908da3287f64611cf7032d987e358301d33473e3a97a2ad5c0d1` |
| Bytes | 278 696 |
| Status | **OK** |

---

## D5c — Hirose CX70M-24P1 (CL0480-0304-0-00) — NRND / Archive

| Item | Path | SHA256 (first 16) | Bytes | Status |
|------|------|-------------------|-------|--------|
| Product page EN | `datasheets/D5c-Hirose-CX70M-24P1-product-en.html` | `c036813d85887f80` | 560 558 | **OK** — obtained via `curl -kL` in retry script |
| CX series catalog PDF | `datasheets/D5c-Hirose-CX-series-catalog-20240801.pdf` | `27cb143031e74d43` | 4 313 805 | **OK** |
| 2D drawing PDF | `datasheets/D5c-Hirose-CX70M-24P1-2D-drawing.pdf` | `6d40b7d7d7992c92` | — | **OK** (from earlier session) |
| Design guide PDF | `datasheets/D5c-Hirose-CX70M-24P1-design-guide.pdf` | `4162d79a6b6f9f71` | — | **OK** (from earlier session) |
| Spec sheet PDF | `datasheets/D5c-Hirose-CX70M-24P1-spec-sheet.pdf` | `02efb61eba81fb76` | — | **OK** (from earlier session) |

**Recommended PCB Thickness: 0.8 mm Max.** (quoted from product page JSON, table label "Recommended PCB Thickness: 0.8 ｍｍ Max.")  
Rated current: 5.0 A. Status: NRND (Not Recommended for New Designs). Archive only.

---

## D5d — Hirose CX90B2-24P (CL0480-0889-0-00) — Archive

| Item | Path | SHA256 (first 16) | Bytes | Status |
|------|------|-------------------|-------|--------|
| Product page EN | `datasheets/D5d-Hirose-CX90B2-24P-product-en.html` | `c1396afd2aa4a68f` | 560 380 | **OK** |
| Design guide PDF | `datasheets/D5d-Hirose-CX90B2-24P-design-guide.pdf` | `3475425a920d059a` | 1 453 536 | **OK** |
| Spec sheet PDF | `datasheets/D5d-Hirose-CX90B2-24P-spec-sheet.pdf` | `3c683f85ac4c85a5` | 97 719 | **OK** |
| 2D drawing PDF | `datasheets/D5d-Hirose-CX90B2-24P-2D-drawing.pdf` | `a564fab009a7c1ae` | — | **OK** (from earlier session) |

**Recommended PCB Thickness: 1.6 mm Max.** (quoted from product page JSON, table label "Recommended PCB Thickness: 1.6 ｍｍ Max.")  
Archive only.

---

## D5e — HOAUC HYC78-USBC24-140B (C3034184)

| Item | Path | Status |
|------|------|--------|
| Manufacturer page | `datasheets/D5e-HOAUC-HYC78-USBC24-140-manufacturer.html` | **OK** |
| LCSC C3034184 | `datasheets/D5e-LCSC-C3034184.html` | **OK** |
| JLC C3034184 | `datasheets/D5e-JLC-C3034184.html` | **OK** |

Manufacturer drawing PDF for this exact MPN (HYC78-USBC24-140B): **HOLD** — see `D5e-HYC-REQUEST.md`.

---

## D5f — TI ESD/TVS Devices

| Item | Path | Status |
|------|------|--------|
| SLVAF82B app note | `datasheets/D5f-TI-SLVAF82B.pdf` | **OK** |
| TPD2S300 datasheet | `datasheets/D5f-TI-TPD2S300.pdf` | **OK** |
| TPD4S201 datasheet | `datasheets/D5f-TI-TPD4S201.pdf` | **OK** |

---

## D5g — G-Switch GT-USB-7005A (C5250872)

| Item | Path | SHA256 (first 16) | Bytes | Status |
|------|------|-------------------|-------|--------|
| **Manufacturer drawing PDF** | `datasheets/D5g-GSwitch-GT-USB-7005A-manufacturer-drawing.pdf` | `abe0fb3ee8c705b2` | 964 364 | **OK** — image-only PDF (no searchable text); obtained from `dg-switch.com` |
| Manufacturer page | `datasheets/D5g-GSwitch-GT-USB-7005X-manufacturer.html` | `be6132e970c76330` | 40 793 | **OK** |
| LCSC C5250872 | `datasheets/D5g-LCSC-C5250872.html` | `303f25fead7d4fd4` | 510 807 | **OK** |

**G-Switch drawing EXISTS** — the drawing PDF is a rasterised image file (no extractable text). The "missing drawing" stop from earlier Phase D planning is cleared.  
The drawing does not state a recommended PCB thickness; D050 hold on PCB thickness compatibility vs. 1.60 mm stack remains open.  
`D5g-DRAWING-MISSING.md` was **not** written (file exists).

---

## D5h — TE Connectivity 2129691-1 (C590834) — Archive / Fallback

| Item | Path | Status |
|------|------|--------|
| Customer drawing | `datasheets/D5h-TE-2129691-customer-drawing.pdf` | **OK** |
| Family datasheet | `datasheets/D5h-TE-1-1773868-8-USB-Type-C-datasheet.pdf` | **OK** |
| Additional specs | `datasheets/D5h-TE-108-115109-2.pdf`, `D5h-TE-108-160251.pdf`, `D5h-TE-108-99061.pdf` | **OK** |
| LCSC C590834 | `datasheets/D5h-LCSC-C590834.html` | **OK** |

LCSC stock: 0 (wmsc); jlcsearch empty. Archive only.

---

## D6 — USB2422 Procurement Status

| Field | Value |
|-------|-------|
| Path | `datasheets/D6-Microchip-USB2422-product-jina.html` |
| SHA256 | `ac369695a06e88da83b6dcc8fa5003e04c7df1a71cec3b20da8250102d5d7ff6` |
| Status | **OK** — jina.ai reader snapshot of microchip.com/en-us/product/usb2422 |

Direct GET to Microchip product page returns HTTP 403. Reader snapshot confirms: **Status: In Production**.  
Quote from snapshot: *"Status: In Production — 2 Port Low Cost USB2.0 Hub Controller"*.

---

## D7 — C622610 USB2422T-I/MJ QFN-24

| Field | Value |
|-------|-------|
| MPN | USB2422T-I/MJ |
| Package | QFN-24-EP (4×4) |
| JLC class | `is_basic: false`, `is_preferred: false` → **Extended** (not Basic) |
| jlcsearch stock | 397 |
| LCSC stock | 87 (wmsc) |
| Path | `datasheets/D7-LCSC-C622610.html`, `datasheets/D7-jlcsearch-C622610.json` |

---

## Summary — Missing / Hold Items

| Item | Status |
|------|--------|
| D4 NXP direct URLs | Both HTTP 404. PDFs obtained via archive.org — **resolved** |
| D5c/D5d Hirose SSL | Retry script succeeded with `-kL`. All Hirose files present — **resolved** |
| D5e HYC manufacturer drawing | Still outstanding — **HOLD** (`D5e-HYC-REQUEST.md`) |
| D5g G-Switch drawing | **EXISTS** (`D5g-GSwitch-GT-USB-7005A-manufacturer-drawing.pdf`) |
| D6 Microchip 403 | jina.ai snapshot confirms In Production — **resolved** |

---

## Output Files Written This Session

| File | Purpose |
|------|---------|
| `USB2422-PIN-EXTRACT.md` | All 24 pins, D9–D18 items |
| `ERRATA-HOLD.md` | Anomaly 3 verbatim + Anomaly 1 and 2 one-liners |
| `NXP-USB-OTG1-VBUS-EXTRACT.md` | 25/50 mA row, 4.40–5.5 V from IEC PDF |
| `ESP-USB-SELF-POWERED-EXTRACT.md` | 4.75/4.35/3 ms/0.75×Vdd quoted from HTML |
| `PROCUREMENT.md` | Updated with TPS2052B electrical table |
| `SHA256SUMS.txt` | Rebuilt with 131 entries (all current files) |
| `PHASE-D-RECEIPT.md` | This file |
