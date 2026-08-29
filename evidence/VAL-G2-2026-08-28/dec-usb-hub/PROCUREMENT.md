# PROCUREMENT — Phase D snapshot (2026-08-29)

No MPN is bound. These are dated catalogue observations.

## USB2422 family

| Item | Observation | Source |
|---|---|---|
| Manufacturer status | **In Production** | https://www.microchip.com/en-us/product/usb2422 (2026-08-29). Direct GET 403; reader snapshot `datasheets/D6-Microchip-USB2422-In-Production-2026-08-29.md` and `datasheets/D6-Microchip-USB2422-product-jina.html`. |
| Intended LCSC line | `USB2422T-I/MJ` = **C622610**, industrial, QFN-24-EP (4×4) | Plan D7; wmsc + jlcsearch below |
| Pin-compatible substitute | **Forbidden** without a new Captain decision | — |

Datasheet on disk: `datasheets/D1-USB2422-DS00001726B.pdf`. LCSC’s C622610 PDF is the same DS00001726B family sheet (`LCSC-C622610-catalog-or-vendor.pdf`).

## C622610 — USB2422T-I/MJ

| Field | 2026-08-29 |
|---|---|
| MPN | USB2422T-I/MJ |
| Maker | Microchip |
| Package | QFN-24-EP (4×4) |
| LCSC stock (wmsc) | **87** (`LCSC-wmsc-C622610.json`) |
| jlcsearch stock | **397** (`D7-jlcsearch-C622610.json`) — same day, different API. Do not average them. |
| JLC class | `is_basic: false` → **Extended**, not Basic |
| JLC HTML | `D7-JLC-C622610.html` is a JS shell; Assembly Difficulty was not independently readable from that snapshot |
| LCSC HTML | `D7-LCSC-C622610.html` |

Treat the part as **Extended** until a later snapshot proves otherwise. Stock disagreement is a procurement watch, not a reason to pick another hub.

## C5250872 — G-Switch GT-USB-7005A (Captain-selected J1, not bound)

| Field | 2026-08-29 |
|---|---|
| MPN | GT-USB-7005A |
| LCSC | C5250872 |
| Maker | G-Switch / 品赞 |
| Package / mount | SMD, catalogue “Laminated board” / recessed |
| LCSC stock (wmsc) | **1028** ship-immediately (`LCSC-wmsc-C5250872.json`) |
| jlcsearch stock | **1040** (`D5g-jlcsearch-C5250872.json`) |
| JLC class | `is_basic: false` → **Extended** |
| JLC HTML | `D5g-JLC-C5250872.html` is a JS shell. The 2026-08-29 “Assembly Difficulty High / Standard Only” reading from the live JLC UI is **not re-proven** in this HTML file. Keep it as a named process hold for D050. |
| Manufacturer drawing | **Present**: `D5g-GSwitch-GT-USB-7005A-manufacturer-drawing.pdf` from https://dg-switch.com/uploads/soft/230408/GT-USB-7005A.pdf |
| Manufacturer 3D | `D5g-GSwitch-GT-USB-7005A-3D.zip` |
| Manufacturer page | `D5g-GSwitch-GT-USB-7005X-manufacturer.html` (USB-IF member number 13584 is a company claim, not a part TID) |
| LCSC PDF | `LCSC-C5250872-catalog-or-vendor.pdf` — **different SHA-256** from the manufacturer drawing. Cache only. |
| Unikeyic | `D5g-Unikeyic-GT-USB-7005A-paraphrase-only.html` — paraphrase only |

**Do not bind.** The manufacturer drawing exists, so the “missing drawing” stop is cleared. The drawing titles the part **Sinker1.9 / CH=0.4 / L=10.30 mm** and does **not** state a recommended PCB thickness versus D-012 1.60 mm. That thickness/sink-cutout question stays a D050 hold.

## TPS2052B (validity switch, not a bind)

| LCSC | MPN | Package | wmsc stock 2026-08-29 | jlcsearch stock |
|---|---|---|---|---|
| C130049 | TPS2052BDR | SOIC-8 | 680 | 4913 |
| C2680445 | TPS2052BDRBT | WSON-8-EP 3×3 | 42 | 42 |

Both `is_basic: false` (Extended).

**TPS2052B electrical (from DS SLVS514P, extracted 2026-08-29):**

| Parameter | Value | Source |
|-----------|-------|--------|
| EN polarity | **Active-high** ("All enable outputs are active high for the TPS205xB series") | Features / Figure caption |
| OC polarity | **Active-low** open-drain output (VOL ≤ 0.4 V at 5 mA; deglitched 15 ms) | Electrical Characteristics table |
| Input voltage range (Vin) | **2.7 V to 5.5 V** | Features list |
| Continuous current per channel | **500 mA** | Features list |
| Current limit threshold range | **0.75 A min / 1.25 A max** | Features list |
| rDS(on) typical | 70 mΩ (D/DGN packages, 5 V) | Electrical Characteristics |
| Thermal shutdown | 135 °C | Electrical Characteristics |

Note: recommended Vin max is 5.5 V; operating the switch at 5 V nominal is within the specified range.

## Archived / fallback connectors (not selected)

| Part | LCSC | 2026-08-29 stock | Notes |
|---|---|---|---|
| TE 2129691-1 | C590834 | **0** (wmsc); jlcsearch empty | Archive pack complete (`D5h-*`). Fallback only if D050-0 fails and Captain re-selects it. |
| HYCW78-USBC24-140B | C3034184 | 57 wmsc / 62 jlcsearch | Manufacturer drawing for this exact MPN is outstanding. See `D5e-HYC-REQUEST.md`. |
| CX70M-24P1 | (Hirose CL0480-0304-0-00) | — | NRND + 0.8 mm max PCB. Archive only. |
| CX90B2-24P | (Hirose CL0480-0889-0-00) | — | 1.60 mm Hirose control. Archive only. |

## What this snapshot does not do

- It does not bind J1, the hub, or TPS2052B.
- It does not change D-012 or the stack.
- It does not treat EasyEDA / LCSC footprints as rebuild authority.
- It does not authorise a pin-compatible USB2422 substitute.
