# Live-sheet damage inspect — 2026-08-28

Identity: `K1-Core-Val-R0` / `64325d0e…` page `1435cb46…`.  
Live dump: `live-source-2026-08-28-2226.json` hash `2244327:b5d507ab`.  
Baseline: `live-source-2026-08-28-2200.json` hash `2142088:6a266bf3`.  
No writes in this inspect.

## Captain-facing fact

`C62-MOT1` is a spare 100 nF with no nets. The original `C62-MOT` is still on the sheet and still on `3V3` / `GND`.

## Motion-row damage

| Ref | Id | Now | Nets on pins (wire-end match) |
|---|---|---|---|
| C62-MOT | e13842 | still present; dragged 2080,-2525 → 2430,-3095 | 3V3 / GND |
| C62-MOT1 | 1c431593519b8c88 | **new** at 2290,-3000 | **none** |
| C63-MOT | e13878 | present; dragged | 3V3 / GND |
| R44-MOT | e13914 | **gone** after dump 2203 | was I2C_SDA / MOTION_SDA |
| R44-MOT1 | 4baf65b7a960e4f0 | **new**; now on those SDA nets | MOTION_SDA / I2C_SDA |
| R45-MOT | e13953 | **gone** after dump 2220 | was DNP 10k |
| R45-MOT1 | 4bf3295db021c743 | **new**; on SDA pair | MOTION_SDA / I2C_SDA |
| U13-MOT | e14187 | present | SCL, SDA, GND, 3V3, INT1 still landed; CS / SA0 / RES / extra GND still open |

MOT1 trio first appears in dump `2203`, the same window as the U4 / R8 / C68 LED-eFuse delete. They are hex-id creates, not copies of the original `e*` ids.

## Designator delta 2200 → 2226

Gone: `U4-PWR2`, `R8-PWR2`, `C68-PWR2`, `R44-MOT`, `R45-MOT`, `F1-PWR1`, `L3-NFC`, `R43-NFC`, `R50-MOT`.  
Added: `C62-MOT1`, `R44-MOT1`, `R45-MOT1`, `U17-PWR2`, `RILIM-LED`, `RLED_ENL_PD-LED`, `RLED_ENR_PD-LED`.

## Other live defects left by this session's intended writes

- Four leftover `5V_USB_FILTERED` net attrs after F1 was removed; inlet not collapsed onto `5V_USB`.
- Orphan `LED_EFUSE_ILIM` / `LED_EFUSE_DVDT` stubs after U4 removal.
- `5V_LED_COMMON` and old `+5V_LED_L/R` labels still present.

## Pre-existing, not this session

- Undesignated ghost `6da43ee181cf13a9` at 0,0 (`pid8a0e77bacb214e`) already in dump 2200.

## Screenshot note

`damage-c62-mot1-cluster.png` Fit-Selection missed the motion cluster and showed the RTC cap row instead. Semantic pin/wire match is the evidence for C62-MOT1.
