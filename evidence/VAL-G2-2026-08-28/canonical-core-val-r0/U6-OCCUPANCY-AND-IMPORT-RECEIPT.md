# Receipt — U6 occupancy vs single-unit import path

**Date:** 2026-08-29  
**Live read:** `jobs/u6-occupancy-live-2026-08-29.json`

## What is true on the live canvas

Both RT1062 symbol halves are on the one sheet. The occupancy report from
[U6 sheet occupancy](e494705d-7437-4d0b-9932-f2b6c098e34b) was right about
that, and wrong about 3D.

| Item | Live now |
|---|---|
| Schematic | `U6-RTC` = `e3295` `.1` at (2315, 4440) and `e3673` `.2` at (2250, 3930) |
| PCB | One footprint `U6-RTC` |
| 3D on U6-RTC | NXP donor STEP `de5664fd2ea74aa082831cfa5b198edb` — **already bound** |
| 3D on USB1 | Hirose `71aa35b92da84360b5d9e21f25c486f0` — still only on USB1 |
| Silicon | `MIMXRT1062DVJ6B` (D-028). Instance LCSC reads `C2847497`, not `C3216699` |

The occupancy claim “PCB has no model3D” came from the older
`pre-usbc-3d-sch.json` dump. It is stale.

## Import path — recorded, not executed

[Import single-unit into EasyEDA](e17f9073-ae1f-4ca1-9ed5-f8777d460f22) found
no library API for the SamacSys `.lbr`. Official LCSC is two-unit and has no
3D. `lib_Device.copy` failed. `symbolType` on create makes empty shells.

Already done: millimetre STEP in the personal library, then instance `modify`
on the PCB footprint.

Not done, and **not started from this receipt**:

1. Personal device that reuses the official two-unit symbol + LCSC LFBGA + STEP,
   keeping `MIMXRT1062DVJ6B` / `C3216699`. No `symbolType`. Leave the sheet alone.
2. GUI `File → Import → EAGLE` of the `.lbr` into the **personal** library only.
   Prove pin numbers are `A1`–`P14`, not `VSS_1`.
3. New personal device: that single-unit symbol + existing LCSC footprint + STEP.
   Discard any imported SamacSys footprint.
4. Gated sheet replace of `U6-RTC`. Delete both units, place one, restub pins.
   Mutation gate. Not a library import.

Pinout reuse is already closed:
`RT1061-VS-1062-PINOUT-RECEIPT.md` (`PINOUT_IDENTICAL`, no silicon swap).
