#!/usr/bin/env python3
"""Extract and optionally freeze the G2.1 electrical digest.

Geometry is excluded. Serialization generation of the source is recorded so
the renderer can emit the same generation. U4-era companions are a census
assertion, not a premise.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
from easyeda_source_format import detect_format
from extract_electrical_graph import extract_electrical_graph, _load_source, _pin_bindings
from g22_pwr1_ilm import analyse as analyse_ilm
from g22_usb_hub import analyse as analyse_usb_hub

U4_ERA = ("U4-PWR2", "C68-PWR2", "R8-PWR2")
REQUIRED_PRESENT = ("U1-PWR1", "U17-PWR2")
HUB_FORBIDDEN = (
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
    "DVBUS-PWR1",
)
J1_DESIGNATOR = "J1-PWR1"
HUB_REQUIRED = (
    J1_DESIGNATOR,
    "J6-ESP",
    "U20-USB",
    "U21-USB",
    "U22-USB",
    "U23-USB",
    "U24-USB",
    "U25-USB",
)


def census_u4(identity: dict) -> dict:
    present = [name for name in U4_ERA if name in identity]
    required = [name for name in REQUIRED_PRESENT if name not in identity]
    leftovers = []
    for name in identity:
        if name.startswith("U4-") or name in U4_ERA:
            leftovers.append(name)
    return {
        "u4_era_absent": not present,
        "unexpected_present": present,
        "required_missing": required,
        "leftover_named": leftovers,
        "ok": (not present) and (not required),
    }


def census_hub(identity: dict) -> dict:
    forbidden_present = [name for name in HUB_FORBIDDEN if name in identity]
    required_missing = [name for name in HUB_REQUIRED if name not in identity]
    return {
        "forbidden_present": forbidden_present,
        "required_missing": required_missing,
        "ok": (not forbidden_present) and (not required_missing),
    }


def digest_bytes(graph: dict) -> str:
    payload = {
        "identity": graph["identity"],
        "nets": graph["nets"],
        "nc": graph["nc"],
        "pin_membership": graph.get("pin_membership"),
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--pin-bindings", type=Path)
    parser.add_argument("--role", default="G2.1_ELECTRICAL_DIGEST")
    parser.add_argument("--official-freeze", action="store_true")
    parser.add_argument("--erc-disposition", type=Path, help="required for official freeze")
    parser.add_argument(
        "--hub-identity",
        action="store_true",
        help="require D-049 hub census (J7 gone, U20–U25 present)",
    )
    parser.add_argument(
        "--ilm-semantics",
        action="store_true",
        help="require U1-PWR1.9 ILM on USB_EFUSE_ILIM (G2.2 promotion gate)",
    )
    parser.add_argument(
        "--skip-ilm-semantics",
        action="store_true",
        help="explicit opt-out; G2.2 roles and official freeze ignore this",
    )
    parser.add_argument(
        "--usb-hub-semantics",
        action="store_true",
        help="require D-049/D-050 J1 + USB2422 semantic completion (G2.2 promotion gate)",
    )
    parser.add_argument(
        "--skip-usb-hub-semantics",
        action="store_true",
        help="explicit opt-out; G2.2 roles and official freeze ignore this",
    )
    args = parser.parse_args(argv)

    source, meta = _load_source(args.source)
    generation = detect_format(source)
    if args.official_freeze:
        if not args.erc_disposition or not args.erc_disposition.is_file():
            print("ORACLE=REFUSED official freeze requires item-level ERC disposition")
            return 2
        disp = json.loads(args.erc_disposition.read_text(encoding="utf-8"))
        if disp.get("unclassified_fatals", 1) != 0:
            print("ORACLE=REFUSED unclassified ERC fatals remain")
            return 2
        if disp.get("real_defects_open", 1) != 0:
            print("ORACLE=REFUSED real electrical defects remain")
            return 2

    graph = extract_electrical_graph(
        source,
        source_path=str(args.source),
        pin_bindings=_pin_bindings(args.pin_bindings),
        role=args.role,
        official_freeze=args.official_freeze,
    )
    graph["serialization"] = {
        "generation": generation,
        "source_document_uuid": meta.get("documentUuid"),
        "source_hash_host": meta.get("sourceHash"),
    }
    graph["u4_census"] = census_u4(graph["identity"])
    hub = census_hub(graph["identity"])
    graph["hub_census"] = hub
    graph["electrical_digest_sha256"] = digest_bytes(graph)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    census = graph["u4_census"]
    want_hub = args.hub_identity or "HUB" in str(args.role).upper()
    print(
        "ORACLE=OK "
        f"generation={generation} "
        f"designators={graph['counts']['designators']} "
        f"digest={graph['electrical_digest_sha256'][:16]} "
        f"official_freeze={graph['official_freeze']} "
        f"u4_census_ok={census['ok']} "
        f"hub_census_ok={hub['ok'] if want_hub else 'n/a'}"
    )
    if not census["ok"]:
        print(f"  unexpected={census['unexpected_present']} missing={census['required_missing']}")
        return 2
    if want_hub and not hub["ok"]:
        print(
            "ORACLE=REFUSED hub identity "
            f"forbidden={hub['forbidden_present']} missing={hub['required_missing']}"
        )
        return 2
    role_u = str(args.role).upper()
    g22_role = "G2.2" in role_u or "G22" in role_u
    want_ilm = args.ilm_semantics or g22_role or args.official_freeze
    if args.skip_ilm_semantics and not args.official_freeze and not g22_role:
        want_ilm = False
    if want_ilm:
        if "U1-PWR1" not in (graph.get("identity") or {}):
            print("ORACLE=REFUSED U1-PWR1 absent; ILM pin-role resolution unavailable")
            return 2
        expect_r1 = 1240 if (g22_role or args.ilm_semantics) else None
        ilm = analyse_ilm(source, source_path=str(args.source), expect_r1_ohms=expect_r1)
        graph["ilm_semantics"] = ilm.as_dict()
        args.output.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(
            "ILM_SEMANTICS "
            f"ok={ilm.ok} unresolved={ilm.unresolved} "
            f"pin9={None if '9' not in ilm.u1_pins else ilm.u1_pins['9'].nets} "
            f"r1_ohms={ilm.r1.get('electrical_ohms')}"
        )
        if ilm.unresolved or not ilm.ok:
            print("ORACLE=REFUSED U1 ILM semantic failure — G2.2 promotion / JLC-SCH-READY cannot close")
            for item in ilm.errors:
                print(f"  {item}")
            return 2
    want_usb = args.usb_hub_semantics or g22_role or args.official_freeze
    if args.skip_usb_hub_semantics and not args.official_freeze:
        want_usb = False
    if want_usb:
        identity = graph.get("identity") or {}
        if J1_DESIGNATOR not in identity:
            if args.usb_hub_semantics or args.official_freeze:
                print("ORACLE=REFUSED J1-PWR1 absent; USB hub pin-role resolution unavailable")
                return 2
            print("USB_HUB_SEMANTICS skipped — J1-PWR1 absent on this sheet")
        else:
            usb = analyse_usb_hub(source, source_path=str(args.source))
            graph["usb_hub_semantics"] = usb.as_dict()
            args.output.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(
                "USB_HUB_SEMANTICS "
                f"ok={usb.ok} unresolved={usb.unresolved} "
                f"j1_wired={usb.paths.get('j1_functional_wired')} "
                f"cfg_sel={(usb.straps or {}).get('CFG_SEL')} "
                f"non_rem_10={(usb.straps or {}).get('non_rem_10')}"
            )
            if usb.unresolved or not usb.ok:
                print("ORACLE=REFUSED USB2422/J1 semantic failure — USB_HUB_PHASE_K cannot close")
                for item in usb.errors:
                    print(f"  {item}")
                return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
