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

- **U1-PWR1.9 (eFuse ILM) is bound to USB_DP_UP** while R1-PWR1 dangles on
  USB_EFUSE_ILIM — an eFuse current-limit node on the USB HS pair. VERIFY before anything.
- U23/U25 supply pins deviate from H0f (V+/GND swapped; PRTPWR2 path grounded).
- Same-net series elements the router could bypass: R85, R94, R90, C123.
- J1 GT-USB-7005A placed 0/28 wired; USB4105 parked -RETIRED still on legacy nets.
- Hub support (Y3, RBIAS, CRFILT, PLLFILT, VDD33 pin1) unwired; NON_REM straps orphaned.
- Dangling-by-pinmux (D-031, expected): RT_I2C_*, PWR_ENTRY_PG, MOTION_INT_S3, CC ADC taps.

Reconciliation PASSED (0 mechanical fails) — the ALL sheet was generated from the same
inventory, so a port cannot exist on one sheet and not its counterpart.
