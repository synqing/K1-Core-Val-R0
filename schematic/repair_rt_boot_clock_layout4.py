#!/usr/bin/env python3
"""Final reset-layout repair with the switch immediately beside U7."""
from __future__ import annotations

import sys

import repair_rt_boot_clock_layout3 as repair


repair.REJECTED = "canonical-rt-boot-clock-layout-repair3-2026-08-28"
repair.TX = "canonical-rt-boot-clock-layout-repair4-2026-08-28"
repair.SWITCH_TARGET = [3040, 4285]
repair.SWITCH_REQUEST_PIN = "2"
repair.SWITCH_GROUND_PIN = "1"
repair.NET_ATTR_VISIBLE = 0
repair.INTENDED = (
    "Place SW1 immediately beside U7 and replace the oversized recovery loop with one short "
    "horizontal RT_RESET_REQ_N connection; retain a compact GND stub on the other switch contact"
)


def short_horizontal_wire(
    u7_point: tuple[int, int], switch_point: tuple[int, int]
) -> list[list[int]]:
    return [[switch_point[0], switch_point[1], u7_point[0], u7_point[1]]]


repair.build_local_wire = short_horizontal_wire


if __name__ == "__main__":
    sys.exit(repair.main())
