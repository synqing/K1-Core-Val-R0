#!/usr/bin/env python3
"""DEC-USB-HUB Phase E census extractor.

Reads only G2.1 electrical sources (3db861a3 epro + review dumps).
Does not touch EasyEDA. Writes _phase_e_census.json next to this script.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OFF = REPO / "evidence/VAL-G2-2026-08-28/offline-bulk-repair"
EPRO = OFF / "K1-Core-Val-R0-G2.1-BULK-CANDIDATE-3db861a3.epro"
SEED = OFF / "g2.1-electrical-graph-seed.json"
BIND = OFF / "review-pin-bindings.json"
SRC_AFTER = OFF / "review-source-after-reopen.json"
AUDIT = OFF / "independent-audit-3db861a3.json"
CENSUS = OFF / "review-source-census-after-reopen.json"

sys.path.insert(0, str(OFF))
from independent_epro_audit_cli import build, vals  # noqa: E402


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def ident_of(seed: dict, des: str) -> dict:
    rec = seed.get("identity", {}).get(des) or {}
    unit = (rec.get("units") or [{}])[0]
    return {
        "designator": des,
        "present_in_seed": des in seed.get("identity", {}),
        "mpn": unit.get("mpn") or (rec.get("mpns") or [None])[0],
        "lcsc": unit.get("supplier_part") or (rec.get("supplier_parts") or [None])[0],
        "part_id": unit.get("part_id") or (rec.get("part_ids") or [None])[0],
        "value": unit.get("value"),
        "bom": unit.get("bom"),
        "pcb": unit.get("pcb"),
        "device": unit.get("device"),
        "symbol": unit.get("symbol"),
    }


def epro_attrs(model, des: str) -> dict:
    keys = [
        "Manufacturer Part",
        "Supplier Part",
        "supplierId",
        "Value",
        "Add into BOM",
        "Convert to PCB",
        "Name",
        "LCSC Part Name",
    ]
    out = {}
    for k in keys:
        vv = vals(model, des, k)
        if vv:
            out[k] = vv
    return out


def pin_inventory(model, des: str) -> list[dict]:
    """Every symbol pin for a designator, with geometric net membership."""
    by_num: dict[str, dict] = {}
    for (d, num), plist in model["_pins_raw"].items():
        if d != des:
            continue
        for p in plist:
            ns = set()
            for wid, x1, y1, x2, y2 in model["_seg"]:
                if _onseg(p["x"], p["y"], x1, y1, x2, y2):
                    ns.update(a[4] for a in model["_wattrs"].get(wid, []))
            rec = by_num.setdefault(
                str(num),
                {
                    "pin": str(num),
                    "name": p.get("name"),
                    "part": p.get("part"),
                    "pin_id": p.get("pin_id"),
                    "nc_flag": False,
                    "nets": [],
                    "net": None,
                    "instances": 0,
                },
            )
            rec["instances"] += 1
            if p.get("name") and not rec.get("name"):
                rec["name"] = p.get("name")
            rec["nets"] = sorted(set(rec["nets"]) | ns)
            rec["net"] = rec["nets"][0] if len(rec["nets"]) == 1 else (rec["nets"] or None)
    for cid in model["bydes"].get(des, []):
        for a in model["comps"][cid]["attrs"].get("No Connect", []) + model["comps"][cid][
            "attrs"
        ].get("NO_CONNECT", []):
            pass
    return [by_num[k] for k in sorted(by_num, key=_pin_sort)]


def _pin_sort(n: str):
    m = re.match(r"^([A-Z]*)(\d+)$", n)
    if m:
        return (m.group(1), int(m.group(2)))
    return (n, 0)


def _onseg(px, py, x1, y1, x2, y2, tol=1e-6):
    return (
        abs((px - x1) * (y2 - y1) - (py - y1) * (x2 - x1)) <= tol
        and min(x1, x2) - tol <= px <= max(x1, x2) + tol
        and min(y1, y2) - tol <= py <= max(y1, y2) + tol
    )


def attach_raw(model, z):
    """Rebuild pin list with pin_id so NC flags can be resolved."""
    import math

    def trans(x, y, cx, cy, rot, mirror):
        if mirror:
            x = -x
        a = math.radians(rot % 360)
        ca = round(math.cos(a), 12)
        sa = round(math.sin(a), 12)
        return round(cx + x * ca - y * sa, 6), round(cy + x * sa + y * ca, 12)

    recs = model["recs"]
    wires = {r[1]: r for r in recs if r[0] == "WIRE"}
    wattrs = defaultdict(list)
    for r in recs:
        if r[0] == "ATTR" and r[2] in wires and r[3] == "NET":
            wattrs[r[2]].append(r)
    seg = []
    for wid, r in wires.items():
        for s in r[2]:
            if len(s) >= 4:
                seg.append((wid, *map(float, s[:4])))

    pins_raw = defaultdict(list)
    nc_by_pin_id = {}
    for r in recs:
        if r[0] == "ATTR" and len(r) >= 5 and r[3] in {"No Connect", "NO_CONNECT", "noConnected"}:
            nc_by_pin_id[r[2]] = r[4]

    proj = model["proj"]
    for des, cids in model["bydes"].items():
        for cid in cids:
            c = model["comps"][cid]
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
            part = None
            pins = {}
            for r in model["syms"](sid):
                if r[0] == "PART":
                    part = r[1]
                elif r[0] == "PIN" and part == c["record"][2]:
                    pins[r[1]] = {"x": r[4], "y": r[5], "num": None, "name": None}
                elif r[0] == "ATTR" and r[2] in pins:
                    if r[3] == "NUMBER":
                        pins[r[2]]["num"] = str(r[4])
                    elif r[3] == "NAME":
                        pins[r[2]]["name"] = r[4]
            for lp, p in pins.items():
                if p["num"] is None:
                    continue
                x, y = trans(p["x"], p["y"], c["record"][3], c["record"][4], c["record"][5], c["record"][6])
                pins_raw[(des, p["num"])].append(
                    {
                        "x": x,
                        "y": y,
                        "part": c["record"][2],
                        "pin_id": f"{cid}-{lp}" if not str(lp).startswith(str(cid)) else lp,
                        "local_pin_id": lp,
                        "comp_id": cid,
                        "name": p["name"],
                    }
                )
    model["_pins_raw"] = pins_raw
    model["_seg"] = seg
    model["_wattrs"] = wattrs
    model["_nc_by_pin_id"] = nc_by_pin_id
    return model


def apply_nc(model, inv: list[dict], seed_nc: list[dict], des: str) -> list[dict]:
    seed_ids = {n["pin_id"] for n in seed_nc if n.get("designator") == des}
    for p in inv:
        cid = None
        raw = model["_pins_raw"].get((des, p["pin"]), [])
        flags = []
        for r in raw:
            pid_full = f"{r['comp_id']}-{r['local_pin_id']}"
            pid_alt = r["local_pin_id"]
            if pid_full in seed_ids or pid_alt in seed_ids:
                flags.append(True)
            # ATTR No Connect on pin primitive
            for key in (pid_full, pid_alt, r.get("pin_id")):
                if key in model["_nc_by_pin_id"]:
                    flags.append(True)
        p["nc_flag"] = bool(flags) or any(
            n.get("pin_id", "").endswith(f"-{raw[0]['local_pin_id']}")
            for n in seed_nc
            if n.get("designator") == des
        ) if raw else bool(flags)
        # also match seed pin_id suffix
        if raw:
            loc = raw[0]["local_pin_id"]
            if any(n.get("pin_id", "").endswith(f"-{loc}") for n in seed_nc if n.get("designator") == des):
                p["nc_flag"] = True
    return inv


def net_members(model, net: str) -> list[str]:
    return sorted(model["membership"].get(net, set()))


def live_bindings(bind: dict, des: str) -> list[dict]:
    rows = []
    for p in bind.get("bindings", {}).get(des, []):
        rows.append(
            {
                "pin": str(p.get("pin")),
                "name": p.get("name"),
                "nc": p.get("nc"),
                "net": p.get("net"),
                "nets": p.get("nets") or [],
            }
        )
    return rows


def numeric_prefix(des: str, letter: str) -> int | None:
    m = re.match(rf"^{letter}(\d+)", des)
    return int(m.group(1)) if m else None


def main() -> None:
    seed = json.loads(SEED.read_text())
    bind = json.loads(BIND.read_text())
    census = json.loads(CENSUS.read_text())
    src_after = json.loads(SRC_AFTER.read_text())
    audit = json.loads(AUDIT.read_text())

    z = zipfile.ZipFile(EPRO)
    model = build(z)
    attach_raw(model, z)

    designators = sorted(model["bydes"])
    seed_des = sorted(seed.get("identity", {}))
    census_des = census.get("unique_designators") or []

    families = {k: [] for k in "URCYJ"}
    for d in designators:
        letter = d[0]
        if letter in families:
            families[letter].append(d)

    seed_nc = seed.get("nc") or []

    targets = [
        "J1-PWR1",
        "D1-PWR1",
        "U1-PWR1",
        "U2-PWR1",
        "RSH1-PWR1",
        "RCC1-PWR1",
        "RCC2-PWR1",
        "RCC1S-PWR1",
        "RCC1B-PWR1",
        "RCC2S-PWR1",
        "RCC2B-PWR1",
        "RUSB_DP-PWR1",
        "RUSB_DN-PWR1",
        "DVBUS-PWR1",
        "C1-PWR1",
        "C2-PWR1",
        "C3-PWR1",
        "C4-PWR1",
        "C67-PWR1",
        "R1-PWR1",
        "R2-PWR1",
        "R3-PWR1",
        "R4-PWR1",
        "R63-PWR1",
        "R64-PWR1",
        "R65-PWR1",
        "R66-PWR1",
        "R67-PWR1",
        "CINA_DIFF-PWR1",
        "RINA_N-PWR1",
        "RINA_P-PWR1",
        "J7-ESP",
        "U10-ESP",
        "C43-ESP",
        "C44-ESP",
        "R71-ESP",
        "R72-ESP",
        "R73-ESP",
        "R74-ESP",
        "R21-ESP",
        "R22-ESP",
        "FB4-ESP",
        "FB6-ESP",
        "U9-ESP",
        "J6-ESP",
        "U6-RTC",
        "CUSBVBUS-RTC",
        "R56-VAL",
        "R57-VAL",
        "C69-RTC",
        "C70-RTC",
        "C71-RTC",
        "C72-RTC",
        "C73-RTC",
        "C74-RTC",
        "C75-RTC",
        "C76-RTC",
        "C77-RTC",
        "C78-RTC",
        "C79-RTC",
        "C80-RTC",
        "C81-RTC",
        "C82-RTC",
        "C83-RTC",
        "C84-RTC",
        "C85-RTC",
        "C86-RTC",
        "C87-RTC",
        "C88-RTC",
        "C89-RTC",
        "C90-AUD",
    ]

    parts = {}
    for des in targets:
        present = des in model["bydes"]
        inv = pin_inventory(model, des) if present else []
        if present:
            apply_nc(model, inv, seed_nc, des)
        parts[des] = {
            "present_epro": present,
            "present_seed": des in seed.get("identity", {}),
            "present_census": des in census_des,
            "identity_seed": ident_of(seed, des) if des in seed.get("identity", {}) else None,
            "epro_attrs": epro_attrs(model, des) if present else {},
            "pins": inv,
            "live_bindings": live_bindings(bind, des),
            "component_ids": list(model["bydes"].get(des, [])),
        }

    # U6 OTG-named pins only (name contains USB)
    u6_usb = [p for p in parts["U6-RTC"]["pins"] if p.get("name") and "USB" in str(p["name"]).upper()]

    # U9 USB-ish pins (GPIO19/20/15 or USB in name)
    u9_usb = [
        p
        for p in parts["U9-ESP"]["pins"]
        if str(p.get("pin")) in {"8", "13", "14"}
        or (p.get("name") and re.search(r"USB|GPIO19|GPIO20|GPIO15", str(p["name"]), re.I))
    ]

    interesting_nets = [
        "5V_USB",
        "5V_PROTECTED",
        "5V_SYS",
        "USB_CC1",
        "USB_CC2",
        "USB_CC1_ADC_TAP",
        "USB_CC2_ADC_TAP",
        "USB_DP_J1",
        "USB_DN_J1",
        "USB_DP_PROT",
        "USB_DN_PROT",
        "USB_DP_RT",
        "USB_DN_RT",
        "USB_DP",
        "USB_DM",
        "USB_DP_ESD",
        "USB_DM_ESD",
        "USB_DP_S3",
        "USB_DM_S3",
        "S3_VBUS",
        "ESP_USB_VBUS_SENSE",
        "OPT_USB_AUD",
        "OPT_USB_AUD_RT",
        "RT_USB_AUD_STRAP_IOMUX_TBD",
        "VDD_USB_CAP",
        "USB_EFUSE_EN",
        "USB_EFUSE_OVLO",
        "USB_EFUSE_PGTH",
        "USB_EFUSE_ILIM",
        "USB_EFUSE_DVDT",
        "PWR_ENTRY_PG_RT_IOMUX_TBD",
        "INA_KELVIN_P",
        "INA_KELVIN_N",
        "INA_ALERT",
        "ESP_UART0_TX",
        "ESP_UART0_RX",
        "ESP_EN",
        "ESP_GPIO0",
    ]
    net_map = {}
    for n in interesting_nets:
        members = net_members(model, n)
        net_map[n] = {
            "present": n in model["membership"] or n in seed.get("nets", []),
            "in_seed_net_list": n in seed.get("nets", []),
            "member_count": len(members),
            "members": members,
        }

    # UART-bridge IC hunt in identity / part_id
    uart_hits = []
    for des, rec in seed.get("identity", {}).items():
        blob = json.dumps(rec).upper()
        if re.search(r"CP210|CH340|CH344|FT232|FT2232|USB.?UART|CP211|WCH.*UART", blob):
            uart_hits.append(des)

    # next-free allocator
    used_u = sorted({numeric_prefix(d, "U") for d in families["U"] if numeric_prefix(d, "U") is not None})
    used_r = sorted({numeric_prefix(d, "R") for d in families["R"] if numeric_prefix(d, "R") is not None})
    used_c = sorted({numeric_prefix(d, "C") for d in families["C"] if numeric_prefix(d, "C") is not None})
    used_y = sorted({numeric_prefix(d, "Y") for d in families["Y"] if numeric_prefix(d, "Y") is not None})
    used_j = sorted({numeric_prefix(d, "J") for d in families["J"] if numeric_prefix(d, "J") is not None})

    def first_free(used: list[int], start: int) -> int:
        n = start
        s = set(used)
        while n in s:
            n += 1
        return n

    suffix_usb = [d for d in designators if d.endswith("-USB")]
    suffix_hub = [d for d in designators if d.endswith("-HUB")]

    # CC collision: members whose designator is J7 island vs J1 island
    j7_island = {
        "J7-ESP",
        "U10-ESP",
        "C43-ESP",
        "C44-ESP",
        "R71-ESP",
        "R72-ESP",
        "R73-ESP",
        "R74-ESP",
        "R21-ESP",
        "R22-ESP",
        "FB4-ESP",
        "FB6-ESP",
    }
    j1_cc_parts = {
        "J1-PWR1",
        "RCC1-PWR1",
        "RCC2-PWR1",
        "RCC1S-PWR1",
        "RCC1B-PWR1",
        "RCC2S-PWR1",
        "RCC2B-PWR1",
    }

    def des_of_member(m: str) -> str:
        return m.split("|", 1)[0]

    cc_collision = {}
    for net in ("USB_CC1", "USB_CC2"):
        mems = net_map[net]["members"]
        dess = {des_of_member(m) for m in mems}
        cc_collision[net] = {
            "members": mems,
            "designators": sorted(dess),
            "j1_members": sorted(dess & j1_cc_parts),
            "j7_members": sorted(dess & j7_island),
            "other": sorted(dess - j1_cc_parts - j7_island),
            "shared_across_j1_and_j7": bool(dess & j1_cc_parts) and bool(dess & j7_island),
        }

    # audit postconditions of interest
    kp = audit.get("key_postconditions") or {}

    # source-after-reopen: confirm document identity only
    src_meta = {
        "keys": sorted(src_after.keys()) if isinstance(src_after, dict) else None,
        "documentUuid": src_after.get("documentUuid") if isinstance(src_after, dict) else None,
        "sourceHash": None,
    }
    if isinstance(src_after, dict):
        src_meta["sourceHash"] = src_after.get("sourceHash") or src_after.get("source_hash")
        if "source" in src_after and isinstance(src_after["source"], str):
            src_meta["source_chars"] = len(src_after["source"])

    # J1 symbol pin names vs Type-C 24-pin expected set (documentation only)
    expected_24 = [
        "A1",
        "A2",
        "A3",
        "A4",
        "A5",
        "A6",
        "A7",
        "A8",
        "A9",
        "A10",
        "A11",
        "A12",
        "B1",
        "B2",
        "B3",
        "B4",
        "B5",
        "B6",
        "B7",
        "B8",
        "B9",
        "B10",
        "B11",
        "B12",
    ]
    j1_pins = {p["pin"] for p in parts["J1-PWR1"]["pins"]}
    j1_24 = {
        "symbol_pins": sorted(j1_pins, key=_pin_sort),
        "expected_24_present": [p for p in expected_24 if p in j1_pins],
        "expected_24_absent": [p for p in expected_24 if p not in j1_pins],
        "extra_symbol_pins": sorted(j1_pins - set(expected_24), key=_pin_sort),
    }

    out = {
        "sources": {
            "epro": str(EPRO.relative_to(REPO)),
            "epro_sha256": sha256(EPRO),
            "seed": str(SEED.relative_to(REPO)),
            "seed_sha256": sha256(SEED),
            "bindings": str(BIND.relative_to(REPO)),
            "bindings_sha256": sha256(BIND),
            "review_source_after_reopen": str(SRC_AFTER.relative_to(REPO)),
            "review_source_after_reopen_sha256": sha256(SRC_AFTER),
            "independent_audit": str(AUDIT.relative_to(REPO)),
            "independent_audit_output_sha256": audit.get("output_sha256"),
            "census_after_reopen": str(CENSUS.relative_to(REPO)),
        },
        "counts": {
            "epro_designators": len(designators),
            "seed_designators": len(seed_des),
            "census_designators": len(census_des),
            "epro_named_nets": len(model["membership"]),
            "seed_named_nets": len(seed.get("nets") or []),
        },
        "designators": {
            "all": designators,
            "U": families["U"],
            "R": families["R"],
            "C": families["C"],
            "Y": families["Y"],
            "J": families["J"],
        },
        "allocator": {
            "used_U": used_u,
            "used_R": used_r,
            "used_C": used_c,
            "used_Y": used_y,
            "used_J": used_j,
            "next_free_U_from_18": first_free(used_u, 18),
            "next_free_R_from_77": first_free(used_r, 77),
            "next_free_C_from_100": first_free(used_c, 100),
            "next_free_Y_from_3": first_free(used_y, 3),
            "next_free_J_from_12": first_free(used_j, 12),
            "suffix_USB_collision": suffix_usb,
            "suffix_HUB_collision": suffix_hub,
            "U4_present": "U4-PWR2" in designators or any(d.startswith("U4-") for d in designators),
        },
        "parts": parts,
        "u6_usb_named_pins": u6_usb,
        "u9_usb_related_pins": u9_usb,
        "nets": net_map,
        "cc_collision": cc_collision,
        "uart_bridge_hits": uart_hits,
        "audit_usb_postconditions": {k: kp[k] for k in kp if "USB" in k},
        "j1_vs_24pin": j1_24,
        "fb4_present": "FB4-ESP" in designators,
        "src_after_meta": src_meta,
        "seed_nets_usb": [n for n in seed.get("nets") or [] if "USB" in n or n in {"S3_VBUS", "OPT_USB_AUD"}],
    }

    dest = HERE / "_phase_e_census.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {dest} designators={len(designators)} nets={len(model['membership'])}")


if __name__ == "__main__":
    main()
