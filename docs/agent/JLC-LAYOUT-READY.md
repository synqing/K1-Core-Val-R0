# JLC-LAYOUT-READY — later programme

`JLC-SCH-READY` is not this gate.

```text
JLC_LAYOUT_READY = BLOCKED_BY_JLC_SCH_READY
```

This stamp unblocks **paid JLCPCB placement and routing**. Do not stamp it from
an archived G2.2/HOLD reconstruction. `JLC-SCH-READY` attaches to GREENFIELD
(D-052).

Required, after `JLC-SCH-READY` PASS:

1. Final layout-relevant RT1062 / S3 IOMUX — no layout-critical `IOMUX_TBD`
   (RQ-014 / 015 / 025 / 038 / 045 remain `PARTIAL_G3`).
2. Verified PCB footprints for every fitted part, including custom `U17-PWR2`
   and `DVBUS-PWR1`.
3. TPS2561 RILIM re-derivation (59 kΩ is nominal only).
4. RF matching / SI `TUNE_TBD` numbers that affect pad or keepout geometry.
5. Final DXF / fixed mechanics.
6. Exact pad count.
7. The required JLC source package.

VAL-G3 owns IOMUX, footprints and mechanics. CopperPilot may propose geometry
and must not write the canonical board or certify this gate.

Later mechanics assume **one** Type-C (D-049 `RATIFIED`) and a J1 MPN from D-050,
not two receptacles. This file does not stamp either gate.
