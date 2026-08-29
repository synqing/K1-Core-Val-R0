# GO / NO-GO — Phase H (GREEN, 2026-08-29, coordinator merge)

Every line is YES or NO with a pointer. No “mostly green”.
Family-only freeze hatch stays **deleted**. H RED would be the work queue;
this merge found remaining defects, repaired them, and re-scored.

Siblings merged: `H0-CLOSE.md`, `H0f-CLOSE.md`, plan H-state-machine
(work queue, not Phase Z), `EASYEDA-PREFLIGHT.md`.

```text
VERDICT = GREEN
COLOUR = GREEN
MEANING = RATIFY D-049, BIND D-050, ADVANCE I–L
DEC-USB-HUB = ADOPTED
D049_AFTER_H = RATIFIED
D049_RATIFIED = yes
D050_BOUND = GT-USB-7005A / C5250872
F6_VALIDITY_SOURCE = 5V0_USB_VALID
F6_VALIDITY_IC = TPS7A2550DRVR / C2876265
READY_FOR_EASYEDA = yes
I_L = IN_SCOPE
EASYEDA = authorised on disposable hub project 41c8e652… only
HUB_PROJECT = 41c8e6523576456582ea35958b3684ed
LIVE = 64325d0e55e0435abd018defb0089a9b  UNTOUCHED
```

GREEN because H0–H14 are YES after this merge. Phase Z is not taken.

Coordinator repairs this pass (were remaining RED, now closed):

- USB2422 DN1/DN2 pin map in `PIN-CONTRACT.md` G2 aligned to DS00001726B
  (DN1 = pins 4/3, DN2 = pins 5/2).
- XOR designators moved to R94/R95 so they do not steal H0f R85/R86.
- T14/T15 skipped; T16 is GPIO15 from `USB_5V_VALID` (H0f Clock 1).
- H0 STEP solder-face cluster independently reproduced (120 points at
  Y = 0.400 mm).

## H0–H14

| ID | Q | Y/N | Pointer |
| --- | --- | --- | --- |
| H0 | D-050 usable bind: named MPN **and** mechanical cleared **and** independently verified symbol/footprint **and** CC disposition | **YES** | `H0-CLOSE.md`. STEP sink 1.880 mm, 0.280 mm bottom keepout on 1.60 mm. Drawing SILENT on thickness window. |
| H0a | 24-pin + shell contract written; SS/SBU NC; cache not authority | **YES** | `CONNECTOR-COMPATIBILITY.md` D050-4; four tabs named |
| H0b | CX70M not bound on 1.60 mm; no agent 0.8 mm edit | **YES** | D-012 unedited; CX70M NO-GO |
| H0c | CC-PROTECTION letter closed | **YES** | `CC-PROTECTION.md` IEC ESD only for VAL |
| H0d | F9 / D050-6 budget, startup, OVLO vs 5.50 V, PD steelman | **YES** | `VBUS-CONTRACT.md` F9; closed by `5V0_USB_VALID` |
| H0e | F6-B-KILL letter KILL-A or KILL-B (not C) | **YES** | **KILL-B** (TLV7031 + dual AND) |
| H0f | `F6_VALIDITY_SOURCE` filled from envelope proof | **YES** | `H0f-CLOSE.md` `5V0_USB_VALID` = U22-USB TPS7A2550DRVR / C2876265. Not `5V_PROTECTED`. |
| H0g | Three F8 timing proofs written | **YES** | Clock 1 = 1.45 ms ≤ 3 ms; Clock 2 = 28 ms ≤ 100 ms; Clock 3 = 2.60 ms ≤ 10 ms (`H0f-CLOSE.md`) |
| H1 | D-049 `APPROVED_FOR_PHYSICS / PROVISIONAL` entering H; GREEN would RATIFY | **YES** enter / **YES** RATIFY | H GREEN. D-049 **RATIFIED**. |
| H2 | USB2422 + checklist + errata + NXP + Espressif + TPS2052B + UFP WP + Hirose/HYC/TI packs on disk with SHA256 | **YES** | Packs hashed; TPS7A25 on disk |
| H3 | 24-pin extract complete | **YES** | `USB2422-PIN-EXTRACT.md` |
| H4 | Census KEEP/DELETE/RETARGET no blanks on J1/J7/OTG1/S3-USB/CC | **YES** | `CENSUS.md` |
| H5 | F2 and F6 letters; F6-B ⇒ F2-C + F6-B1 + KILL | **YES** | F2-C, F6-B, KILL-B. IN = `5V0_USB_VALID` |
| H6 | S3 4.75 / 4.35 / 3 ms and VIH, or comparator specified | **YES** | Comparator TLV7031; GPIO15 from `USB_5V_VALID` |
| H7 | Hub `VBUS_DET` from `5V_USB` | **YES** | F1 / G2 pin 16 |
| H8 | F6-B pin map; not NON_REM; outputs do not power MCUs | **YES** | G4b / G4c / G4d |
| H8a | F8 discharge ≤ locked VBUS_DET VIL time | **YES** | R80 4.7 kΩ, C_raw ≤ 1.2 µF → 5τ ≈ 28 ms ≤ 100 ms |
| H8b | NXP 25/50 mA row copied from IEC PDF | **YES** | `NXP-USB-OTG1-VBUS-EXTRACT.md` |
| H8c | Anomaly 3 hold; USB audio EXPERIMENT_ONLY | **YES** | `ERRATA-HOLD.md` |
| H9 | J6 brick path | **YES** | census; debug-fabric |
| H10 | XOR true XOR / DNP default | **YES** | G6 R94 FIT / R95 DNP |
| H11 | C622610 In Production / buyable | **YES** | `PROCUREMENT.md` |
| H12 | J1 upstream VBUS cap ≤ 10 µF | **YES** | C1 contracted 1.0 µF on `5V_USB`. C2/C120 behind eFuse. |
| H13 | Authority checker PASS | **YES** | re-run after this merge |
| H14 | PIN-CONTRACT names every hub pin and every TPS2052B pin | **YES** | `PIN-CONTRACT.md` G2 (DS pin numbers) / G4b / G4c / G4d |

## H15–H17 (GREEN path)

- H15. `DEC-USB-HUB = ADOPTED`. Failing IDs: none.
- H16. Phase I already created `41c8e652…`. Continue T00–T24 on that UUID only.
- H17. Do **not** freeze the dual-USB graph. Living D-049 is **RATIFIED**. D-050 is **BOUND**.
