#!/usr/bin/env python3
"""Hashed CLI auditor for the G2.1 offline bulk-repair candidate.

Does not mutate independent_epro_audit.py (90f109c3…). Accepts --input/--output/--report.
Adds the orphan-net invariant that the first /mnt/data auditor missed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

PCB_SHA = "8d14a5fd7a56ec4a689c7bd183c73acd4dc01d0248617999f5351fc39a903184"
LEFTOVER_SUPPORT = {"C11-PWR2", "C68-PWR2", "R8-PWR2", "R67-PWR1"}
NAMED_HOLD_NETS = {
    "RT_USB_AUD_STRAP_IOMUX_TBD",
    "PWR_ENTRY_PG_RT_IOMUX_TBD",
    "LED_FAULT_L_N",
    "LED_FAULT_R_N",
    "MOTION_INT_S3",
    "RT_I2C_SCL",
    "RT_I2C_SDA",
    "S3_I2C_SCL",
    "S3_I2C_SDA",
}


def h(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_nd(z, n):
    return [json.loads(x) for x in z.read(n).decode().splitlines() if x.strip()]


def trans(x, y, cx, cy, rot, mirror):
    if mirror:
        x = -x
    a = math.radians(rot % 360)
    ca = round(math.cos(a), 12)
    sa = round(math.sin(a), 12)
    return round(cx + x * ca - y * sa, 6), round(cy + x * sa + y * ca, 6)


def onseg(px, py, x1, y1, x2, y2, tol=1e-6):
    return (
        abs((px - x1) * (y2 - y1) - (py - y1) * (x2 - x1)) <= tol
        and min(x1, x2) - tol <= px <= max(x1, x2) + tol
        and min(y1, y2) - tol <= py <= max(y1, y2) + tol
    )


def build(z):
    names = z.namelist()
    esch = next(n for n in names if n.endswith(".esch"))
    recs = load_nd(z, esch)
    proj = json.loads(z.read("project.json"))
    comps = {r[1]: {"record": r, "attrs": defaultdict(list)} for r in recs if r[0] == "COMPONENT"}
    wires = {r[1]: r for r in recs if r[0] == "WIRE"}
    for r in recs:
        if r[0] == "ATTR" and r[2] in comps:
            comps[r[2]]["attrs"][r[3]].append(r)
    bydes = defaultdict(list)
    for cid, c in comps.items():
        for a in c["attrs"].get("Designator", []):
            bydes[a[4]].append(cid)
    wattrs = defaultdict(list)
    for r in recs:
        if r[0] == "ATTR" and r[2] in wires and r[3] == "NET":
            wattrs[r[2]].append(r)
    seg = []
    for wid, r in wires.items():
        for s in r[2]:
            if len(s) >= 4:
                seg.append((wid, *map(float, s[:4])))
    symcache = {}

    def syms(sid):
        if sid not in symcache:
            symcache[sid] = load_nd(z, f"SYMBOL/{sid}.esym")
        return symcache[sid]

    def partpins(sid, pname):
        part = None
        pins = {}
        for r in syms(sid):
            if r[0] == "PART":
                part = r[1]
            elif r[0] == "PIN" and part == pname:
                pins[r[1]] = {"x": r[4], "y": r[5], "num": None, "name": None}
            elif r[0] == "ATTR" and r[2] in pins:
                if r[3] == "NUMBER":
                    pins[r[2]]["num"] = str(r[4])
                elif r[3] == "NAME":
                    pins[r[2]]["name"] = r[4]
        return pins

    pins = defaultdict(list)
    for des, cids in bydes.items():
        for cid in cids:
            c = comps[cid]
            did = (c["attrs"].get("Device") or [None])[0]
            if not did:
                continue
            sid = (
                c["attrs"].get("Symbol")
                or [
                    [
                        None,
                        None,
                        None,
                        None,
                        proj["devices"].get(did[4], {}).get("attributes", {}).get("Symbol"),
                    ]
                ]
            )[0][4]
            if not sid:
                continue
            for lp, p in partpins(sid, c["record"][2]).items():
                if p["num"] is None:
                    continue
                x, y = trans(p["x"], p["y"], c["record"][3], c["record"][4], c["record"][5], c["record"][6])
                pins[(des, p["num"])].append(
                    {
                        "x": x,
                        "y": y,
                        "part": c["record"][2],
                        "page": cid + lp,
                        "name": p["name"],
                    }
                )

    def pn(des, num, part=None):
        vals = []
        for p in pins.get((des, str(num)), []):
            if part and p["part"] != part:
                continue
            ns = set()
            for wid, x1, y1, x2, y2 in seg:
                if onseg(p["x"], p["y"], x1, y1, x2, y2):
                    ns.update(a[4] for a in wattrs.get(wid, []))
            vals.append(sorted(ns))
        return vals

    membership = defaultdict(set)
    pin_nets = defaultdict(set)
    for (des, num), plist in pins.items():
        for p in plist:
            ns = set()
            for wid, x1, y1, x2, y2 in seg:
                if onseg(p["x"], p["y"], x1, y1, x2, y2):
                    ns.update(a[4] for a in wattrs.get(wid, []))
            key = f"{des}|{p['part']}|{num}"
            pin_nets[key].update(ns)
            for net in ns:
                if net:
                    membership[net].add(key)
    return {
        "names": names,
        "recs": recs,
        "proj": proj,
        "comps": comps,
        "bydes": bydes,
        "syms": syms,
        "pn": pn,
        "membership": {k: set(v) for k, v in membership.items()},
        "pin_nets": {k: set(v) for k, v in pin_nets.items()},
        "z": z,
    }


def vals(model, des, k):
    out = []
    for cid in model["bydes"].get(des, []):
        out += [r[4] for r in model["comps"][cid]["attrs"].get(k, [])]
    return out


def orphan_invariant(mi, mo, errors, warnings):
    findings = []
    all_nets = set(mi["membership"]) | set(mo["membership"])
    for net in sorted(all_nets):
        before = mi["membership"].get(net, set())
        after = mo["membership"].get(net, set())
        if after == before:
            continue
        members = sorted(after)
        if not members:
            # Retired or renamed away: zero pin endpoints is not an orphan.
            continue
        if len(members) >= 2:
            continue
        leftover = [m for m in members if m.split("|", 1)[0] in LEFTOVER_SUPPORT]
        iomux = net.endswith("_IOMUX_TBD") or net in NAMED_HOLD_NETS
        stranded = []
        if iomux and members:
            for pin in members:
                for old_net in mi["pin_nets"].get(pin, ()):
                    for other in mi["membership"].get(old_net, set()) - set(members):
                        des = other.split("|", 1)[0]
                        # Only support/pull-up remnants count as stranded companions.
                        # An intentional pin move (USB DN, DNP IRQ alt) is not an orphan.
                        if des in LEFTOVER_SUPPORT and des in mo["bydes"] and other not in after:
                            stranded.append(other)
        if leftover:
            msg = f"orphan leftover-support net {net} members={members}"
            errors.append(msg)
            findings.append({"net": net, "ok": False, "reason": "leftover_support", "members": members})
            continue
        if stranded:
            msg = f"orphan IOMUX net {net} stranded companions {sorted(set(stranded))} members={members}"
            errors.append(msg)
            findings.append(
                {
                    "net": net,
                    "ok": False,
                    "reason": "stranded_companion",
                    "members": members,
                    "stranded": sorted(set(stranded)),
                }
            )
            continue
        if len(members) < 2 and not iomux:
            msg = f"orphan changed/new net {net} has {len(members)} endpoint(s): {members}"
            errors.append(msg)
            findings.append({"net": net, "ok": False, "reason": "lt2_endpoints", "members": members})
            continue
        findings.append({"net": net, "ok": True, "reason": "named_hold", "members": members})
    return findings


def audit(input_path: Path, output_path: Path, report_path: Path) -> dict:
    zi = zipfile.ZipFile(input_path)
    zo = zipfile.ZipFile(output_path)
    mi = build(zi)
    mo = build(zo)
    errors = []
    warnings = []
    no = mo["names"]
    ni = mi["names"]
    for n in no:
        if n.endswith((".esch", ".esym", ".efoo", ".epcb")):
            try:
                load_nd(zo, n)
            except Exception as e:
                errors.append(f"parse:{n}:{e}")
        elif n == "project.json":
            try:
                json.loads(zo.read(n))
            except Exception as e:
                errors.append(f"parse project:{e}")
    ids = [r[1] for r in mo["recs"] if isinstance(r, list) and len(r) > 1 and isinstance(r[1], str)]
    dups = [x for x, c in Counter(ids).items() if c > 1]
    if dups:
        errors.append("duplicate primitive ids " + repr(dups[:20]))
    missing_parts = []
    missing_devs = []
    missing_syms = []
    missing_fps = []
    symbol_mismatch = []
    for cid, c in mo["comps"].items():
        dr = c["attrs"].get("Device", [])
        if not dr:
            missing_devs.append((cid, "none"))
            continue
        did = dr[0][4]
        dev = mo["proj"].get("devices", {}).get(did)
        if not dev:
            missing_devs.append((cid, did))
            continue
        sid = dev.get("attributes", {}).get("Symbol")
        if not sid or f"SYMBOL/{sid}.esym" not in no:
            missing_syms.append((cid, sid))
            continue
        parts = [r[1] for r in mo["syms"](sid) if r[0] == "PART"]
        if c["record"][2] not in parts:
            missing_parts.append((cid, c["record"][2], sid, parts[:5]))
        sr = c["attrs"].get("Symbol", [])
        if sr and any(r[4] != sid for r in sr):
            symbol_mismatch.append((cid, [r[4] for r in sr], sid))
        fp = dev.get("attributes", {}).get("Footprint", "")
        if fp:
            if fp not in mo["proj"].get("footprints", {}) or f"FOOTPRINT/{fp}.efoo" not in no:
                missing_fps.append((cid, fp))
    for arr, label in [
        (missing_devs, "missing devices"),
        (missing_syms, "missing symbols"),
        (missing_parts, "invalid component PART refs"),
        (symbol_mismatch, "symbol attrs mismatch"),
        (missing_fps, "missing footprints"),
    ]:
        if arr:
            errors.append(label + ": " + repr(arr[:12]))
    dups_des = {d: c for d, c in mo["bydes"].items() if len(c) > 1 and d != "U6-RTC"}
    if dups_des:
        errors.append("duplicate designators " + repr({k: len(v) for k, v in dups_des.items()}))
    if len(mo["bydes"].get("U6-RTC", [])) != 2:
        errors.append("U6 multipart count !=2")
    pcb = [n for n in no if n.endswith(".epcb")]
    pcb_unchanged = {n: (n in ni and zo.read(n) == zi.read(n)) for n in pcb}
    if not all(pcb_unchanged.values()):
        errors.append("PCB bytes changed")
    for n in pcb:
        if h(zo.read(n)) != PCB_SHA:
            errors.append(f"PCB SHA mismatch {n}")
    common = set(ni) & set(no)
    changed = sorted(n for n in common if h(zi.read(n)) != h(zo.read(n)))
    added = sorted(set(no) - set(ni))
    removed = sorted(set(ni) - set(no))
    for des in ["R40-AUD", "R41-AUD", "R45-MOT", "R47-MOT", "R49-MOT", "R56-VAL", "R57-VAL"]:
        for k, expected in [
            ("Add into BOM", "no"),
            ("Convert to PCB", "no"),
            ("Manufacturer Part", ""),
            ("Supplier Part", ""),
            ("supplierId", ""),
        ]:
            vv = vals(mo, des, k)
            if not vv or any(v != expected for v in vv):
                errors.append(f"RQ048 {des} {k}={vv!r}, expected {expected!r}")
    for des in ["DVBUS-PWR1", "U17-PWR2"]:
        if vals(mo, des, "Convert to PCB") != ["no"]:
            errors.append(f"{des} custom footprint hold not fail-closed")
    checks = {
        "BUCK_PG": ("U3-PWR2", "5", "BUCK_PG", None),
        "LIS_CS": ("U13-MOT", "2", "3V3", None),
        "LIS_SA0": ("U13-MOT", "3", "GND", None),
        "RT_USB_DP": ("U6-RTC", "L8", "USB_DP_RT", "MIMXRT1062DVJ6B.2"),
        "RT_USB_DN": ("U6-RTC", "M8", "USB_DN_RT", "MIMXRT1062DVJ6B.2"),
        "RT_USB_VBUS": ("U6-RTC", "N6", "5V_PROTECTED", "MIMXRT1062DVJ6B.2"),
        "NFC_VDD": ("U12-NFC", "8", "NFC_5V", None),
        "NFC_VDDTX": ("U12-NFC", "10", "NFC_5V", None),
        "NFC_RFI1": ("U12-NFC", "22", "NFC_RFI1_DIV", None),
        "S3_FILTERED": ("U9-ESP", "2", "3V3_S3_FILTERED", None),
        "U16_SENSE": ("U16-VAL", "5", "3V3", None),
    }
    check_results = {}
    pno = mo["pn"]
    for name, (des, p, net, part) in checks.items():
        allnets = pno(des, p, part)
        ok = bool(allnets and any(net in x for x in allnets))
        check_results[name] = {"ok": ok, "nets": allnets}
        if not ok:
            errors.append(f"postcondition {name} failed: {allnets}")
    if "U1-PWR1" not in mo["bydes"]:
        errors.append("U1-PWR1 missing; trunk eFuse must remain")
    if "U4-PWR2" in mo["bydes"]:
        errors.append("U4-PWR2 still present; shared LED eFuse should be replaced by U17")
    if "U17-PWR2" not in mo["bydes"]:
        errors.append("U17-PWR2 missing; per-branch LED protection not drawn")
    if "R8-PWR2" in mo["bydes"]:
        errors.append("R8-PWR2 remains after U4 removal; ILIM remnant")
    if "C68-PWR2" in mo["bydes"]:
        errors.append("C68-PWR2 remains after U4 removal; DVDT remnant")
    u1_pg = set()
    for nets in pno("U1-PWR1", "3"):
        u1_pg.update(nets)
    r67_pg = set()
    for nets in pno("R67-PWR1", "2"):
        r67_pg.update(nets)
    shared = u1_pg & r67_pg
    check_results["U1_PG_WITH_R67"] = {"ok": bool(shared), "u1": sorted(u1_pg), "r67": sorted(r67_pg)}
    if not shared:
        errors.append(f"U1.3 and R67.2 do not share a PG net: U1={sorted(u1_pg)} R67={sorted(r67_pg)}")
    for ref in ("R31-AUD", "R32-AUD", "R33-AUD"):
        if ref not in mo["bydes"]:
            errors.append(f"{ref} missing; DEC-13 requires R31-R33 all three fitted")
    out_ids = set(ids)
    for rid in ["e153914", "e146347"]:
        if rid in out_ids:
            errors.append(f"stale primitive remains: {rid}")
    orphan_findings = orphan_invariant(mi, mo, errors, warnings)
    res = {
        "audit": "CLI independent structural/semantic audit; does not import into EasyEDA GUI",
        "input_sha256": h(input_path.read_bytes()),
        "output_sha256": h(output_path.read_bytes()),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "archive_entries_before": len(ni),
        "archive_entries_after": len(no),
        "changed_existing_members": changed,
        "added_members": added,
        "removed_members": removed,
        "pcb_unchanged": pcb_unchanged,
        "schematic_record_count": len(mo["recs"]),
        "component_primitives": len(mo["comps"]),
        "designator_attributes": sum(len(v) for v in mo["bydes"].values()),
        "unique_designators": len(mo["bydes"]),
        "device_count": len(mo["proj"].get("devices", {})),
        "symbol_count": len(mo["proj"].get("symbols", {})),
        "footprint_count": len(mo["proj"].get("footprints", {})),
        "key_postconditions": check_results,
        "orphan_net_findings": orphan_findings,
        "rq048_exact_metadata": {
            d: {
                k: vals(mo, d, k)
                for k in ["Add into BOM", "Convert to PCB", "Manufacturer Part", "Supplier Part", "supplierId"]
            }
            for d in ["R40-AUD", "R41-AUD", "R45-MOT", "R47-MOT", "R49-MOT", "R56-VAL", "R57-VAL"]
        },
        "custom_footprint_holds": {d: vals(mo, d, "Convert to PCB") for d in ["DVBUS-PWR1", "U17-PWR2"]},
        "presence": {
            "U1-PWR1": "U1-PWR1" in mo["bydes"],
            "U4-PWR2": "U4-PWR2" in mo["bydes"],
            "U17-PWR2": "U17-PWR2" in mo["bydes"],
            "R8-PWR2": "R8-PWR2" in mo["bydes"],
            "C68-PWR2": "C68-PWR2" in mo["bydes"],
            "C11-PWR2": "C11-PWR2" in mo["bydes"],
            "R67-PWR1": "R67-PWR1" in mo["bydes"],
        },
    }
    report_path.write_text(json.dumps(res, indent=2) + "\n")
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description="G2.1 independent epro audit with orphan-net invariant")
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--report", required=True)
    a = ap.parse_args()
    res = audit(Path(a.input), Path(a.output), Path(a.report))
    print(json.dumps({"ok": res["ok"], "output_sha256": res["output_sha256"], "errors": res["errors"][:20]}, indent=2))
    return 0 if res["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
