# Single-sheet qualification — test plan

Status: **VAL-G2.0 — REQUIRED FIRST, NOT RUN**

Purpose: prove that EasyEDA Pro can carry the complete K1-CORE-VAL board on one schematic sheet
before canonical one-sheet capture creates irreversible implementation reliance.

EasyEDA Pro documents no schematic area limit, but separately recommends fewer than 100
components per page and warns of editor lag beyond that. Those statements are not contradictory:
no hard limit, and a practical performance warning. K1-CORE-VAL will exceed 100 components, so
the test is mandatory.

## Fixture

Disposable project, named so it cannot be confused with the real design:

    K1-CORE-VAL-SINGLE-SHEET-QUAL

Exactly one large schematic page. **Size the fixture to Option C**, the worst case, because it
places both RT1062 and ESP32_S3, their support circuitry and the carrier peripherals on one board:

    N_test = max(200, ceil(1.20 x N_estimated_symbols_option_C))

Use representative symbol and wiring complexity. Not 200 identical resistors.

Minimum content:

- 200 representative electrical symbols
- 120 named nets
- 10 or more high-fanout power and control nets
- one visibly wired power tree
- at least one representative domain group of 20 or more symbols

Mock but electrically coherent domains for: RT1062 and support; ESP32_S3 and support; the bridge
interface; power entry and protection; buck and rails; LED power and data; audio, TDM and PDM;
USB; NFC; accelerometer; connectors; option links.

## Objective responsiveness gate

Measure with screen recording or monotonic timestamps. Not prose impressions. Run each operation
five times. A failure is recorded with its measured duration and operation. Do not average away
a repeatable stall.

| Operation | Pass condition |
| --- | --- |
| Move a domain of 20+ symbols with attached wires | Editor accepts the next selection or edit within 2.0 s of mouse release, on every run |
| Add, move or delete a connected wire segment | Editor accepts the next selection or edit within 2.0 s, on every run |
| Pan and zoom continuously for 30 s | No individual UI freeze longer than 1.0 s |
| Annotate the full sheet | Completes within 60 s, no missing or duplicate designators |
| Run ERC | Completes within 60 s, no editor lock-up |
| Save, close, reopen | Reopens with exact symbol and net inventory |
| Update or import to a disposable PCB | Completes with exact schematic component and net counts |

## Integrity gate

- No components or nets disappear.
- Save and reopen is stable and repeatable.
- ERC completes.
- PCB import inventory matches the schematic exactly.
- No repeatable corruption.

## On failure

Failing this test does **not** authorise hierarchical sheets. Stop, report the measured failure,
and optimise the one-sheet implementation: symbol density, decorative content, wiring layout,
net-trunk use, tables and canvas organisation.

## Boundary

This test creates a disposable qualification project only. It does not create the final K1
EasyEDA project, schematic, PCB or any manufacturing artefact.
