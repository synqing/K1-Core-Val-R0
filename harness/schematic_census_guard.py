#!/usr/bin/env python3
"""Compare two EasyEDA V3 schematic dumps. Exit 1 if the delta is not exactly allowed."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def parse(path: Path) -> dict:
    raw = json.loads(path.read_text())
    source = raw.get("source")
    if not isinstance(source, str):
        raise SystemExit(f"{path}: no source")
    comps: dict[str, dict] = {}
    des: dict[str, str] = {}
    nets: dict[str, list[str]] = defaultdict(list)
    nwire = 0
    nline = 0
    for line in source.splitlines():
        if "}||{" not in line:
            continue
        header_s, payload_s = line.split("}||{", 1)
        header = json.loads(header_s + "}")
        payload = json.loads("{" + payload_s.rstrip("|"))
        kind = header.get("type")
        hid = header.get("id")
        if kind == "COMPONENT":
            comps[hid] = {
                "x": payload.get("x"),
                "y": payload.get("y"),
                "part": payload.get("partId"),
            }
        elif kind == "ATTR":
            parent = payload.get("parentId") or payload.get("parent_id")
            key = payload.get("key")
            val = payload.get("value")
            if key == "Designator" and val:
                des[parent] = val
            elif key == "NET" and val:
                nets[parent].append(val)
        elif kind == "WIRE":
            nwire += 1
        elif kind == "LINE":
            nline += 1
    return {
        "hash": raw.get("sourceHash"),
        "comps": comps,
        "des": des,
        "nets": dict(nets),
        "nwire": nwire,
        "nline": nline,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("before", type=Path)
    ap.add_argument("after", type=Path)
    ap.add_argument("--allow-gone-id", action="append", default=[])
    ap.add_argument("--allow-gone-des", action="append", default=[])
    ap.add_argument("--allow-added-des", action="append", default=[])
    ap.add_argument("--forbid-new-ids", action="store_true", default=True)
    args = ap.parse_args()
    before = parse(args.before)
    after = parse(args.after)
    gone_ids = sorted(set(before["comps"]) - set(after["comps"]))
    new_ids = sorted(set(after["comps"]) - set(before["comps"]))
    gone_des = sorted(set(before["des"].values()) - set(after["des"].values()))
    added_des = sorted(set(after["des"].values()) - set(before["des"].values()))
    moved = []
    for cid, meta in before["comps"].items():
        if cid not in after["comps"]:
            continue
        nxt = after["comps"][cid]
        if (meta["x"], meta["y"]) != (nxt["x"], nxt["y"]):
            moved.append((before["des"].get(cid, cid), meta, nxt))
    print(f"before {before['hash']} n={len(before['comps'])}/{before['nwire']}/{before['nline']} des={len(before['des'])}")
    print(f"after  {after['hash']} n={len(after['comps'])}/{after['nwire']}/{after['nline']} des={len(after['des'])}")
    print("GONE_IDS", gone_ids)
    print("NEW_IDS", new_ids)
    print("GONE_DES", gone_des)
    print("ADDED_DES", added_des)
    print("MOVED", len(moved), moved[:12])
    errors = []
    unexpected_gone = [i for i in gone_ids if i not in args.allow_gone_id]
    if unexpected_gone:
        errors.append(f"unexpected gone ids: {unexpected_gone}")
    missing_allowed = [i for i in args.allow_gone_id if i not in gone_ids]
    if missing_allowed:
        errors.append(f"allowed gone id still present: {missing_allowed}")
    if new_ids:
        errors.append(f"new component ids: {new_ids}")
    unexpected_gone_des = [d for d in gone_des if d not in args.allow_gone_des]
    if unexpected_gone_des:
        errors.append(f"unexpected gone designators: {unexpected_gone_des}")
    unexpected_added = [d for d in added_des if d not in args.allow_added_des]
    if unexpected_added:
        errors.append(f"unexpected added designators: {unexpected_added}")
    if moved:
        errors.append(f"components moved: {len(moved)}")
    if before["nwire"] != after["nwire"]:
        errors.append(f"wire count {before['nwire']} -> {after['nwire']}")
    if errors:
        print("CENSUS_GUARD_FAIL")
        for err in errors:
            print(" ", err)
        return 1
    print("CENSUS_GUARD_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
