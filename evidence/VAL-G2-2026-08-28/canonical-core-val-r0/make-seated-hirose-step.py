#!/usr/bin/env python3
"""Write a distinct Hirose STEP for a new personal-library UUID.

The documented EasyEDA 3D matrix recentres XY and pins lowest Z to the board,
then applies OFFSET. A raw origin rewrite is invariant under that ORIGIN step.
This file is a new product identity so the 3D builder cannot reuse the dead
71aa35… cache. Geometry is unchanged; the bind will carry USB2-style OFFSET.
"""
from __future__ import annotations

from pathlib import Path

SRC = Path("/Users/spectrasynq/Downloads/User Library-USB_C_Hirose_CX_4800304000_v3.STEP")
DST = Path("evidence/VAL-G2-2026-08-28/canonical-core-val-r0/USB_C_Hirose_CX_4800304000_seated.STEP")

text = SRC.read_text(errors="replace")
text = text.replace(
    "User Library-USB_C_Hirose_CX_4800304000_v3",
    "USB_C_Hirose_CX_4800304000_seated",
)
text = text.replace(
    "FILE_NAME ('USB_C_Hirose_CX_4800304000_seated.STEP'",
    "FILE_NAME ('USB_C_Hirose_CX_4800304000_seated.STEP'",
)
if "USB_C_Hirose_CX_4800304000_seated" not in text:
    raise SystemExit("rename did not land")
DST.write_text(text)
print(f"wrote {DST} bytes={DST.stat().st_size}")
