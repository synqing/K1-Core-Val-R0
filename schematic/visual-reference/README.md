# K1-CORE-VAL-R0 — Visual Schematic Reference Package

```text
STATUS   = STUDY_INPUT / BINDING=NO
ROLE     = visual construction reference. NOT an EasyEDA schematic. Nothing here can be
           imported into EasyEDA; no pseudo-EasyEDA JSON exists; no PCB placement
           coordinate was generated. The Captain is the sole EasyEDA schematic author.
DATE     = 2026-08-29
```

## Contents

| File set | What it is |
|---|---|
| `D01..D10-BUILD.svg/.png` | ten domain reference sheets — construction view |
| `D01..D10-AUDIT.svg/.png` | same geometry + provenance overlays, VERIFY marks, numbered callouts |
| `ALL-BUILD / ALL-AUDIT` | Phase B: all-domains component-level sheet (287 designators, one sheet) |
| `REGISTERS.md` | reconciliation returns: counts, inventory, port register, rails, orphans, TBD, USB deltas |
| `reconciliation.json` | machine registers + PASS verdict that gated Phase B |
| `inventory.json` | the canonical pin→net inventory every sheet was generated from |

## Truth layering (read this before trusting any line)

1. **Capture truth** — nets parsed from `G2.2-HOLD-REOPEN.source.txt` (hub-era, freshest
   machine-readable). Pin→net binding oracle-proven (55/60 U6 agreement; the 5
   disagreements are hub-era renames + the M8 hub rewire, i.e. confirmations).
2. **Contract truth** — where the capture is unwired or deviant, sheets draw the
   PIN-CONTRACT / H0f-CLOSE wiring in red-dash TBD with status chips. Nothing deviant was
   silently "fixed"; every delta is a numbered AUDIT callout.
3. **Provenance** — ball geometry MEASURED · ball function symbol-derived (repair history,
   NXP cross-check pending) · peripheral assignment NOT pinmux-frozen (D-031).

## Headline findings (from the AUDIT views)

These AUDIT views were generated from the **pre-repair** G2.2 HOLD-REOPEN dump.
They are not a live netlist of either EasyEDA project.

- **CANONICAL `64325d0e…`:** U1-PWR1.9 / ILM is on `USB_EFUSE_ILIM`. **CLEAN — do not fix.**
- **G2.2 hub candidate:** **HAD** U1-PWR1.9 bound to `USB_DP_UP` while R1-PWR1 sat on
  `USB_EFUSE_ILIM` (this package's dump). Live HOLD `55ed9ee9…` was **repaired**
  2026-08-30 (`g22-pwr1-ilm-repair-2026-08-30`). Do not treat this visual package as
  current ILM topology, and do not copy that pre-repair geometry onto canonical.
- **R1-PWR1 trap:** electrical/device identity is **1.24 kΩ** /
  `RNCF0402BTC1K24` / `C2491273`. Stale `partId` `RC0402FR-0710KL.1` implies 10 kΩ
  and is display/legacy metadata only.
- U23/U25 supply pins deviate from H0f (V+/GND swapped; PRTPWR2 path grounded).
- Same-net series elements the router could bypass: R85, R94, R90, C123.
- J1 GT-USB-7005A placed 0/28 wired; USB4105 parked -RETIRED still on legacy nets.
- Hub support (Y3, RBIAS, CRFILT, PLLFILT, VDD33 pin1) unwired; NON_REM straps orphaned.
- Dangling-by-pinmux (D-031, expected): RT_I2C_*, PWR_ENTRY_PG, MOTION_INT_S3, CC ADC taps.

Reconciliation PASSED (0 mechanical fails) — the ALL sheet was generated from the same
inventory, so a port cannot exist on one sheet and not its counterpart.
