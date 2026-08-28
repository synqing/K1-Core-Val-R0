#!/usr/bin/env python3
"""DRAWING oracle for the K1 single-sheet EasyEDA schematic.

WHAT THIS IS, AND WHAT IT IS NOT
================================
This measures ONE property: **do the wires visually meet the pins they are
labelled for, in the drawing?**

It is NOT a netlist oracle. It cannot tell you what EasyEDA will export as the
netlist, and it must never be quoted as though it could. The disproof is on the
record: `U9-ESP` was displaced by a rejected-but-never-rolled-back transaction
at `474325:91295516`, and Captain's DRC — run 46 seconds after the accepted
repair that followed, with the displacement already present — reported **19**
floating pins on `U9-ESP`, not the 41 the geometry sees. EasyEDA's netlist does
not depend on exact endpoint coincidence the way geometry does.

The property is still real and still required. `schematic/SINGLE-SHEET-CONTRACT.md`
demands visible wiring — *"A page of hundreds of floating components joined only
by global names is not a schematic"* — so a sheet whose wires miss their pins
fails the contract regardless of what the netlister salvages. That failure is
invisible to every other check in this repo, which is why this oracle exists.

Violation names are therefore DRAWING language, not electrical language:

    net_labels_meeting_fewer_than_two_pins   (not "nets reaching...")
    wires_not_meeting_any_pin                (not "touching no pin")
    pins_met_by_multiple_net_labels
    off_sheet_wires
    components_displaced_from_their_wiring

There is also no geometric graph to traverse here: of 1359 wire endpoints only
9 are shared, so all 675 wires are isolated labelled stubs. Union-find over
shared endpoints has almost nothing to merge. That is the construction method
(`schematic/wire_led_efuse_support.py:37-48`), not a defect — see the
fragmentation note below.

WHAT THIS MEASURES, AND WHY IT IS NOT A FRAGMENTATION COUNTER
=============================================================
An earlier version of this file counted, for each named net, how many disjoint
geometric islands carried that name. That was the WRONG PROPERTY, and it is
worth recording why, because the number it produced looked alarming and meant
almost nothing.

On the frozen denominator it reported 142 of 143 nets "fragmented", GND at 186
islands, 3V3 at 90 — islands == wire count for essentially every net. That is
not 142 defects. It is the sheet's CONSTRUCTION METHOD. See
`schematic/wire_led_efuse_support.py:37-48`: for each pin it emits a 20-unit
stub outward from that pin and hangs a `NET` ATTR on it. Pins share a net by
sharing a NAME, never by touching. A checker that flags this goes RED on
142/143 — as useless as one that always passes.

It would also have been wrong on doctrine. `schematic/SINGLE-SHEET-CONTRACT.md`
says, verbatim: "Long global rails and major shared buses may use labelled
trunks." GND and 3V3 are exactly that. Flagging them would contradict the
contract the sheet is built to.

So this oracle measures the property that actually carries the electrical
claim, and that K1E-016 is about — "a named one-ended stub is not an electrical
connection" — the same thing EasyEDA's own DRC reports as *"The wire X is a
single network connected to only one component pin."*

    For each named net: HOW MANY DISTINCT COMPONENT PINS does it actually touch?

Not how many wires carry the name. Not how many islands. Pins.

VIOLATION CLASSES
-----------------
  1. net_labels_meeting_fewer_than_two_pins  a label meeting <2 real pins (K1E-016)
  2. wires_not_meeting_any_pin               a labelled stub landing on no pin
  3. pins_met_by_multiple_net_labels         one pin met by two names (K1E-018)
  4. off_sheet_wires                         a wire with a negative coordinate
  5. components_displaced_from_their_wiring   pin cloud offset from its own anchor

Class 4 is the only one carrying NO registration or tolerance caveat: a negative
coordinate is off the page, and no fit recovers it. Class 5 is REPORTED, never
cancelled — see the note on the refused DRC-anchored fit.

Geometric fragmentation is still COMPUTED and REPORTED — it is useful context
for reading the sheet — but it is a STATISTIC, never a violation. Likewise the
free far-end of every stub: that is the construction method, not a dangling
defect, and counting it as one was the same mistake in a second place.

THE COORDINATE TRANSFORM — the load-bearing step, stated exactly
----------------------------------------------------------------
Pin coordinates are NOT in the schematic source; they live in the symbol
library and are read back through `list_schematic_component_pins`. Everything
this oracle concludes rests on mapping those into source coordinates, so the
transform is written out in full rather than left implicit.

    THE TRANSFORM IS:   (x, y)  ->  (x, -y)

That is the whole of it. In particular:

  * `list_schematic_component_pins` returns ABSOLUTE PAGE COORDINATES in a
    y-DOWN screen frame. It does NOT return offsets relative to the component.
  * Component `(x, y, rotation)` is therefore NOT composed, and must not be.
    Rotation is ALREADY BAKED IN by the host. Evidence: component `e3673` has
    `rotation=90` and its first pins read (2010, 4040), (2020, 4040) — absolute
    page positions, not anchor-relative offsets awaiting a rotation. Composing
    rotation here would move every pin on every rotated part off its wire.
  * Only `y` flips. `x` is identical in both frames.

This was established DIFFERENTIALLY, not assumed. Against the 881-pin harvest
and the 1359 wire endpoints of the frozen denominator:

    identity      (x,  y)   ->    0/881   0.0%
    NEGATE Y      (x, -y)   ->  654/881  74.2%   <- the transform used
    negate X     (-x,  y)   ->    0/881   0.0%
    negate both  (-x, -y)   ->    0/881   0.0%
    swap          (y,  x)   ->    0/881   0.0%
    swap+negate  (-y,  x)   ->    2/881   0.2%

A wrong transform does not degrade gracefully here — it lands ~0%. The 74.2%
is not a partial match to be explained away; every other candidate is refuted.
(Anyone re-deriving this with the identity transform gets 0% and will conclude
the frames are unrelated. They are not. Negate y.)

`pin_landing_rate` is reported alongside the verdict for exactly this reason:
if it ever collapses, the transform — not the board — is what broke. The
battery carries a `rotated-component` case that goes RED if rotation is ever
composed into the transform.

PINS ARE KEYED BY PRIMITIVE ID, NOT DESIGNATOR
----------------------------------------------
A multi-part component is several COMPONENT records sharing one Designator.
Keying pin read-backs by designator makes the parts collide and silently drops
all but the last. Measured: `U6-RTC` is a two-part MIMXRT1062, `e3295` and
`e3673`, 98 pins each; designator-keyed loading held 783 of 881 pins — the
missing 98 being exactly one part. Since the RT1062 is where most signals
terminate, that gap could manufacture false "net reaches fewer than two pins"
findings across the whole sheet. Pin data is keyed by `componentPrimitiveId`;
designators are for display only.

Coverage is therefore never assumed. A wire that touches no KNOWN pin is
attributed to its nearest component anchor:

  * nearest component's pins ARE measured  -> VIOLATION (it really touches nothing)
  * nearest component's pins are NOT measured -> UNKNOWN, and the oracle ABSTAINS

Nets carrying an abstained wire are reported as UNKNOWN, never as pass or fail.
Partial coverage stated honestly beats a confident number over an unknown
denominator. Coverage is reported as a fraction of designators AND of component
PARTS, because a multi-part component (one designator, several COMPONENT
records) yields one read-back per part but is keyed by designator — so the last
part written wins and the rest vanish silently.

WHAT THIS ORACLE CANNOT SEE
---------------------------
It can only measure nets that EXIST. A net that was never drawn is invisible to
it: on the real sheet `NFC_RFO1` exists, while `NFC_RFO2`, `NFC_RFI1` and
`NFC_RFI2` do not exist at all. Completeness against a design authority (BOM,
block spec, reference schematic) is a DIFFERENT checker with an external
denominator. Claiming this one covers that would be a false denominator.

FAULT BATTERY -- `--self-test`. Includes cases expected to be RED, cases
expected to ABSTAIN, and cases expected to FAIL CLOSED, and asserts each
(K1E-054, K1E-055). Note the `disjoint-same-name` case expects GREEN: it is the
positive control proving this oracle does NOT flag fragmentation.

EXIT CODES
  0  GREEN       -- measured a real sheet, no binding violations
  1  RED         -- measured a real sheet, violations found
  2  FAIL-CLOSED -- could not measure the property at all; no verdict possible

READ-ONLY. Never touches EasyEDA, a bridge, or a live session.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import Counter, defaultdict

import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
from easyeda_source_format import (  # V2/V3 serialisation, format-agnostic
    SourceFormatError,
    parse_records_any_format,
)


SCHEMA_VERSION = 2

# Pin read-backs report y in screen space, negated relative to the source records.
PIN_Y_SIGN = -1


class FailClosed(RuntimeError):
    """Raised when the oracle cannot honestly reach any verdict at all."""


# --------------------------------------------------------------------------
# SNAP TOLERANCE — measured, not chosen
# --------------------------------------------------------------------------
# A tolerance changes the findings, so it cannot be picked by taste. Measured on
# the frozen denominator, pin-to-nearest-wire-endpoint distance is QUANTISED, not
# noisy: 654 pins at 0, 15 at 5, 81 at 10, 47 at 20, 84 beyond. There is no
# continuum, so there is no "grid noise" band to absorb.
#
# All 15 pins at distance 5 belong to ONE component, U9-ESP, which has ZERO pins
# at distance 0. That is a systematic drawing offset on one part, not measurement
# error — exactly the defect an oracle should report rather than snap away.
#
# The decisive test: bind at tol=5 and check the wire's NET name against the
# pin's NAME. It produces 0 correct bindings and 14 WRONG ones — GND onto EN,
# 3V3 onto IO4, I2C_SDA onto TXD0, ESP_EN onto IO5. A tolerance that
# manufactures 14 false connections is not a tolerance; it is a net-swap.
#
# Pin pitch on this sheet is 10 units, so tol >= 5 is exactly half-pitch: a point
# at distance 5 is EQUIDISTANT between two adjacent pins and the binding is
# ambiguous by construction. The oracle refuses such a tolerance rather than
# silently resolving the tie.
DEFAULT_SNAP_TOLERANCE = 0
SENSITIVITY_TOLERANCES = (0, 5, 10)

# How far a component's pin cloud may sit from its own SOURCE anchor before the
# component is reported as displaced. 214 of 229 components land within 10.
DISPLACEMENT_TOLERANCE = 10

# WHY A DRC-ANCHORED PER-COMPONENT FIT IS REFUSED
# -----------------------------------------------
# It was proposed that this oracle fit a per-component translation, constrained to
# reproduce EasyEDA's DRC verdict on every pin (reported: exact fit on 221/228).
# That is declined as the measurement path, for three reasons, and the residual
# offsets are REPORTED instead as `components_displaced_from_their_wiring`.
#
# 1. It is self-defeating against this file's own contract. The oracle exists
#    because the netlist and the drawing disagree. Fitting the geometry until it
#    reproduces the netlist verdict destroys exactly that distinction: after the
#    fit, "the wires do not meet the pins" becomes unreportable by construction.
#
# 2. It fits the model to the answer. Two free parameters per component, chosen to
#    maximise agreement with the target verdict, will agree with that verdict —
#    221/228 is what the method produces, not evidence that it is right. It also
#    forfeits the DRC as an INDEPENDENT witness, which is its more valuable role.
#
# 3. Measured counterexample. `C10-PWR2` was cited as needing (0,-5). Its pin cloud
#    sits at delta (0.0, 0.0) from its own source anchor — the pin data is correct
#    and the WIRE is 5 units off. Applying that offset would move good pin data onto
#    a badly drawn wire and erase the defect. `U9-ESP` does show (5,-20), matching a
#    displacement from a rejected-but-never-rolled-back transaction — which is a real
#    uncorrected defect, and cancelling it would blind the oracle to precisely the
#    event class the mutation gate exists to catch.


def chebyshev(a, b) -> int:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def min_pin_pitch(pin_points: list[tuple[int, int]]) -> int:
    """Smallest spacing between two pins of the same component, per axis."""
    pitches = set()
    for i, p in enumerate(pin_points):
        for q in pin_points[i + 1 : i + 12]:
            if p[0] == q[0] and p[1] != q[1]:
                pitches.add(abs(p[1] - q[1]))
            elif p[1] == q[1] and p[0] != q[0]:
                pitches.add(abs(p[0] - q[0]))
    return min(pitches) if pitches else 0


# --------------------------------------------------------------------------
# source parsing (record shapes decoded in harness/extract_frozen_denominator.py)
# --------------------------------------------------------------------------

def parse_records(text: str) -> list[list]:
    """Parse a document source into V2-shaped rows, whichever grammar (V2 tagged
    arrays or V3 typed header||payload records) the snapshot is actually in.

    ONE internal representation. The V3 named-field grammar is normalised into
    the V2 positional rows at this boundary — including the y-axis negation, see
    `easyeda_source_format` — so nothing below this line forks per host version.

    Any refusal from the parse layer (unrecognised serialisation, record-shape
    drift, a truncated record) is converted to FailClosed here, so the oracle's
    contract holds: it either measures the property or it declines. It never
    reports a verdict over a document it could not fully read.
    """
    try:
        return parse_records_any_format(text, tool="check_schematic_connectivity.parse_records")
    except SourceFormatError as exc:
        raise FailClosed(
            f"parsed zero source records — the snapshot could not be read at all: {exc}"
        ) from exc
    except (TypeError, ValueError) as exc:
        # Backstop. The shape gate in easyeda_source_format is the real guard and
        # it is proven by mutation (neuter it and four battery cases go RED). This
        # catches an unforeseen drift the gate does not enumerate, so the CLI still
        # exits FAIL-CLOSED(2) instead of dying with a traceback — a crash is not a
        # verdict, but it is also not a refusal a caller can act on.
        raise FailClosed(
            f"parsed zero source records — the snapshot could not be read at all: "
            f"unhandled {exc.__class__.__name__} while normalising records ({exc}). "
            f"Suspect UNENUMERATED RECORD-SHAPE DRIFT in the host serialisation."
        ) from exc


def extract_topology(records: list[list]) -> dict:
    wires: dict[str, list[list[int]]] = {}
    components: dict[str, dict] = {}
    for rec in records:
        if rec[0] == "WIRE" and len(rec) > 2 and isinstance(rec[2], list):
            segs = [
                [int(s[0]), int(s[1]), int(s[2]), int(s[3])]
                for s in rec[2]
                if isinstance(s, list) and len(s) >= 4
            ]
            if segs:
                wires[rec[1]] = segs
        elif rec[0] == "COMPONENT" and len(rec) > 4:
            components[rec[1]] = {"primitive_id": rec[1], "x": rec[3], "y": rec[4], "attrs": {}}

    wire_net: dict[str, str] = {}
    for rec in records:
        if rec[0] != "ATTR" or len(rec) < 5:
            continue
        parent, key, value = rec[2], rec[3], rec[4]
        if parent in wires and key == "NET" and value:
            wire_net[parent] = str(value)
        elif parent in components:
            components[parent]["attrs"][key] = value

    parts_of_designator: dict[str, list[dict]] = defaultdict(list)
    for comp in components.values():
        ref = comp["attrs"].get("Designator")
        if ref:
            comp["designator"] = str(ref)
            parts_of_designator[str(ref)].append(comp)
    return {
        "wires": wires,
        "wire_net": wire_net,
        "components": components,
        "parts_of_designator": dict(parts_of_designator),
    }


# --------------------------------------------------------------------------
# pin read-back merging
# --------------------------------------------------------------------------

def load_pins(paths: list[pathlib.Path]) -> dict:
    """Merge MCP pin read-backs, keyed by componentPrimitiveId.

    Keying by designator collapses the parts of a multi-part component — see the
    module docstring. `designator_collisions` records every case where two
    records shared a tag, so the collision is reported rather than silently
    resolved in favour of whichever was written last.
    """
    by_pid: dict[str, dict] = {}
    designator_of_pid: dict[str, str] = {}
    tag_pids: dict[str, set] = defaultdict(set)
    files_parsed = records_seen = records_failed = records_no_pid = 0
    for path in paths:
        try:
            payload = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, list):
            continue
        files_parsed += 1
        for item in payload:
            if not isinstance(item, dict) or "tag" not in item:
                continue
            records_seen += 1
            result = item.get("result")
            if not item.get("ok") or not isinstance(result, dict) or not isinstance(result.get("pins"), list):
                records_failed += 1
                continue
            pid = result.get("componentPrimitiveId")
            if not pid:
                records_no_pid += 1
                continue
            tag = str(item["tag"])
            tag_pids[tag].add(pid)
            designator_of_pid[pid] = tag
            by_pid[pid] = {
                "component_primitive_id": pid,
                "designator": tag,
                "pins": [
                    {
                        "number": str(p.get("pinNumber")),
                        # pinName is what the wrong-pin audit compares a net name
                        # against — without it a snap cannot be shown to be wrong.
                        "name": str(p.get("pinName") or p.get("pinNumber")),
                        # THE TRANSFORM: absolute page coords, y-down -> source frame.
                        # x is unchanged; rotation is already baked in by the host
                        # and must NOT be composed here. See module docstring.
                        "x": int(p["x"]),
                        "y": PIN_Y_SIGN * int(p["y"]),
                    }
                    for p in result["pins"]
                    if isinstance(p, dict) and p.get("x") is not None and p.get("y") is not None
                ],
                "source_file": path.name,
            }
    collisions = {tag: sorted(pids) for tag, pids in sorted(tag_pids.items()) if len(pids) > 1}
    return {
        "by_pid": by_pid,
        "designator_of_pid": designator_of_pid,
        "designators": set(designator_of_pid.values()),
        "designator_collisions": collisions,
        "files_parsed": files_parsed,
        "records_seen": records_seen,
        "records_failed": records_failed,
        "records_without_primitive_id": records_no_pid,
    }


# --------------------------------------------------------------------------
# geometric fragmentation — STATISTIC ONLY, never a violation
# --------------------------------------------------------------------------

class DSU:
    def __init__(self) -> None:
        self.parent: dict = {}

    def find(self, node):
        self.parent.setdefault(node, node)
        root = node
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[node] != root:
            self.parent[node], node = root, self.parent[node]
        return root

    def union(self, a, b) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def _on_interior(point, seg) -> bool:
    px, py = point
    x1, y1, x2, y2 = seg
    if (px, py) in ((x1, y1), (x2, y2)):
        return False
    if (x2 - x1) * (py - y1) != (y2 - y1) * (px - x1):
        return False
    return min(x1, x2) <= px <= max(x1, x2) and min(y1, y2) <= py <= max(y1, y2)


def island_stats(wires: dict[str, list[list[int]]], wire_net: dict[str, str]) -> dict:
    """How many disjoint geometric islands carry each name. Context, not a verdict."""
    dsu = DSU()
    segments = []
    endpoints = set()
    for wire_id, segs in wires.items():
        for x1, y1, x2, y2 in segs:
            dsu.union((x1, y1), (x2, y2))
            segments.append((x1, y1, x2, y2))
            endpoints.add((x1, y1))
            endpoints.add((x2, y2))
    t_junctions = 0
    for point in endpoints:
        for seg in segments:
            if _on_interior(point, seg):
                dsu.union(point, (seg[0], seg[1]))
                t_junctions += 1
    per_net: dict[str, int] = {}
    for wire_id, segs in wires.items():
        net = wire_net.get(wire_id)
        if not net:
            continue
        per_net.setdefault(net, set())
    roots_by_net: dict[str, set] = defaultdict(set)
    for wire_id, segs in wires.items():
        net = wire_net.get(wire_id)
        if not net:
            continue
        for x1, y1, x2, y2 in segs:
            roots_by_net[net].add(dsu.find((x1, y1)))
            roots_by_net[net].add(dsu.find((x2, y2)))
    return {
        "islands_per_net": {net: len(roots) for net, roots in sorted(roots_by_net.items())},
        "total_islands": len({dsu.find(p) for p in endpoints}) if endpoints else 0,
        "t_junction_merges": t_junctions,
        "distinct_endpoints": len(endpoints),
    }


# --------------------------------------------------------------------------
# the actual measurement: label -> pin binding
# --------------------------------------------------------------------------

def bind_wires_to_pins(wires, named, pin_records, tolerance: int) -> dict:
    """Bind each named wire to the pins its endpoints reach, within `tolerance`.

    Returns the bindings plus every binding made at NON-ZERO distance, with the
    wire's net name beside the pin's name so a wrong-pin snap is visible rather
    than absorbed.
    """
    pin_index: dict[tuple[int, int], list[tuple[str, str]]] = defaultdict(list)
    for label, (px, py, pname) in pin_records.items():
        pin_index[(px, py)].append((label, pname))

    wire_pins: dict[str, list[str]] = {}
    inexact: list[dict] = []
    for wire_id, net in named.items():
        points = set()
        for x1, y1, x2, y2 in wires[wire_id]:
            points.add((x1, y1))
            points.add((x2, y2))
        touched: set[str] = set()
        for pt in points:
            if pt in pin_index:
                touched.update(label for label, _ in pin_index[pt])
                continue
            if tolerance <= 0:
                continue
            for (px, py), entries in pin_index.items():
                d = chebyshev((px, py), pt)
                if d == 0 or d > tolerance:
                    continue
                for label, pname in entries:
                    touched.add(label)
                    inexact.append(
                        {
                            "wire_id": wire_id,
                            "net": net,
                            "endpoint": [pt[0], pt[1]],
                            "pin": label,
                            "pin_name": pname,
                            "distance": d,
                            "net_matches_pin_name": bool(pname) and net == pname,
                        }
                    )
        wire_pins[wire_id] = sorted(touched)
    return {"wire_pins": wire_pins, "inexact_bindings": inexact}


def analyse(
    source_text: str,
    pin_paths: list[pathlib.Path],
    snap_tolerance: int = DEFAULT_SNAP_TOLERANCE,
    allow_ambiguous_tolerance: bool = False,
    drc_report: pathlib.Path | None = None,
) -> dict:
    records = parse_records(source_text)
    if not records:
        raise FailClosed("parsed zero source records — refusing to emit a connectivity verdict")

    topo = extract_topology(records)
    wires, wire_net = topo["wires"], topo["wire_net"]
    if not wires:
        raise FailClosed("parsed zero WIRE records — refusing to emit a connectivity verdict")
    named = {w: n for w, n in wire_net.items() if w in wires}
    if not named:
        raise FailClosed("parsed zero named nets — refusing to emit a connectivity verdict")

    pin_data = load_pins(pin_paths)
    if not pin_data["by_pid"]:
        raise FailClosed(
            "no pin geometry loaded — pins are not in the schematic source, so without a pin "
            "read-back the label-to-pin binding cannot be measured at all. Refusing to report "
            "a connectivity verdict rather than passing vacuously."
        )

    pin_at: dict[tuple[int, int], list[str]] = defaultdict(list)
    pins_total = 0
    pins_landed = 0
    pins_not_landed: list[str] = []
    all_endpoints: set[tuple[int, int]] = set()
    for segs in wires.values():
        for x1, y1, x2, y2 in segs:
            all_endpoints.add((x1, y1))
            all_endpoints.add((x2, y2))
    for pid, entry in pin_data["by_pid"].items():
        for pin in entry["pins"]:
            pins_total += 1
            label = f"{entry['designator']}.{pin['number']}"
            point = (pin["x"], pin["y"])
            pin_at[point].append(label)
            if point in all_endpoints:
                pins_landed += 1
            else:
                pins_not_landed.append(label)

    # ---- coverage: which component PARTS do we have pin geometry for? --------
    measured_pids = set(pin_data["by_pid"])
    measured_parts, unmeasured_parts = [], []
    for ref, parts in sorted(topo["parts_of_designator"].items()):
        for part in parts:
            target = measured_parts if part["primitive_id"] in measured_pids else unmeasured_parts
            target.append({"designator": ref, "primitive_id": part["primitive_id"],
                           "x": part["x"], "y": part["y"]})
    designators_without_pin_data = sorted(
        set(topo["parts_of_designator"]) - pin_data["designators"]
    )

    def nearest(point, candidates):
        best = None
        for cand in candidates:
            d = abs(cand["x"] - point[0]) + abs(cand["y"] - point[1])
            if best is None or d < best[0]:
                best = (d, cand)
        return best

    # ---- snap tolerance: guarded, and its sensitivity reported --------------
    pin_records: dict[str, tuple[int, int, str]] = {}
    for pid, entry in pin_data["by_pid"].items():
        for pin in entry["pins"]:
            pin_records[f"{entry['designator']}.{pin['number']}"] = (
                pin["x"], pin["y"], pin.get("name") or pin["number"]
            )
    pitch = min_pin_pitch([(x, y) for x, y, _ in pin_records.values()])
    ambiguous_at = pitch / 2 if pitch else 0
    if snap_tolerance and ambiguous_at and snap_tolerance >= ambiguous_at:
        if not allow_ambiguous_tolerance:
            raise FailClosed(
                f"snap tolerance {snap_tolerance} is >= half the measured pin pitch "
                f"({pitch}/2 = {ambiguous_at:g}). At that distance a wire endpoint is "
                f"EQUIDISTANT between two adjacent pins and the binding is ambiguous by "
                f"construction. Measured on this sheet, tol=5 produces 0 correct and 14 "
                f"WRONG-pin bindings (GND onto EN, 3V3 onto IO4, I2C_SDA onto TXD0). "
                f"Refusing rather than silently resolving the tie."
            )

    bound = bind_wires_to_pins(wires, named, pin_records, snap_tolerance)
    wire_pins = bound["wire_pins"]
    inexact_bindings = bound["inexact_bindings"]
    wrong_pin_bindings = [b for b in inexact_bindings if not b["net_matches_pin_name"]]

    # ---- off-sheet wires: the one class with NO registration caveat ---------
    # A negative coordinate is off the page. No tolerance and no registration fit
    # recovers off-sheet geometry, and no netlist should bind through it. Measured:
    # e146347 (NET=BUCK_PG) is the only one of 675, at y=-4535.
    off_sheet: list[dict] = []
    for wire_id, net in sorted(named.items()):
        bad = [s for s in wires[wire_id] if min(s[0], s[2]) < 0 or min(s[1], s[3]) < 0]
        if bad:
            off_sheet.append({"wire_id": wire_id, "net": net, "segments": bad})

    # ---- components displaced from their own wiring ------------------------
    # A per-component offset between the pin cloud and the SOURCE anchor localises a
    # displacement. It is REPORTED, never cancelled — see the header note on why a
    # DRC-anchored per-component fit is refused.
    displaced: list[dict] = []
    for pid, entry in sorted(pin_data["by_pid"].items()):
        comp = topo["components"].get(pid)
        if not comp or not entry["pins"]:
            continue
        xs = [p["x"] for p in entry["pins"]]
        ys = [p["y"] for p in entry["pins"]]
        dx = (min(xs) + max(xs)) / 2 - comp["x"]
        dy = (min(ys) + max(ys)) / 2 - comp["y"]
        if abs(dx) > DISPLACEMENT_TOLERANCE or abs(dy) > DISPLACEMENT_TOLERANCE:
            displaced.append(
                {
                    "designator": entry["designator"],
                    "primitive_id": pid,
                    "source_anchor": [comp["x"], comp["y"]],
                    "pin_bbox_centre": [dx + comp["x"], dy + comp["y"]],
                    "offset": [dx, dy],
                    "pins": len(entry["pins"]),
                }
            )

    # ---- classify every named wire -----------------------------------------
    wires_no_pin_measured: list[dict] = []   # violation: really touches nothing
    wires_no_pin_unmeasured: list[dict] = []  # abstain: could be an unmeasured pin
    for wire_id, net in sorted(named.items()):
        points = set()
        for x1, y1, x2, y2 in wires[wire_id]:
            points.add((x1, y1))
            points.add((x2, y2))
        if wire_pins[wire_id]:
            continue
        near_m = nearest(next(iter(points)), measured_parts) if measured_parts else None
        near_u = nearest(next(iter(points)), unmeasured_parts) if unmeasured_parts else None
        entry = {
            "wire_id": wire_id,
            "net": net,
            "segments": wires[wire_id],
            "nearest_measured": (near_m[1]["designator"] + "/" + near_m[1]["primitive_id"]) if near_m else None,
            "nearest_measured_distance": near_m[0] if near_m else None,
            "nearest_unmeasured": (near_u[1]["designator"] + "/" + near_u[1]["primitive_id"]) if near_u else None,
            "nearest_unmeasured_distance": near_u[0] if near_u else None,
        }
        if near_u is not None and (near_m is None or near_u[0] < near_m[0]):
            wires_no_pin_unmeasured.append(entry)
        else:
            wires_no_pin_measured.append(entry)

    abstained_wire_ids = {e["wire_id"] for e in wires_no_pin_unmeasured}
    violating_wire_ids = {e["wire_id"] for e in wires_no_pin_measured}

    # ---- per-net verdicts ---------------------------------------------------
    net_wires: dict[str, list[str]] = defaultdict(list)
    for wire_id, net in named.items():
        net_wires[net].append(wire_id)

    islands = island_stats(wires, named)

    nets: dict[str, dict] = {}
    for net, wire_ids in sorted(net_wires.items()):
        reached = sorted({p for wid in wire_ids for p in wire_pins[wid]})
        abstained = [w for w in wire_ids if w in abstained_wire_ids]
        floating = [w for w in wire_ids if w in violating_wire_ids]
        if abstained:
            status = "UNKNOWN"
        elif floating or len(reached) < 2:
            status = "RED"
        else:
            status = "GREEN"
        nets[net] = {
            "status": status,
            "wire_count": len(wire_ids),
            "pins_reached": reached,
            "pins_reached_count": len(reached),
            "wires_not_meeting_any_pin": floating,
            "wires_abstained_unmeasured_part": abstained,
            "geometric_islands": islands["islands_per_net"].get(net, 0),
        }

    # ---- K1E-018: one pin claimed by two names ------------------------------
    pin_nets: dict[str, set] = defaultdict(set)
    for wire_id, net in named.items():
        for pin in wire_pins[wire_id]:
            pin_nets[pin].add(net)
    pins_on_multiple_nets = {p: sorted(s) for p, s in sorted(pin_nets.items()) if len(s) > 1}

    below_two = sorted(n for n, v in nets.items() if v["status"] == "RED" and v["pins_reached_count"] < 2)
    unknown_nets = sorted(n for n, v in nets.items() if v["status"] == "UNKNOWN")

    # ---- tolerance sensitivity: show how the findings move -----------------
    sensitivity = []
    for tol in SENSITIVITY_TOLERANCES:
        probe = bind_wires_to_pins(wires, named, pin_records, tol)
        per_net: dict[str, set] = defaultdict(set)
        floating_wires = 0
        for wire_id, net in named.items():
            hits = probe["wire_pins"][wire_id]
            if not hits:
                floating_wires += 1
            per_net[net].update(hits)
        wrong = [b for b in probe["inexact_bindings"] if not b["net_matches_pin_name"]]
        sensitivity.append(
            {
                "tolerance": tol,
                "ambiguous": bool(ambiguous_at) and tol >= ambiguous_at,
                "nets_below_two_pins": sum(1 for v in per_net.values() if len(v) < 2),
                "wires_not_meeting_any_pin": floating_wires,
                "bindings_at_nonzero_distance": len(probe["inexact_bindings"]),
                "wrong_pin_bindings": len(wrong),
            }
        )

    # ---- differential oracle: geometry vs EasyEDA's own DRC -----------------
    differential = None
    if drc_report is not None:
        try:
            drc = json.loads(drc_report.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise FailClosed(f"could not read DRC report {drc_report}: {exc}") from exc
        drc_floating = set(drc.get("items_by_kind", {}).get("floating_pins", []))
        drc_floating |= {w.get("item") for w in drc.get("waived", []) if w.get("kind") == "floating_pins"}
        drc_floating.discard(None)
        if not drc_floating:
            raise FailClosed(
                f"DRC report {drc_report} yielded zero floating pins — refusing to run a "
                "differential against an empty second oracle"
            )
        geometry_bound = {p for hits in wire_pins.values() for p in hits}
        geometry_floating = set(pin_records) - geometry_bound
        differential = {
            "drc_report": str(drc_report),
            "drc_floating_pins": len(drc_floating),
            "geometry_floating_pins": len(geometry_floating),
            "agreed_floating": sorted(drc_floating & geometry_floating),
            "geometry_only": sorted(geometry_floating - drc_floating),
            "drc_only": sorted(drc_floating - geometry_floating),
            "interpretation": {
                "agreed_floating": "both oracles say unconnected — high confidence, actionable",
                "geometry_only": "geometry says unconnected, DRC does not — suspect tolerance, "
                                 "transform, or a DRC older than the dump, in that order",
                "drc_only": "DRC says floating, geometry says bound — suspect the geometry",
            },
        }
        differential["counts"] = {
            "agreed_floating": len(differential["agreed_floating"]),
            "geometry_only": len(differential["geometry_only"]),
            "drc_only": len(differential["drc_only"]),
        }

    counts = {
        "source_records": len(records),
        "component_records": len(topo["components"]),
        "designators": len(topo["parts_of_designator"]),
        "wires": len(wires),
        "named_wires": len(named),
        "named_nets": len(nets),
        "pin_files_parsed": pin_data["files_parsed"],
        "pin_records_seen": pin_data["records_seen"],
        "pin_records_failed": pin_data["records_failed"],
        "pin_records_without_primitive_id": pin_data["records_without_primitive_id"],
        "component_parts_with_pin_data": len(pin_data["by_pid"]),
        "pins_loaded": pins_total,
        "pins_landing_on_wire_geometry": pins_landed,
        "pins_not_landing_on_wire_geometry": pins_total - pins_landed,
        "pin_landing_rate": f"{100.0 * pins_landed / pins_total:.1f}%" if pins_total else "0.0%",
        "wires_bound_to_at_least_one_pin": sum(1 for w in named if wire_pins[w]),
        "wires_touching_no_pin_measured": len(wires_no_pin_measured),
        "wires_abstained_unmeasured_part": len(wires_no_pin_unmeasured),
    }

    # Count only designators that actually exist in the source. A read-back may
    # carry extra tags (the page frame, for one), and counting those would push
    # coverage above 100% and hide a real gap behind a flattering number.
    covered_designators = pin_data["designators"] & set(topo["parts_of_designator"])
    coverage = {
        "designators_with_pin_data": len(covered_designators),
        "designators_total": len(topo["parts_of_designator"]),
        "designator_coverage": (
            f"{len(covered_designators)}/{len(topo['parts_of_designator'])}"
        ),
        "pin_readback_tags_not_in_source": sorted(
            pin_data["designators"] - set(topo["parts_of_designator"])
        ),
        "designators_without_pin_data": designators_without_pin_data,
        "parts_with_pin_data": len(measured_parts),
        "parts_total": len(measured_parts) + len(unmeasured_parts),
        "part_coverage": f"{len(measured_parts)}/{len(measured_parts) + len(unmeasured_parts)}",
        "parts_without_pin_data": unmeasured_parts,
        "designator_collisions_avoided": pin_data["designator_collisions"],
        "pins_not_landing_on_any_wire": sorted(pins_not_landed),
    }

    violations = {
        "net_labels_meeting_fewer_than_two_pins": below_two,
        "wires_not_meeting_any_pin": wires_no_pin_measured,
        "pins_met_by_multiple_net_labels": pins_on_multiple_nets,
        "off_sheet_wires": off_sheet,
        "wrong_pin_bindings": wrong_pin_bindings,
    }
    violation_counts = {
        "net_labels_meeting_fewer_than_two_pins": len(below_two),
        "wires_not_meeting_any_pin": len(wires_no_pin_measured),
        "pins_met_by_multiple_net_labels": len(pins_on_multiple_nets),
        "off_sheet_wires": len(off_sheet),
        "wrong_pin_bindings": len(wrong_pin_bindings),
    }

    statistics = {
        "note": (
            "Geometric fragmentation is REPORTED, never flagged. Every pin gets its own "
            "20-unit labelled stub (schematic/wire_led_efuse_support.py:37-48), so islands "
            "== wire count by construction, and SINGLE-SHEET-CONTRACT.md permits labelled "
            "trunks for long global rails and major shared buses."
        ),
        "total_geometric_islands": islands["total_islands"],
        "t_junction_merges": islands["t_junction_merges"],
        "distinct_wire_endpoints": islands["distinct_endpoints"],
        "nets_spanning_multiple_islands": sum(1 for v in nets.values() if v["geometric_islands"] > 1),
        "most_fragmented": dict(
            sorted(
                ((n, v["geometric_islands"]) for n, v in nets.items()),
                key=lambda kv: -kv[1],
            )[:10]
        ),
    }

    red = any(violation_counts.values())
    return {
        "schema_version": SCHEMA_VERSION,
        "measured_property": "label-to-pin binding (distinct component pins per named net)",
        "counts": counts,
        "pin_coverage": coverage,
        "violation_counts": violation_counts,
        "violations": violations,
        "abstentions": {
            "nets_unknown": unknown_nets,
            "nets_unknown_count": len(unknown_nets),
            "wires_abstained": wires_no_pin_unmeasured,
        },
        "diagnostics": {
            "components_offset_from_their_anchor": displaced,
            "note": (
                "Offset between a component's pin-cloud bbox centre and its own SOURCE anchor. "
                "REPORTED, never cancelled. NOT promoted to a violation: 14 of the 15 hits are "
                "(-20,0) on single-pin test points and connectors, which is SYMBOL ASYMMETRY "
                "(pin length 20), not displacement. Separating the two needs the symbol "
                "definitions, which this oracle does not have. U9-ESP at (5,-20) is the one "
                "distinctive value and matches a known rejected-but-never-rolled-back move."
            ),
        },
        "snap_tolerance": {
            "applied": snap_tolerance,
            "measured_pin_pitch": pitch,
            "ambiguous_at_or_above": ambiguous_at,
            "bindings_at_nonzero_distance": len(inexact_bindings),
            "wrong_pin_bindings": len(wrong_pin_bindings),
            "sensitivity": sensitivity,
            "note": (
                "Pin-to-wire distance on this sheet is QUANTISED (0/5/10/20), not noisy, so "
                "there is no grid-noise band to absorb. tol>=half-pitch is refused as "
                "ambiguous by construction."
            ),
        },
        "drc_differential": differential,
        "statistics": statistics,
        "limitations": [
            "Only nets that EXIST can be measured. A net that was never drawn is invisible "
            "here; completeness against a design authority is a different checker.",
            "Pin geometry comes from on-disk read-backs, not from the schematic source. "
            "Components without pin geometry are abstained on, never passed.",
        ],
        "nets": nets,
        "verdict": "RED" if red else "GREEN",
    }


# --------------------------------------------------------------------------
# fault battery
# --------------------------------------------------------------------------

FIXTURE_DIR = pathlib.Path(__file__).resolve().parent / "fixtures" / "connectivity"

# (fixture, expected verdict, description, fail-closed reason, required counts)
BATTERY = [
    ("joined-net", "GREEN", "one label binding two real pins", None,
     {"net_labels_meeting_fewer_than_two_pins": 0}),
    ("t-junction", "GREEN", "T-junction stub, three pins bound", None, None),
    ("disjoint-same-name", "GREEN",
     "POSITIVE CONTROL: two geometrically disjoint stubs sharing a name, each on a real pin — "
     "fragmentation must NOT be flagged", None,
     {"net_labels_meeting_fewer_than_two_pins": 0, "wires_not_meeting_any_pin": 0}),
    ("one-pin-net", "RED", "a label binding only ONE pin (K1E-016)", None,
     {"net_labels_meeting_fewer_than_two_pins": 1}),
    ("stub-to-nowhere", "RED", "a labelled stub landing on no pin at all", None,
     {"wires_not_meeting_any_pin": 1}),
    ("pin-on-two-nets", "RED", "one pin claimed by two names (K1E-018)", None,
     {"pins_met_by_multiple_net_labels": 1}),
    ("unmeasured-part", "GREEN",
     "ABSTENTION CONTROL: a pin-less stub beside a component with NO pin geometry must be "
     "abstained on, never called a defect", None,
     {"wires_not_meeting_any_pin": 0, "net_labels_meeting_fewer_than_two_pins": 0}),
    # `pins_loaded` is load-bearing in both of these. Without it, reverting to
    # designator keying still produced GREEN: dropping a part also made every part
    # look UNMEASURED, so the ABSTENTION path absorbed the bug and the control
    # passed for the wrong reason. Asserting the pin COUNT makes the drop itself
    # the failure, independent of how the abstention logic then behaves.
    ("rotated-component", "GREEN",
     "TRANSFORM CONTROL: rotated parts (90 deg / 270 deg) whose read-back pins are ABSOLUTE — goes "
     "RED if component rotation is ever composed into the transform", None,
     {"pin_landing_rate_pct": 100, "wires_not_meeting_any_pin": 0, "pins_loaded": 2}),
    ("multi-part-designator", "GREEN",
     "KEYING CONTROL: two parts sharing one designator — goes RED if pin data is keyed by "
     "designator instead of primitive id, because one part is then dropped", None,
     {"pin_landing_rate_pct": 100, "wires_not_meeting_any_pin": 0,
      "net_labels_meeting_fewer_than_two_pins": 0, "pins_loaded": 2}),
    ("off-sheet-wire", "RED",
     "OFF-SHEET: a wire with a negative coordinate — the one class with no tolerance "
     "or registration caveat", None,
     {"off_sheet_wires": 1}),
    # ---- V3 grammar (EasyEDA Pro 3.2.149) ---------------------------------
    # Same sheet, other grammar. The V3 fixture is the byte-for-byte semantic
    # twin of `joined-net`: two parts, two labelled stubs meeting at (120,100),
    # written as typed header||payload records with y NEGATED and the wire
    # geometry moved out into LINE records. It must reach the SAME verdict, and
    # `run_self_test` additionally asserts the two reports are IDENTICAL — that
    # equality is what proves the analysis did not fork per host version.
    ("v3-joined-net", "GREEN",
     "V3 GRAMMAR CONTROL: the V2 `joined-net` sheet re-serialised as 3.2.149 typed records — "
     "goes RED if the y-negation or the LINE->WIRE fold is wrong", None,
     {"net_labels_meeting_fewer_than_two_pins": 0, "wires_not_meeting_any_pin": 0,
      "pin_landing_rate_pct": 100, "pins_loaded": 2}),
    ("v3-shape-drift", "FAIL-CLOSED",
     "RECORD-SHAPE DRIFT: V3 COMPONENT payload renamed x -> posX. A parser that shrugs "
     "reports a smaller sheet, not a broken one",
     "RECORD-SHAPE DRIFT", None),
    ("v3-truncated-record", "FAIL-CLOSED",
     "TRUNCATED V3 RECORD: last payload cut mid-object — must refuse the file, not skip "
     "the line and measure the remainder",
     "TRUNCATED RECORD", None),
    ("v3-no-wires", "FAIL-CLOSED",
     "V3 components present, zero WIRE records — the fail-closed path survives the new "
     "grammar", "zero WIRE records", None),
    ("empty-source", "FAIL-CLOSED", "zero parseable records", "zero source records", None),
    ("no-wires", "FAIL-CLOSED", "components present, zero WIRE records", "zero WIRE records", None),
    ("no-pin-data", "FAIL-CLOSED",
     "wires and nets present but NO pin geometry — the property is unmeasurable",
     "no pin geometry loaded", None),
]


def run_self_test(verbose: bool = True) -> int:
    if not FIXTURE_DIR.is_dir():
        print(f"SELF_TEST=FAIL-CLOSED fixture directory missing: {FIXTURE_DIR}", file=sys.stderr)
        return 2
    results = []
    for name, expected, description, want_reason, want_counts in BATTERY:
        case = FIXTURE_DIR / name
        source = case / "source.txt"
        pins = case / "pins.json"
        if not source.is_file():
            results.append([name, expected, "MISSING-FIXTURE", description, None, False])
            continue
        ok_reason = True
        try:
            report = analyse(source.read_text(), [pins] if pins.is_file() else [])
            observed, detail = report["verdict"], dict(report["violation_counts"])
            detail["nets_unknown"] = report["abstentions"]["nets_unknown_count"]
            counts = report["counts"]
            detail["pin_landing_rate_pct"] = round(
                100.0 * counts["pins_landing_on_wire_geometry"] / counts["pins_loaded"]
            ) if counts["pins_loaded"] else 0
            detail["pins_loaded"] = counts["pins_loaded"]
            if want_counts:
                wrong = {k: {"want": v, "got": detail.get(k)}
                         for k, v in want_counts.items() if detail.get(k) != v}
                if wrong:
                    ok_reason = False
                    detail["POSITIVE_CONTROL_FAILED"] = wrong
        except FailClosed as exc:
            observed, detail = "FAIL-CLOSED", str(exc)
            if want_reason is not None:
                ok_reason = want_reason in detail
        results.append([name, expected, observed, description, detail, ok_reason])

    failures = [r for r in results if r[1] != r[2] or not r[5]]
    if verbose:
        print("CONNECTIVITY_SELF_TEST  (property: label-to-pin binding)")
        print(f"  fixture dir = {FIXTURE_DIR}")
        for name, expected, observed, description, detail, ok_reason in results:
            mark = "ok " if (expected == observed and ok_reason) else "BAD"
            print(f"  [{mark}] {name:20} expected={expected:12} observed={observed:12} {description}")
            if isinstance(detail, dict):
                fired = {k: v for k, v in detail.items() if v and k != "POSITIVE_CONTROL_FAILED"}
                if fired:
                    print(f"          fired: {fired}")
                if "POSITIVE_CONTROL_FAILED" in detail:
                    print(f"          POSITIVE CONTROL FAILED: {detail['POSITIVE_CONTROL_FAILED']}")
                    print("          right verdict, wrong reason — the case proves nothing")
            else:
                print(f"          reason: {detail}")
                if not ok_reason:
                    print("          WRONG GUARD FIRED")
    # ---- tolerance guard cases (not fixture-shaped: the tolerance is the input) ----
    # Fixture pins sit at 10-unit pitch, mirroring the real sheet, and w1's endpoint
    # is 5 units off U1.VDD — the exact half-pitch case. tol=4 must leave it unbound
    # (RED); tol>=5 must be REFUSED, not silently resolved toward the nearer pin.
    guard = FIXTURE_DIR / "half-pitch-offset"
    guard_failures = 0
    if (guard / "source.txt").is_file():
        rows = []
        for tol, expected in ((0, "RED"), (4, "RED"), (5, "FAIL-CLOSED"), (10, "FAIL-CLOSED")):
            try:
                rep = analyse(
                    (guard / "source.txt").read_text(), [guard / "pins.json"], snap_tolerance=tol
                )
                observed, detail = rep["verdict"], ""
            except FailClosed as exc:
                observed, detail = "FAIL-CLOSED", str(exc)
            ok = observed == expected
            guard_failures += 0 if ok else 1
            rows.append((tol, expected, observed, ok, detail))
        if verbose:
            print("  TOLERANCE GUARD (fixture pin pitch 10, so half-pitch = 5):")
            for tol, expected, observed, ok, detail in rows:
                print(f"  [{'ok ' if ok else 'BAD'}] snap-tolerance={tol:<3} "
                      f"expected={expected:12} observed={observed}")
                if detail:
                    print(f"          refused: {detail.splitlines()[0][:104]}")
    else:
        guard_failures += 1
        if verbose:
            print("  [BAD] tolerance guard fixture missing")

    # ---- CROSS-GRAMMAR EQUALITY -------------------------------------------
    # The two fixtures are the SAME sheet in the two serialisations. Matching
    # verdicts is not enough — two different sheets can both be GREEN. The whole
    # report must be identical, or the analysis forked on the grammar somewhere.
    grammar_failures = 0
    pair = (FIXTURE_DIR / "joined-net", FIXTURE_DIR / "v3-joined-net")
    if all((p / "source.txt").is_file() for p in pair):
        try:
            reports = [
                analyse((p / "source.txt").read_text(), [p / "pins.json"]) for p in pair
            ]
            differing = sorted(
                key for key in set(reports[0]) | set(reports[1])
                if reports[0].get(key) != reports[1].get(key)
            )
            ok = not differing
            grammar_failures += 0 if ok else 1
            if verbose:
                print("  CROSS-GRAMMAR EQUALITY (joined-net V2 vs v3-joined-net V3, same sheet):")
                print(f"  [{'ok ' if ok else 'BAD'}] every report section identical"
                      + ("" if ok else f" — DIFFERING SECTIONS: {differing}"))
                if not ok:
                    for key in differing:
                        print(f"          {key}: V2={reports[0].get(key)!r}")
                        print(f"          {key}: V3={reports[1].get(key)!r}")
        except FailClosed as exc:
            grammar_failures += 1
            if verbose:
                print(f"  [BAD] cross-grammar equality could not run: {exc}")
    else:
        grammar_failures += 1
        if verbose:
            print("  [BAD] cross-grammar equality fixtures missing "
                  "(joined-net and/or v3-joined-net)")

    red_seen = sum(1 for r in results if r[2] == "RED")
    closed_seen = sum(1 for r in results if r[2] == "FAIL-CLOSED")
    if verbose:
        print(f"  cases={len(results)} red_observed={red_seen} fail_closed_observed={closed_seen}")
    if not results:
        print("SELF_TEST=FAIL-CLOSED zero battery cases ran", file=sys.stderr)
        return 2
    if red_seen == 0 or closed_seen == 0:
        print("SELF_TEST=FAIL-CLOSED battery produced no RED or no FAIL-CLOSED case", file=sys.stderr)
        return 2
    if failures or guard_failures or grammar_failures:
        print(f"SELF_TEST=FAIL {len(failures) + guard_failures + grammar_failures} case(s) did "
              f"not match expectation", file=sys.stderr)
        return 1
    print("SELF_TEST=OK every battery case matched, including the RED, abstention, "
          "tolerance-guard, V3-grammar and cross-grammar-equality controls")
    return 0


# --------------------------------------------------------------------------
# cli
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", type=pathlib.Path)
    ap.add_argument("--pins", type=pathlib.Path, nargs="*", default=[])
    ap.add_argument("--json-out", type=pathlib.Path)
    ap.add_argument("--max-list", type=int, default=15)
    ap.add_argument("--snap-tolerance", type=int, default=DEFAULT_SNAP_TOLERANCE,
                    help="max Chebyshev distance for a wire endpoint to bind a pin "
                         "(default 0; >= half pin pitch is refused as ambiguous)")
    ap.add_argument("--allow-ambiguous-tolerance", action="store_true",
                    help="override the half-pitch refusal — records wrong-pin bindings as violations")
    ap.add_argument("--drc-report", type=pathlib.Path,
                    help="parse_drc_log.py JSON, used as an independent second oracle")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.source or not args.source.is_file():
        print(f"CONNECTIVITY=FAIL-CLOSED source not found: {args.source}", file=sys.stderr)
        return 2

    try:
        report = analyse(
            args.source.read_text(), list(args.pins),
            snap_tolerance=args.snap_tolerance,
            allow_ambiguous_tolerance=args.allow_ambiguous_tolerance,
            drc_report=args.drc_report,
        )
    except FailClosed as exc:
        print(f"CONNECTIVITY=FAIL-CLOSED {exc}", file=sys.stderr)
        return 2

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    # The abstention count rides on the headline. A GREEN that quietly skipped a
    # component is the false green this oracle exists to prevent.
    unknown = report["abstentions"]["nets_unknown_count"]
    suffix = (
        f"  (ABSTAINED on {unknown} net(s) and "
        f"{len(report['abstentions']['wires_abstained'])} wire(s) — NOT judged)"
        if unknown or report["abstentions"]["wires_abstained"] else ""
    )
    print(f"CONNECTIVITY={report['verdict']}{suffix}")
    print(f"measured property: {report['measured_property']}")
    print("counts")
    for key, value in report["counts"].items():
        print(f"  {key:36} = {value}")
    cov = report["pin_coverage"]
    print("pin geometry coverage")
    print(f"  {'designators':36} = {cov['designator_coverage']}")
    print(f"  {'component parts':36} = {cov['part_coverage']}")
    print(f"  {'pin landing rate':36} = {report['counts']['pin_landing_rate']} "
          f"({report['counts']['pins_landing_on_wire_geometry']}"
          f"/{report['counts']['pins_loaded']} pins sit on a wire endpoint)")
    print(f"  {'pins on no wire at all':36} = {report['counts']['pins_not_landing_on_wire_geometry']}"
          "  <- either genuinely unconnected, or a transform gap; reconcile before trusting")
    print("     transform applied: (x, y) -> (x, -y). Rotation is NOT composed — it is already")
    print("     baked into the read-back. A wrong transform lands ~0%, not a partial rate.")
    if cov["designator_collisions_avoided"]:
        for tag, pids in cov["designator_collisions_avoided"].items():
            print(f"  multi-part designator kept whole: {tag} -> parts {pids} "
                  "(keyed by primitive id, so no part was dropped)")
    for part in cov["parts_without_pin_data"]:
        print(f"    NO PIN GEOMETRY: {part['designator']} part {part['primitive_id']} "
              f"@({part['x']},{part['y']}) — nets touching it are ABSTAINED, not judged")
    print("violations (label-to-pin binding)")
    for key, value in report["violation_counts"].items():
        print(f"  {key:36} = {value}")
    print("abstentions")
    print(f"  {'nets_unknown':36} = {report['abstentions']['nets_unknown_count']}")
    print(f"  {'wires_abstained':36} = {len(report['abstentions']['wires_abstained'])}")

    below = report["violations"]["net_labels_meeting_fewer_than_two_pins"]
    if below:
        print(f"nets binding fewer than two pins ({len(below)}):")
        for name in below[: args.max_list]:
            print(f"  {name:22} pins={report['nets'][name]['pins_reached']}")
    floating = report["violations"]["wires_not_meeting_any_pin"]
    if floating:
        print(f"labelled stubs landing on no pin ({len(floating)}):")
        for entry in floating[: args.max_list]:
            print(f"  {entry['wire_id']:10} {entry['net']:20} nearest={entry['nearest_measured']} "
                  f"dist={entry['nearest_measured_distance']} segs={entry['segments']}")
        if len(floating) > args.max_list:
            print(f"  ... and {len(floating) - args.max_list} more")
    multi = report["violations"]["pins_met_by_multiple_net_labels"]
    if multi:
        print(f"pins claimed by two names ({len(multi)}): {list(multi.items())[: args.max_list]}")
    snap = report["snap_tolerance"]
    print("snap tolerance")
    print(f"  {'applied':36} = {snap['applied']}  (measured pin pitch {snap['measured_pin_pitch']}, "
          f"ambiguous at >= {snap['ambiguous_at_or_above']:g})")
    print(f"  {'bindings at nonzero distance':36} = {snap['bindings_at_nonzero_distance']}"
          f"  of which WRONG-pin: {snap['wrong_pin_bindings']}")
    print("  sensitivity — how the findings move with tolerance:")
    print(f"    {'tol':>4} {'<2 pins':>8} {'no-pin wires':>13} {'inexact':>8} {'WRONG pin':>10}")
    for row in snap["sensitivity"]:
        flag = "  <- AMBIGUOUS, refused by default" if row["ambiguous"] else ""
        print(f"    {row['tolerance']:>4} {row['nets_below_two_pins']:>8} "
              f"{row['wires_not_meeting_any_pin']:>13} {row['bindings_at_nonzero_distance']:>8} "
              f"{row['wrong_pin_bindings']:>10}{flag}")
    off = report["violations"]["off_sheet_wires"]
    if off:
        print(f"OFF-SHEET WIRES ({len(off)}) — negative coordinate, no fit recovers these:")
        for e in off:
            print(f"  {e['wire_id']:10} {e['net']:20} {e['segments']}")
    disp = report["diagnostics"]["components_offset_from_their_anchor"]
    if disp:
        print(f"components whose pin cloud is offset from their anchor ({len(disp)}) — DIAGNOSTIC, "
              "not a violation: symbol asymmetry and real displacement are not separable here")
        for e in disp[: args.max_list]:
            print(f"  {e['designator']:12} anchor={e['source_anchor']} pin-bbox-centre="
                  f"{e['pin_bbox_centre']} offset={e['offset']} pins={e['pins']}")
    wrong = report["violations"]["wrong_pin_bindings"]
    if wrong:
        print(f"  WRONG-PIN BINDINGS created by this tolerance ({len(wrong)}):")
        for b in wrong[: args.max_list]:
            print(f"    {b['net']:20} -> {b['pin']} (pin name {b['pin_name']}) at distance {b['distance']}")

    diff = report.get("drc_differential")
    if diff:
        print("differential oracle — geometry vs EasyEDA DRC")
        for key in ("agreed_floating", "geometry_only", "drc_only"):
            print(f"  {key:36} = {diff['counts'][key]:4}  {diff['interpretation'][key]}")
        for key in ("geometry_only", "drc_only"):
            items = diff[key]
            if items:
                print(f"    {key}: {items[: args.max_list]}"
                      + (f" ... +{len(items) - args.max_list}" if len(items) > args.max_list else ""))

    stats = report["statistics"]
    print("statistics (context, NOT violations)")
    print(f"  nets spanning >1 geometric island = {stats['nets_spanning_multiple_islands']} "
          f"of {report['counts']['named_nets']}")
    print(f"  {stats['note']}")
    for line in report["limitations"]:
        print(f"  LIMITATION: {line}")
    if args.json_out:
        print(f"report written to {args.json_out}")
    return 1 if report["verdict"] == "RED" else 0


if __name__ == "__main__":
    sys.exit(main())
