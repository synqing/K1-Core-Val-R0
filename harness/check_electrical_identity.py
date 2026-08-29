#!/usr/bin/env python3
"""Alias for check_electrical_equivalence — G2.2 identity invariant."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_electrical_equivalence import main

if __name__ == "__main__":
    raise SystemExit(main())
