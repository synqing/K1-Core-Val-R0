# ADR-050: J1 USB-C receptacle (bound)

**Status:** RATIFIED / BOUND
**Date:** 2026-08-29
**Deciders:** Captain selected the MPN; H GREEN bound it
**Register:** D-050 = `RATIFIED / BOUND`

This ADR binds J1. It does **not** supersede D-012. Board thickness stays
1.60 mm / six layers unless Captain opens a D-012 amendment.

## Context

D-049 needs one Type-C sink at `J1-PWR1`. The earlier preference was Hirose
`CX70M-24P1`: strong electrical evidence, recessed mid-mount, USB-IF TID
5,200,000,077 — and a manufacturer recommended PCB thickness of **0.8 mm max**.
That part is **NO-GO on the current 1.60 mm board**. Thinning the whole board
to fit it reopens impedance, RT1062 BGA escape, high-current copper, stiffness,
enclosure datums and warpage. Local stepped tongues are unauthorised without
written JLC DFM.

Handoff (copied at Phase A, SHA-256
`c3b6a533e9eecaaaeaf465c0368dc070b176b7cc3724a1445dee393f18c32703`) is evidence
of that collision. It is not a ratified MPN. Live EasyEDA `C778726` / CX70M 3D
experiments on `64325d0e` are not this decision.

Captain then selected G-Switch **GT-USB-7005A / C5250872**. An earlier same-day
pick, TE `2129691-1` / `C590834`, is archived fallback. Selecting G-Switch does
not waive the drawing gate: “laminated board”, “Board Sink 1.9” and centre
height 0.4 mm are recess/offset language, not a thickness proof — the same
class of error as HYC `沉板1.4`.

The bind is **not** a drawing thickness sentence. The drawing is still SILENT
on a recommended PCB-thickness window. The bind is geometric section analysis
plus manufacturer process class. See `CONNECTOR-COMPATIBILITY.md` D050-0c.

## Decision

**Bound MPN:** G-Switch `GT-USB-7005A` / LCSC `C5250872`.

D-050 governs J1 **and** any request to change D-012 thickness to fit a
connector. No agent may set board thickness to 0.8 mm. CX-PATH-A is a read-only
feasibility study unless Captain opens a D-012 amendment.

### Bind evidence (cleared)

- Drawing recommended PCB thickness: **SILENT** (not used as the bind).
- Process class: 前插后贴单壳 (front TH, rear SMT, single shell). Not a
  CX70M-class thickness clamp.
- STEP SMT datum: PCB top at Y = 0.400 mm; shell min Y = −1.480 mm; sink
  1.880 mm; on D-012 1.60 mm, **0.280 mm bottom keepout**.
- Sink-cutout + hybrid DFM: JLC High-difficulty / Extended process hold
  written, not silently ignored.
- Shell / shield-tab contract: four tabs to signal GND + stitching.
- Independently rebuilt symbol/footprint lock:
  `J1-GT-USB-7005A-FOOTPRINT-REBUILD.md`. EasyEDA / LCSC `C5250872` artwork
  is a cache, not authority.
- CC-PROTECTION letter: IEC ESD only for VAL-R0.

### Retired shortlist (evidence, not stealth revert)

| Part | Role |
| --- | --- |
| Hirose `CX70M-24P1` / `C778726` | Earlier preference. **NO-GO on 1.60 mm**. NRND. Archive only. |
| TE `2129691-1` / `C590834` | Previous Captain pick. **Archived fallback.** Do not silently revert. |
| HYC `HYCW78-USBC24-140B` / `C3034184` | Recessed 1.60 mm fallback if G-Switch sink/DFM fails. Not selected. |
| Hirose `CX90B2-24P` | On-board Hirose control (design guide §4.3 recommends 1.6±0.05 mm). Not selected. |

### 24-pin plus shell (winner)

```text
A4/A9/B4/B9     → 5V_USB
A1/A12/B1/B12   → GND
SHELL / shield  → named GND or chassis strategy + stitching
A6+B6 / A7+B7   → low-C ESD → hub US
A5 / B5         → Rd + sense + CC-PROTECTION
SBU, SuperSpeed → NC
```

USB2422 is USB 2.0. SuperSpeed routing is forbidden. A 5 A receptacle rating
does not grant 5 A from a non-PD Type-C source.

## Named holds

- Drawing remains SILENT on recommended PCB thickness. Bind is D050-0c.
- JLC Assembly Difficulty High remains a process hold (not a thickness reject).
- Bottom copper/parts/enclosure must clear **0.30 mm** under the shell.
- EasyEDA cache must not be imported as the part.
- D-012 unchanged. `pcb/STACKUP-STATUS.md` is not edited by this programme.

## Consequences

- D-049 may name the bound MPN.
- Hub-graph official freeze proceeds after EasyEDA ERC (Phase K).
- CX70M on 1.60 mm remains NO-GO even if someone prefers the shape.

## Action items

1. [x] Phase C: Captain implement-the-plan acknowledges D-050 registered OPEN on GT-USB-7005A /
   C5250872. This is not a bind.
2. [x] Phase D / D050: G-Switch drawing on disk. Thickness window SILENT.
   Geometric section + process class + STEP datum bind.
3. [x] H GREEN 2026-08-29: D-050 `RATIFIED / BOUND`.
