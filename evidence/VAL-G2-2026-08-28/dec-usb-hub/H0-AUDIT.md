# H0-AUDIT — STEP proof holds; G-Switch stays bound

```text
AUDIT            = PASS
WINNER           = GT-USB-7005A / C5250872
D050             = UNCHANGED (still BOUND on G-Switch)
CX90B2           = WRITTEN-LETTER CONTROL, NOT SELECTED
EASYEDA          = not mutated
```

The 1.60 mm mechanical bind in `H0-CLOSE.md` was re-parsed from the
manufacturer STEP, not copied from the close note. It still holds.
G-Switch is not unbound. D-050 is not rewritten onto CX90B2.

## Independent STEP reproduce

File `datasheets/_extract/GT-USB-7005A.stp`, SHA-256
`3e8f2300c222477a26adf1221f91e5e01220b0216d33b7826a362ff13ea3b8d5`
(matches `J1-GT-USB-7005A-pads.json`). 9 470 `CARTESIAN_POINT` records.

Rear-class isolation is the same as the close: Z ≤ −3.80 mm, |X| ≤ 3.20 mm
(841 points).

| Quantity | This audit | H0-CLOSE |
| --- | --- | --- |
| SMT solder-face cluster | **120 points at Y = 0.400000 mm**, X = −2.850…+2.850, Z = −4.76…−4.36 | 120 @ 0.400 |
| Second cluster at Y = 0.500 | 120 points — tail thickness, **not** the solder face | same |
| Shell / all-metal min Y | **−1.480 mm** | −1.480 |
| Sink below PCB top | 0.400 − (−1.480) = **1.880 mm** | 1.880 |
| On D-012 1.60 mm | **0.280 mm** under-cutout protrusion | 0.280 |
| TH tip reach below top | **1.100 mm** (does not emerge) | 1.100 |

`_h0_measure/STEP2.json` used a looser 0.25–0.55 mm Y bag and averaged
0.400 with 0.500 (mean ≈ 0.446, sink ≈ 1.926). That file is **not** the
bind. The bind is the exact 0.400 solder-face cluster.

This is **not** Sinker 1.9, CH 0.4, or the planar 1.60 mm land-pattern
spacing. The drawing thickness window stays **SILENT** (`GSWITCH-7005A-FAST-EXTRACT.md`,
YES rows for PCB thickness = 0). That hole is already recorded. It does
not reopen mechanical YES.

## Three bar-failure probes

**Wrong STEP parse — no.** The 120-point 0.400 cluster, shell min Y, sink
and 0.280 mm protrusion reproduce exactly.

**Pinch on 1.60 mm — no.** Tab metal (|X| ≥ 5.50 mm) occupies Y = −0.50…
+0.70 mm only: 0.90 mm below the top, 0.70 mm short of the 1.60 mm bottom
plane (Y = −1.20). Zero wide-X points sit on that plane. Lowest metal in
the whole solid is the **shell body** at Y = −1.480 (cutout sink), not a
bottom flange. Process class 前插后贴单壳 is consistent with that solid.
CX70M-class pinch remains the other part, and stays NO-GO.

**Missing tabs — no.** Four populated groups: left/right × front/rear,
centred near X = ±6.075 mm. Matches `SHELL.TAB1`–`TAB4` in
`J1-GT-USB-7005A-pads.json` / `.csv`. Staggered B-row unchanged.

## CX90B2 role

Hirose CX90B2-24P design guide §4.3 (page 11 of
`datasheets/D5d-Hirose-CX90B2-24P-design-guide.pdf`) still writes
**recommended PCB thickness 1.6±0.05 mm**. That is the strongest *written*
letter in the pack. The part is **on-board**, was evaluated as control,
and is **not selected**. A written letter on a different MPN does not
unseat a Captain-selected recessed part whose STEP section already clears
1.60 mm.

## Disposition

G-Switch **GT-USB-7005A / C5250872** remains the bound J1.
D-012 stays 1.60 mm / six layers. No EasyEDA write. No MPN swap.
