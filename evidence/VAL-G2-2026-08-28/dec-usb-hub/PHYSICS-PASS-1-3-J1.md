# Physics-before-geometry Pass 1–3 — J1 GT-USB-7005A

Required before any coordinate claim. Coordinates live in
`J1-GT-USB-7005A-FOOTPRINT-REBUILD.md` and are Pass 4 only where Pass 3
already names two pads.

No EasyEDA write. Cached C5250872 is reference-only and was **not**
copied into a library part.

## Pass 1 — Authority

| Fact class | What is true | External source in this repo | Lineage (not authority) |
| --- | --- | --- | --- |
| Selected MPN | GT-USB-7005A / C5250872 | Captain D-050; LCSC/JLC snapshots | EasyEDA cache |
| Mechanical envelope, pin names, recommended layout | As drawn on Rev A0; B-row is two staggered Ø0.40 rows | `D5g-GSwitch-GT-USB-7005A-manufacturer-drawing.pdf` | Unikeyic paraphrase; LCSC PDF (different SHA); prior single-row B table |
| PCB thickness vs 1.60 mm | **SILENT on drawing; PROVEN by section** | STEP SMT datum Y=0.400000 (n=120); sink 1.880 mm; 0.280 mm keepout | “Sinker 1.9”, CH 0.4, “laminated board”, layout “1.60” |
| 3D solid envelope | 12.390 × 3.660 × 10.368 mm bbox | `GT-USB-7005A.stp` (secondary) | — |
| Electrical 24-pin + shell contract | D050-4 nets | `CONNECTOR-COMPATIBILITY.md` | G2.1 USB4105 symbol |
| USB2-only routing | SuperSpeed / SBU NC | D-049 / USB2422 is USB 2.0 | — |
| Board thickness lock | 1.60 mm / six layers | D-012; `pcb/STACKUP-STATUS.md` | CX70M 0.8 mm preference |

If the drawing had been absent, this pass would stop. The drawing is
present. Thickness window on the drawing remains unverifiable. Compatibility
is proved by geometric section, not by that missing sentence.

## Pass 2 — Physics (every J1 net / land class)

| Class | Members | Position controls | How it fails |
| --- | --- | --- | --- |
| Rail | A4, A9, B4, B9 → `5V_USB` | IR drop, inrush, shared inlet | One VBUS pin left floating starves current and heat |
| Return | A1, A12, B1, B12 → `GND` | Loop area with VBUS and USB2 | Split GND at the receptacle |
| High di/dt / ESD | A6+B6 D+, A7+B7 D− → ESD → hub US | Pair relationship + connector TVS budget | SuperSpeed leftovers; second ESD island |
| High-Z / sense | A5 CC1, B5 CC2 → Rd + ADC taps | Leakage vs advertisement | Series R / protector lying about Rp |
| NC | SBU1/2, all SSTX/SSRX | Must not exist as stubs | “For later” SuperSpeed |
| Thermal / mechanical | Four shell tabs + two Ø0.75 locators | Insertion load (5–20 N), shield stitch | Missing tab net; unanchored mid-mount |
| Decoupling (inlet) | Raw `5V_USB` C vs protected bulk | Distance to J1 VBUS **and** which side of the eFuse | 22 µF raw holds `VBUS_DET` up |

Group by what they connect to, not by “all USB-C pads in a row”.

## Pass 3 — Relationships (two pad IDs + reason)

| # | Pad A | Pad B | Why |
| --- | --- | --- | --- |
| R1 | J1.A4 | J1.A9 | Both VBUS; must be the same rail `5V_USB` |
| R2 | J1.B4 | J1.B9 | Same |
| R3 | J1.A4 | J1.A1 | VBUS–GND loop starts at the receptacle |
| R4 | J1.A6 | J1.B6 | USB-C D+ pair; short at connector |
| R5 | J1.A7 | J1.B7 | USB-C D− pair |
| R6 | J1.A6 | D1.1 | ESD first; hub US after |
| R7 | J1.A5 | RCC1-PWR1.1 | Rd on CC1, J1-only after J7 delete |
| R8 | J1.B5 | RCC2-PWR1.1 | Rd on CC2 |
| R9 | SHELL.TAB1 | SHELL.TAB2 | Insertion load is a four-tab loop, not one tab |
| R10 | SHELL.TAB3 | SHELL.TAB4 | Same |
| R11 | SHELL.* | GND | VAL default stitch; missing tab net fails D050-4 |
| R12 | J1.A4 | C1-PWR1.1 | Raw inlet C must be small and on `5V_USB` |
| R13 | U1-PWR1.5 | U1-PWR1.6 | eFuse isolates raw from protected bulk |
| R14 | J1.A2 | (none) | SuperSpeed NC — no second pad, no stub |

No Pass 4 coordinate may be used as a bind until R9–R11 and the
thickness SILENT gate are closed. Pitch-only X for A1–A12 is a
**layout reconstruction**, not a D-050 bind.
