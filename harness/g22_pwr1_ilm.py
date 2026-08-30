#!/usr/bin/env python3
"""G2.2 PWR1 ILM semantic reconstruction (TPS259474L pin 9).

A graph with bound_pin_count=0 is not allowed to pass this check via silent
coordinate coincidence. Pin membership is reconstructed from the TPS259474L
symbol offsets plus the instance transform, then validated against a known-good
majority of U1 pins before pin 9 is believed.

Electrical value for R1-PWR1 is taken from Device / Manufacturer Part / Name /
Supplier Part. The legacy partId string is never the ohmic value.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from easyeda_source_format import parse_v3_records
from extract_electrical_graph import _load_source

U1_DESIGNATOR = "U1-PWR1"
R1_DESIGNATOR = "R1-PWR1"
RUSB_DP_DESIGNATOR = "RUSB_DP-PWR1"
U20_DESIGNATOR = "U20-USB"
ILIM_NET = "USB_EFUSE_ILIM"
DP_NET = "USB_DP_UP"

# Symbol-frame offsets for TPS259474LRPWR.1 (EasyEDA symbol 76f01ceafa6a4cf682bb611206e2286f).
# Independently verified: rot180 of pin 9 (65, 55) at U1 (690, -4110) lands on (625, -4165).
TPS259474L_PINS: dict[str, dict[str, Any]] = {
    "1": {"name": "EN/UVLO", "sx": -85, "sy": 0},
    "2": {"name": "OVLO", "sx": -85, "sy": 20},
    "3": {"name": "PG", "sx": 90, "sy": 20},
    "4": {"name": "PGTH", "sx": 90, "sy": 0},
    "5": {"name": "IN", "sx": -85, "sy": -20},
    "6": {"name": "OUT", "sx": 90, "sy": -20},
    "7": {"name": "DVDT", "sx": -15, "sy": 55},
    "8": {"name": "GND", "sx": 25, "sy": 55},
    "9": {"name": "ILM", "sx": 65, "sy": 55},
    "10": {"name": "ITIMER", "sx": -50, "sy": 55},
}

# 0402 resistor: pin 1 left, pin 2 right in the unrotated symbol.
RESISTOR_0402_PINS: dict[str, tuple[int, int]] = {"1": (-20, 0), "2": (20, 0)}

# Pins that prove the transform before pin 9 is trusted. Pin 9 is the DUT.
# Pin 10 is an intentional open. Pin 3 is PG and may carry an IOMUX-hold name.
TRANSFORM_PROOF_PINS = ("1", "2", "4", "5", "6", "7", "8")
TRANSFORM_PROOF_MIN = 6

G2_2_EXPECTED_NETS: dict[str, str | None] = {
    "1": "USB_EFUSE_EN",
    "2": "USB_EFUSE_OVLO",
    "3": "PWR_ENTRY_PG_RT_IOMUX_TBD",
    "4": "USB_EFUSE_PGTH",
    "5": "5V_USB",
    "6": "5V_PROTECTED",
    "7": "USB_EFUSE_DVDT",
    "8": "GND",
    "9": ILIM_NET,
    "10": None,
}

CANONICAL_NETS: dict[str, str | None] = {
    "1": "USB_EFUSE_EN",
    "2": "USB_EFUSE_OVLO",
    "3": "PWR_ENTRY_PG_RT_IOMUX_TBD",
    "4": "USB_EFUSE_PGTH",
    "5": "5V_USB_FILTERED",
    "6": "5V_PROTECTED",
    "7": "USB_EFUSE_DVDT",
    "8": "GND",
    "9": ILIM_NET,
    "10": None,
}

INTENDED_RENAMES = {
    ("5", "5V_USB_FILTERED", "5V_USB"): "hub-era F1 trunk rename after ferrite left the path",
}

FORBIDDEN_USB_DIFF_RE = re.compile(
    r"(?:^USB_D[PM]$)|(?:^USB_D[PM]_)|(?:_D[PM]_(?:UP|DN|S3|J1|PROT))",
    re.I,
)

MPN_OHMS = {
    "RNCF0402BTC1K24": 1240,
    "RC0402FR-071K24L": 1240,
    "RC0402FR-071K33L": 1330,
    "RC0402FR-0710KL": 10000,
}

VALUE_RE = re.compile(
    r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([kKmM])?(?:[\s\u03a9ohmΩ]*)\s*$"
)
K24_RE = re.compile(r"1k24|1\.24\s*k", re.I)
PARTID_10K_RE = re.compile(r"0710K|10KL|10k", re.I)

EXPECTED_R1_OHMS = 1240
EXPECTED_R1_MPN = "RNCF0402BTC1K24"
EXPECTED_R1_LCSC = "C2491273"
EXPECTED_R1_DEVICE = "263cdab6e3341f4ea8fd57ccc688e923"


def _pt(x, y) -> tuple[int, int]:
    return int(round(float(x))), int(round(float(y)))


def transform_offset(sx: float, sy: float, rotation: int, is_mirror: bool) -> tuple[int, int]:
    x, y = float(sx), float(sy)
    if is_mirror:
        x = -x
    rot = int(rotation or 0) % 360
    if rot == 90:
        x, y = -y, x
    elif rot == 180:
        x, y = -x, -y
    elif rot == 270:
        x, y = y, -x
    elif rot != 0:
        raise ValueError(f"unsupported rotation {rotation}")
    return int(round(x)), int(round(y))


def pin_xy(comp: dict, sx: float, sy: float) -> tuple[int, int]:
    dx, dy = transform_offset(sx, sy, int(comp.get("rotation") or 0), bool(comp.get("isMirror")))
    return _pt(comp["x"] + dx, comp["y"] + dy)


def parse_ohms(text: str | None) -> int | None:
    if not text:
        return None
    raw = str(text).strip()
    if K24_RE.search(raw.replace("Ω", "").replace("ohm", "")):
        return 1240
    match = VALUE_RE.match(raw.replace("Ω", "").replace("ohm", "").replace(" ", ""))
    if not match:
        return None
    number = float(match.group(1))
    suffix = (match.group(2) or "").upper()
    if suffix == "K":
        number *= 1000
    elif suffix == "M":
        number *= 1_000_000
    return int(round(number))


def mpn_ohms(mpn: str | None) -> int | None:
    if not mpn:
        return None
    key = str(mpn).strip()
    if key in MPN_OHMS:
        return MPN_OHMS[key]
    if key.endswith(".1") and key[:-2] in MPN_OHMS:
        return MPN_OHMS[key[:-2]]
    return None


def is_forbidden_usb_diff(net: str | None) -> bool:
    if not net:
        return False
    return bool(FORBIDDEN_USB_DIFF_RE.search(str(net)))


@dataclass
class PinHit:
    pin: str
    name: str
    xy: tuple[int, int]
    nets: list[str]
    open: bool


@dataclass
class IlmReport:
    ok: bool
    unresolved: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    u1_pins: dict[str, PinHit] = field(default_factory=dict)
    r1: dict[str, Any] = field(default_factory=dict)
    ilim_members: list[str] = field(default_factory=list)
    dp_continuity: dict[str, Any] = field(default_factory=dict)
    transform: dict[str, Any] = field(default_factory=dict)
    reconstruction: str = "TPS259474L symbol offsets + instance transform; vertex coincidence at tolerance 0"

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "unresolved": self.unresolved,
            "errors": self.errors,
            "warnings": self.warnings,
            "counts": self.counts,
            "reconstruction": self.reconstruction,
            "transform": self.transform,
            "u1_pins": {
                pin: {
                    "name": hit.name,
                    "xy": list(hit.xy),
                    "nets": hit.nets,
                    "open": hit.open,
                }
                for pin, hit in self.u1_pins.items()
            },
            "r1": self.r1,
            "ilim_members": self.ilim_members,
            "dp_continuity": self.dp_continuity,
        }


def _attrs_by_owner(records) -> dict:
    attrs: dict = defaultdict(dict)
    for rec in records:
        if rec.type != "ATTR":
            continue
        key = rec.get("key")
        if not key:
            continue
        attrs[rec.get("parentId")][key] = rec.get("value")
    return attrs


def _components(records, attrs) -> dict[str, dict]:
    out = {}
    for rec in records:
        if rec.type != "COMPONENT":
            continue
        designator = attrs.get(rec.id, {}).get("Designator")
        if not designator:
            continue
        out[designator] = {
            "id": rec.id,
            "partId": rec.get("partId"),
            "x": rec.get("x"),
            "y": rec.get("y"),
            "rotation": rec.get("rotation") or 0,
            "isMirror": bool(rec.get("isMirror")),
            "attrs": dict(attrs.get(rec.id, {})),
        }
    return out


def _wire_geometry(records, attrs) -> tuple[dict[str, str], dict[str, list[tuple[int, int, int, int]]]]:
    net_of_wire = {}
    for rec in records:
        if rec.type == "ATTR" and rec.get("key") == "NET":
            net_of_wire[rec.get("parentId")] = rec.get("value")
    segs: dict[str, list] = defaultdict(list)
    for rec in records:
        if rec.type != "LINE":
            continue
        group = rec.get("lineGroup")
        segs[group].append(
            (
                int(round(float(rec.get("startX")))),
                int(round(float(rec.get("startY")))),
                int(round(float(rec.get("endX")))),
                int(round(float(rec.get("endY")))),
            )
        )
    return net_of_wire, segs


def _vertex_nets(net_of_wire, segs) -> dict[tuple[int, int], set[str]]:
    verts: dict[tuple[int, int], set[str]] = defaultdict(set)
    for wire_id, segments in segs.items():
        net = net_of_wire.get(wire_id)
        if not net:
            continue
        for sx, sy, ex, ey in segments:
            verts[(sx, sy)].add(net)
            verts[(ex, ey)].add(net)
    return verts


def _nets_named(net_of_wire, segs, name: str) -> list[str]:
    return [wid for wid, net in net_of_wire.items() if net == name]


def resolve_r1(comp: dict) -> dict[str, Any]:
    attrs = comp.get("attrs") or {}
    part_id = str(comp.get("partId") or "")
    mpn = attrs.get("Manufacturer Part") or ""
    name = attrs.get("Name") or ""
    value = attrs.get("Value") or ""
    device = attrs.get("Device") or ""
    supplier = attrs.get("Supplier Part") or attrs.get("supplierId") or ""
    electrical = mpn_ohms(mpn)
    if electrical is None:
        electrical = parse_ohms(name) or parse_ohms(value)
    partid_ohms = mpn_ohms(part_id.split(".1")[0] if part_id else None)
    if partid_ohms is None and PARTID_10K_RE.search(part_id):
        partid_ohms = 10000
    mismatch = bool(part_id) and partid_ohms is not None and electrical is not None and partid_ohms != electrical
    if electrical == 10000 and (mpn_ohms(mpn) in {1240, 1330} or parse_ohms(name) in {1240, 1330}):
        # partId must never win.
        electrical = mpn_ohms(mpn) or parse_ohms(name)
        mismatch = True
    return {
        "id": comp.get("id"),
        "partId": part_id,
        "device": device,
        "mpn": mpn,
        "name": name,
        "value_attr": value,
        "supplier": supplier,
        "electrical_ohms": electrical,
        "partid_implied_ohms": partid_ohms,
        "metadata_mismatch": mismatch,
        "xy": [comp.get("x"), comp.get("y")],
        "rotation": comp.get("rotation"),
    }


def _pin_hits(comp: dict, pin_table: dict, verts) -> dict[str, PinHit]:
    hits = {}
    for number, spec in pin_table.items():
        if isinstance(spec, dict):
            name, sx, sy = spec["name"], spec["sx"], spec["sy"]
        else:
            name, (sx, sy) = number, spec
        xy = pin_xy(comp, sx, sy)
        nets = sorted(verts.get(xy, set()))
        hits[number] = PinHit(pin=number, name=name, xy=xy, nets=nets, open=not nets)
    return hits


def classify_pin(pin: str, canonical: str | None, pre: str | None, post: str | None) -> str:
    if pin == "9" and pre == DP_NET and post == ILIM_NET:
        return "DEFECT_FIXED"
    if pin == "9" and post != ILIM_NET:
        return "DEFECT_OPEN"
    if post is None and canonical is None:
        return "SAME"
    if post == canonical:
        return "SAME"
    key = (pin, canonical, post)
    if key in INTENDED_RENAMES:
        return "INTENDED_RENAME"
    if post != canonical and canonical is not None:
        return "DEFECT_OPEN"
    return "SAME"


def analyse(
    source: str,
    *,
    source_path: str | None = None,
    expect_r1_ohms: int | None = EXPECTED_R1_OHMS,
    require_u1: bool = True,
) -> IlmReport:
    errors: list[str] = []
    warnings: list[str] = []
    report = IlmReport(ok=False, unresolved=False, errors=errors, warnings=warnings)

    records = parse_v3_records(source)
    files = 1 if source_path else 0
    if not records:
        report.unresolved = True
        report.counts = {
            "files_inspected": files,
            "easyeda_records_parsed": 0,
            "components_inspected": 0,
            "symbol_pins_resolved": 0,
            "nets_inspected": 0,
            "assertions_executed": 0,
        }
        errors.append("parsed 0 EasyEDA records; failing closed")
        return report

    attrs = _attrs_by_owner(records)
    components = _components(records, attrs)
    net_of_wire, segs = _wire_geometry(records, attrs)
    verts = _vertex_nets(net_of_wire, segs)
    named_nets = sorted({n for n in net_of_wire.values() if n})
    assertions = 0

    report.counts = {
        "files_inspected": max(files, 1),
        "easyeda_records_parsed": len(records),
        "components_inspected": len(components),
        "symbol_pins_resolved": 0,
        "nets_inspected": len(named_nets),
        "assertions_executed": 0,
    }
    if not components:
        report.unresolved = True
        errors.append("parsed 0 designated components; failing closed")
        return report
    if not named_nets:
        report.unresolved = True
        errors.append("parsed 0 named nets; failing closed")
        return report

    u1 = components.get(U1_DESIGNATOR)
    if u1 is None:
        report.unresolved = True
        errors.append(f"{U1_DESIGNATOR} missing; pin-role resolution unavailable")
        report.counts["assertions_executed"] = 1
        return report

    u1_hits = _pin_hits(u1, TPS259474L_PINS, verts)
    report.u1_pins = u1_hits
    report.counts["symbol_pins_resolved"] = len(u1_hits)
    if len(u1_hits) != 10:
        report.unresolved = True
        errors.append(f"U1 symbol pins resolved {len(u1_hits)}/10")
        return report

    proof_ok = 0
    for number in TRANSFORM_PROOF_PINS:
        hit = u1_hits[number]
        expected = G2_2_EXPECTED_NETS[number]
        if expected and expected in hit.nets and len(hit.nets) == 1:
            proof_ok += 1
        elif expected and expected in hit.nets:
            proof_ok += 1
            warnings.append(f"U1-PWR1.{number} lands on multiple nets {hit.nets}")
    report.transform = {
        "u1_xy": [u1["x"], u1["y"]],
        "rotation": u1["rotation"],
        "isMirror": u1["isMirror"],
        "proof_pins_ok": proof_ok,
        "proof_pins_required": TRANSFORM_PROOF_MIN,
        "method": report.reconstruction,
    }
    assertions += 1
    if proof_ok < TRANSFORM_PROOF_MIN:
        report.unresolved = True
        errors.append(
            f"U1 transform UNRESOLVED: only {proof_ok}/{len(TRANSFORM_PROOF_PINS)} "
            "proof pins landed on expected nets; refusing coincidence PASS"
        )
        report.counts["assertions_executed"] = assertions
        return report

    pin9 = u1_hits["9"]
    assertions += 1
    if pin9.name != "ILM":
        errors.append(f"U1-PWR1 pin 9 role is {pin9.name!r}, expected ILM")
    assertions += 1
    pin9_nets = pin9.nets
    if ILIM_NET not in pin9_nets or len(pin9_nets) != 1:
        errors.append(
            f"net(U1-PWR1.9) == {pin9_nets or ['OPEN']}, expected [{ILIM_NET}]"
        )
    for net in pin9_nets:
        assertions += 1
        if is_forbidden_usb_diff(net):
            errors.append(f"U1-PWR1.9 belongs to forbidden USB differential net {net}")

    r1 = components.get(R1_DESIGNATOR)
    if r1 is None:
        errors.append(f"{R1_DESIGNATOR} missing; R1 electrical value cannot be resolved")
        r1_info = {}
        r1_hits: dict[str, PinHit] = {}
    else:
        r1_info = resolve_r1(r1)
        r1_hits = _pin_hits(r1, RESISTOR_0402_PINS, verts)
        r1_info["pins"] = {
            number: {"xy": list(hit.xy), "nets": hit.nets} for number, hit in r1_hits.items()
        }
        assertions += 1
        if r1_info.get("electrical_ohms") is None:
            errors.append("R1 electrical value cannot be resolved from Device/MPN/Name/Value")
        elif expect_r1_ohms is not None and r1_info["electrical_ohms"] != expect_r1_ohms:
            errors.append(
                f"R1 electrical value {r1_info['electrical_ohms']} Ω, expected {expect_r1_ohms}"
            )
        if r1_info.get("electrical_ohms") == 10000:
            errors.append("R1 electrical value resolved to 10 kΩ — partId must not win")
        if r1_info.get("metadata_mismatch"):
            warnings.append(
                "METADATA_MISMATCH: partId text disagrees with bound device/value"
            )
        if r1_info.get("electrical_ohms") == 1240:
            if r1_info.get("mpn") and r1_info["mpn"] != EXPECTED_R1_MPN:
                warnings.append(f"R1 MPN {r1_info['mpn']} (electrical 1.24 kΩ still holds)")
    report.r1 = r1_info

    ilim_wires = _nets_named(net_of_wire, segs, ILIM_NET)
    ilim_members: list[str] = []
    if "9" in u1_hits and ILIM_NET in u1_hits["9"].nets:
        ilim_members.append("U1-PWR1.9")
    r1_ilim_pin = None
    for number, hit in r1_hits.items():
        if ILIM_NET in hit.nets:
            ilim_members.append(f"R1-PWR1.{number}")
            r1_ilim_pin = number
    report.ilim_members = ilim_members
    assertions += 1
    if "U1-PWR1.9" not in ilim_members:
        errors.append(f"{ILIM_NET} does not contain U1-PWR1.9")
    assertions += 1
    if r1_ilim_pin is None:
        errors.append(f"{ILIM_NET} does not contain R1-PWR1.<ILIM terminal>")
    assertions += 1
    if len(ilim_members) < 2:
        errors.append(f"{ILIM_NET} is a one-endpoint orphan: members={ilim_members}")

    rusb = components.get(RUSB_DP_DESIGNATOR)
    u20 = components.get(U20_DESIGNATOR)
    dp_has_rusb = False
    dp_has_hub = False
    if rusb is not None:
        rusb_hits = _pin_hits(rusb, RESISTOR_0402_PINS, verts)
        dp_has_rusb = any(DP_NET in hit.nets for hit in rusb_hits.values())
    dp_wires = _nets_named(net_of_wire, segs, DP_NET)
    hub_verts = []
    if u20 is not None:
        ux, uy = u20["x"], u20["y"]
        for wire_id in dp_wires:
            for sx, sy, ex, ey in segs.get(wire_id, []):
                for x, y in ((sx, sy), (ex, ey)):
                    if abs(x - ux) <= 400 and abs(y - uy) <= 400:
                        dp_has_hub = True
                        hub_verts.append((x, y))
    pin9_on_dp = DP_NET in pin9_nets
    assertions += 1
    if not dp_has_rusb:
        errors.append(f"{DP_NET} lost RUSB_DP-PWR1 — D+ continuity broken")
    assertions += 1
    if u20 is not None and not dp_has_hub:
        errors.append(f"{DP_NET} has no remaining wire near {U20_DESIGNATOR}")
    assertions += 1
    if pin9_on_dp:
        errors.append(f"{DP_NET} still contains U1-PWR1.9")
    report.dp_continuity = {
        "rusb_dp_on_usb_dp_up": dp_has_rusb,
        "hub_island_usb_dp_up": dp_has_hub,
        "u1_pin9_on_usb_dp_up": pin9_on_dp,
        "usb_dp_up_wire_count": len(dp_wires),
    }

    report.counts["assertions_executed"] = assertions
    if any(v == 0 for k, v in report.counts.items() if k != "files_inspected"):
        report.unresolved = True
        errors.append(f"vacuous counts: {report.counts}")
    report.ok = (not errors) and (not report.unresolved)
    return report


def write_audit_markdown(
    path: Path,
    *,
    pre: IlmReport | None,
    post: IlmReport,
) -> None:
    lines = [
        "# U1-PWR1 G2.2 pin differential",
        "",
        "Scope: TPS259474L ten-pin audit of the G2.2 hub candidate.",
        "Canonical project `64325d0e55e0435abd018defb0089a9b` is **CLEAN** for this defect and was not mutated.",
        "",
        "Reconstruction: symbol offsets for `TPS259474LRPWR.1` plus the instance transform, ",
        "validated against a known-good majority of U1 pins at tolerance 0. ",
        "A graph with `bound_pin_count=0` cannot pass this gate.",
        "",
        "| Pin | Datasheet/symbol role | Canonical net | G2.2 pre-fix net | G2.2 post-fix net | Classification | Evidence |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for number, spec in TPS259474L_PINS.items():
        canonical = CANONICAL_NETS[number]
        pre_nets = (pre.u1_pins[number].nets if pre and number in pre.u1_pins else [])
        post_nets = post.u1_pins[number].nets if number in post.u1_pins else []
        pre_net = pre_nets[0] if len(pre_nets) == 1 else ("OPEN" if not pre_nets else ",".join(pre_nets))
        post_net = post_nets[0] if len(post_nets) == 1 else ("OPEN" if not post_nets else ",".join(post_nets))
        classification = classify_pin(
            number,
            canonical,
            pre_nets[0] if len(pre_nets) == 1 else (None if not pre_nets else "MULTI"),
            post_nets[0] if len(post_nets) == 1 else (None if not post_nets else "MULTI"),
        )
        if number == "5" and canonical == "5V_USB_FILTERED" and post_net == "5V_USB":
            classification = "INTENDED_RENAME"
        evidence = f"abs {post.u1_pins[number].xy}" if number in post.u1_pins else "unresolved"
        if classification == "INTENDED_RENAME":
            evidence += "; hub-era 5V_USB_FILTERED → 5V_USB after F1 left the trunk"
        if classification == "DEFECT_FIXED":
            evidence += "; ILM restored onto USB_EFUSE_ILIM; USB_DP_UP no longer owns pin 9"
        lines.append(
            f"| {number} | {spec['name']} | {canonical or 'OPEN'} | {pre_net} | {post_net} | {classification} | {evidence} |"
        )
    lines += [
        "",
        "## R1-PWR1",
        "",
        f"- electrical/device identity: {post.r1.get('electrical_ohms')} Ω / "
        f"{post.r1.get('mpn')} / {post.r1.get('supplier')} / device `{post.r1.get('device')}`",
        f"- display Name: `{post.r1.get('name')}`",
        f"- legacy partId: `{post.r1.get('partId')}`",
        f"- metadata mismatch: {post.r1.get('metadata_mismatch')}",
        "",
        "Authoritative fields: Manufacturer Part, Name, Device, Supplier Part. "
        "Do not infer the ohmic value from `partId`.",
        "",
        "## Checker counts",
        "",
        "```",
        json.dumps(post.counts, indent=2),
        "```",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fixture_v3(
    *,
    ilm_on_dp: bool,
    r1_partid_10k: bool = True,
    r1_mpn: str = EXPECTED_R1_MPN,
    r1_name: str = "1.24k",
    include_dplus: bool = True,
) -> str:
    """Minimal V3 sheet exercising the ILM / R1 assertions."""

    def rec(typ: str, id_: str, payload: dict, ticket: int) -> str:
        header = json.dumps({"type": typ, "ticket": ticket, "id": id_}, separators=(",", ":"))
        return f"{header}||{json.dumps(payload, separators=(',', ':'))}|"

    rows: list[str] = []
    ticket = 1

    def add(typ, id_, payload):
        nonlocal ticket
        rows.append(rec(typ, id_, payload, ticket))
        ticket += 1

    add("COMPONENT", "eU1", {"partId": "TPS259474LRPWR.1", "x": 690, "y": -4110, "rotation": 180, "isMirror": False})
    add("ATTR", "aU1d", {"parentId": "eU1", "key": "Designator", "value": U1_DESIGNATOR})
    add("COMPONENT", "eR1", {"partId": "RC0402FR-0710KL.1" if r1_partid_10k else "RNCF0402BTC1K24.1", "x": 365, "y": -4420, "rotation": 0, "isMirror": False})
    add("ATTR", "aR1d", {"parentId": "eR1", "key": "Designator", "value": R1_DESIGNATOR})
    add("ATTR", "aR1m", {"parentId": "eR1", "key": "Manufacturer Part", "value": r1_mpn})
    add("ATTR", "aR1n", {"parentId": "eR1", "key": "Name", "value": r1_name})
    add("ATTR", "aR1v", {"parentId": "eR1", "key": "Value", "value": ""})
    add("ATTR", "aR1dev", {"parentId": "eR1", "key": "Device", "value": EXPECTED_R1_DEVICE})
    add("ATTR", "aR1s", {"parentId": "eR1", "key": "Supplier Part", "value": EXPECTED_R1_LCSC})
    add("COMPONENT", "eRusb", {"partId": "RC0402FR-070RL.1", "x": 555, "y": -4165, "rotation": 0, "isMirror": False})
    add("ATTR", "aRusb", {"parentId": "eRusb", "key": "Designator", "value": RUSB_DP_DESIGNATOR})
    add("COMPONENT", "eU20", {"partId": "USB2422T-I/MJ.1", "x": 400, "y": -800, "rotation": 0, "isMirror": False})
    add("ATTR", "aU20", {"parentId": "eU20", "key": "Designator", "value": U20_DESIGNATOR})
    add("COMPONENT", "eU17", {"partId": "TPS62913RPUR.1", "x": 200, "y": -3000, "rotation": 0, "isMirror": False})
    add("ATTR", "aU17", {"parentId": "eU17", "key": "Designator", "value": "U17-PWR2"})

    def wire(wid: str, net: str, segments: list[tuple[int, int, int, int]]):
        add("WIRE", wid, {"zIndex": 1, "locked": False})
        add("ATTR", f"n{wid}", {"parentId": wid, "key": "NET", "value": net})
        for i, (sx, sy, ex, ey) in enumerate(segments):
            add("LINE", f"l{wid}{i}", {"startX": sx, "startY": sy, "endX": ex, "endY": ey, "lineGroup": wid})

    # Proof nets at the seven non-DUT pins (tol 0 vertices).
    add("WIRE", "wEN", {"zIndex": 1, "locked": False})
    add("ATTR", "nEN", {"parentId": "wEN", "key": "NET", "value": "USB_EFUSE_EN"})
    add("LINE", "lEN", {"startX": 775, "startY": -4110, "endX": 795, "endY": -4110, "lineGroup": "wEN"})
    add("WIRE", "wOV", {"zIndex": 1, "locked": False})
    add("ATTR", "nOV", {"parentId": "wOV", "key": "NET", "value": "USB_EFUSE_OVLO"})
    add("LINE", "lOV", {"startX": 775, "startY": -4130, "endX": 795, "endY": -4130, "lineGroup": "wOV"})
    add("WIRE", "wPGTH", {"zIndex": 1, "locked": False})
    add("ATTR", "nPGTH", {"parentId": "wPGTH", "key": "NET", "value": "USB_EFUSE_PGTH"})
    add("LINE", "lPGTH", {"startX": 600, "startY": -4110, "endX": 580, "endY": -4110, "lineGroup": "wPGTH"})
    add("WIRE", "wIN", {"zIndex": 1, "locked": False})
    add("ATTR", "nIN", {"parentId": "wIN", "key": "NET", "value": "5V_USB"})
    add("LINE", "lIN", {"startX": 775, "startY": -4090, "endX": 795, "endY": -4090, "lineGroup": "wIN"})
    add("WIRE", "wOUT", {"zIndex": 1, "locked": False})
    add("ATTR", "nOUT", {"parentId": "wOUT", "key": "NET", "value": "5V_PROTECTED"})
    add("LINE", "lOUT", {"startX": 600, "startY": -4090, "endX": 580, "endY": -4090, "lineGroup": "wOUT"})
    add("WIRE", "wDV", {"zIndex": 1, "locked": False})
    add("ATTR", "nDV", {"parentId": "wDV", "key": "NET", "value": "USB_EFUSE_DVDT"})
    add("LINE", "lDV", {"startX": 705, "startY": -4165, "endX": 705, "endY": -4185, "lineGroup": "wDV"})
    add("WIRE", "wGND", {"zIndex": 1, "locked": False})
    add("ATTR", "nGND", {"parentId": "wGND", "key": "NET", "value": "GND"})
    add("LINE", "lGND", {"startX": 665, "startY": -4165, "endX": 665, "endY": -4185, "lineGroup": "wGND"})
    add("WIRE", "wPG", {"zIndex": 1, "locked": False})
    add("ATTR", "nPG", {"parentId": "wPG", "key": "NET", "value": "PWR_ENTRY_PG_RT_IOMUX_TBD"})
    add("LINE", "lPG", {"startX": 600, "startY": -4130, "endX": 580, "endY": -4130, "lineGroup": "wPG"})

    if ilm_on_dp:
        wire("w154290", DP_NET, [(575, -4165, 600, -4165), (600, -4165, 625, -4165), (625, -4165, 640, -4165)])
        wire("w1000", ILIM_NET, [(325, -4420, 345, -4420)])
    else:
        wire("wILM", ILIM_NET, [(345, -4420, 345, -4300), (345, -4300, 625, -4300), (625, -4300, 625, -4165)])
        wire("wDP", DP_NET, [(575, -4165, 595, -4165)])
    if include_dplus:
        wire("wHUBDP", DP_NET, [(570, -810, 640, -810)])
    return "\n".join(rows) + "\n"
