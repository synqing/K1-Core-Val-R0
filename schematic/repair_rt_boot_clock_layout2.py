#!/usr/bin/env python3
"""Second bounded box-4 repair: isolate manual reset and restore right clearance."""
from __future__ import annotations

import argparse
import sys

import repair_rt_boot_clock_layout as repair


repair.REJECTED = "canonical-rt-boot-clock-layout-repair-2026-08-28"
repair.TX = "canonical-rt-boot-clock-layout-repair2-2026-08-28"
repair.MOVES = {
    "U7-RTC": (3150, 4310),
    "C18-RTC": (3340, 4310),
    "R12-RTC": (3490, 4310),
    "R10-RTC": (3690, 4310),
    "R11-RTC": (3850, 4310),
    "SW1-RTC": (3150, 4050),
}
repair.NOTE_TARGET = [3600, 4110]
repair.INTENDED = (
    "Move the manual reset switch onto its own row, shift U7 right for request-net clearance, "
    "and pull R11 inward so every box-4 label remains fully visible"
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-normalized-live-state", action="store_true")
    args = parser.parse_args()
    sys.exit(
        repair.record_normalized_live_state()
        if args.record_normalized_live_state
        else repair.main()
    )
