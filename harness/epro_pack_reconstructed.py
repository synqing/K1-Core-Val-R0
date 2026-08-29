#!/usr/bin/env python3
"""Copy a G2.1 .epro and replace only the schematic page with reconstructed V3 source.

Refuses if the PCB member is not electrically empty. Does not touch the live
canonical project.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import zipfile
from collections import Counter
from pathlib import Path


def pcb_is_empty(payload: bytes) -> bool:
    counts = Counter()
    text = payload.decode("utf-8", "replace")
    if not text.strip() or text.strip() in {"", "{}"}:
        return True
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("["):
            try:
                import json

                rec = json.loads(line)
            except ValueError:
                continue
            if isinstance(rec, list) and rec:
                counts[str(rec[0])] += 1
        elif '"type"' in line:
            if '"COMPONENT"' in line:
                counts["COMPONENT"] += 1
            if '"VIA"' in line:
                counts["VIA"] += 1
    electrical = sum(counts[k] for k in ("COMPONENT", "VIA", "WIRE", "NET") if k in counts)
    return electrical == 0


def pack(src_epro: Path, esch: Path, dest: Path) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_epro, dest)
    source = esch.read_text(encoding="utf-8")
    with zipfile.ZipFile(src_epro) as zin:
        names = zin.namelist()
        esch_name = next(n for n in names if n.endswith(".esch"))
        pcb_names = [n for n in names if n.endswith(".epcb")]
        for pcb_name in pcb_names:
            if not pcb_is_empty(zin.read(pcb_name)):
                dest.unlink(missing_ok=True)
                raise SystemExit(f"epro_pack_reconstructed: {pcb_name} is not electrically empty")
        file_bytes = {name: zin.read(name) for name in names}
    file_bytes[esch_name] = source.encode("utf-8")
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name in names:
            zout.writestr(name, file_bytes[name])
    digest = hashlib.sha256(dest.read_bytes()).hexdigest()
    return {
        "output": str(dest),
        "replaced": esch_name,
        "sha256": digest,
        "esch_chars": len(source),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("epro", type=Path)
    parser.add_argument("--esch", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args(argv)
    report = pack(args.epro, args.esch, args.output)
    print(
        "EPRO_PACK=OK "
        f"replaced={report['replaced']} "
        f"sha256={report['sha256'][:16]} "
        f"esch_chars={report['esch_chars']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
