# Receipt — MIMXRT1061DVJ6B vs frozen MIMXRT1062DVJ6B pinout

**Date:** 2026-08-29  
**Verdict:** `PINOUT_IDENTICAL`  
**Silicon swap:** forbidden. D-028 stays `MIMXRT1062DVJ6B` / LCSC `C3216699`.

The 196 balls are electrically the same. The 1061 SamacSys pack is a donor for
**symbol geometry and STEP only**. It is not a part-number change.

## What this unlocks

- Reuse the 1061 single-unit symbol outline and the imported STEP
  (`de5664fd2ea74aa082831cfa5b198edb`) on the frozen 1062 device identity.
- Keep Manufacturer Part = `MIMXRT1062DVJ6B` and Supplier Part = `C3216699`.

## What this does not unlock

- Do not order, document, or BOM `MIMXRT1061DVJ6B`. 1061 lacks LCD / CSI / PXP IP.
- Do not replace live `U6-RTC` units on the canonical sheet from this receipt.
  Sheet replace is a later gated job (mutation gate, screenshots, pin restub).
- Do not import the SamacSys footprint. Keep LCSC
  `LFBGA-196_L12.0-W12.0-R14-C14-P0.80-BL`.

## Numbers

| Check | Result |
|---|---|
| Shared ball IDs | 196 |
| Balls only on 1061 / only on 1062 | 0 / 0 |
| Functional name mismatches | 0 |
| Cosmetic KiCad power-pin suffixes (`VSS_1` …) | 39 |
| Critical audit balls vs PIN-AUDIT-RT | 48/48 |
| Package | 12×12 mm, 0.8 mm, 14×14, 196 MAPBGA / LFBGA |

Shared wart already on the live 1062 symbol: ball K4 `DCDC__IN_Q` vs NXP `DCDC_IN_Q`.

## Sources

- NXP IMXRT1060CEC Rev. 4, Table 1 + §6.2.2 Tables 85–87 (family-wide 12×12 map)
- SamacSys `MIMXRT1061DVJ6B.kicad_sym` (196 pins, one unit)
- Live harvest `jobs/read-rt1062-all-pins.results.json` (e3295 + e3673 = 196)
- PIN-AUDIT-RT Rev. 2 ball-map PASS
- SSA [1061 vs 1062 pin compare](1fe4b73f-e31e-444d-939e-d11c2be93287)
